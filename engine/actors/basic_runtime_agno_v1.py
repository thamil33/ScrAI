# File: scrai/engine/actors/basic_runtime_agno_v1.py
# Description: Refactored RuntimeActor with Agno integration - Implements AgnoModelBase.

import uuid
import logging
import json 
import asyncio 
from typing import Dict, Any, Optional, List, Tuple, Callable, AsyncIterator, Iterator

# --- Imports from Agno ---
try:
    from agno.agent import Agent
    from agno.tools.decorator import tool as agno_tool
    from agno.models.base import Model as AgnoModelBase
    from agno.models.message import Message as AgnoMessage
    # Agno's FunctionCall is for defining the function schema for the LLM.
    # The actual tool_calls object in AgnoMessage is likely a list of dicts or specific Agno ToolCall objects.
    from agno.tools import FunctionCall as AgnoFunctionDefinitionSchema # Renaming for clarity
except ImportError as e:
    print(f"WARNING: Agno library not found or core components missing: {e}. This code will not run without Agno.")
    # Define dummy classes for static analysis if Agno is not available
    class Agent: pass
    class AgnoModelBase: 
        def __init__(self, id: str, name: Optional[str]=None, provider: Optional[str]=None, **kwargs):
            self.id = id
            self.name = name
            self.provider = provider
        # Add stubs for all abstract methods
        def invoke(self, messages: List[Any], **kwargs) -> Any: raise NotImplementedError
        async def ainvoke(self, messages: List[Any], **kwargs) -> Any: raise NotImplementedError
        def invoke_stream(self, messages: List[Any], **kwargs) -> Iterator[Any]: raise NotImplementedError
        async def ainvoke_stream(self, messages: List[Any], **kwargs) -> AsyncIterator[Any]: raise NotImplementedError
        def parse_provider_response(self, response: Any, run_id: Optional[str] = None, response_format: Optional[Any] = None) -> Any: raise NotImplementedError # Added response_format
        def parse_provider_response_delta(self, delta: Any, run_id: Optional[str] = None, response_format: Optional[Any] = None) -> Any: raise NotImplementedError # Added response_format

    class AgnoMessage:
        def __init__(self, role: str, content: Any, tool_calls: Optional[List[Dict]] = None, name: Optional[str] = None, id: Optional[str] = None):
            self.role = role
            self.content = content
            self.tool_calls = tool_calls
            self.name = name
            self.id = id
    class AgnoFunctionDefinitionSchema: # Dummy for the schema definition aspect
        def __init__(self, name: str, arguments: str): # This was AgnoFunctionCall
            self.name = name
            self.arguments = arguments
    def agno_tool(func): return func


# --- Imports from ScrAI ---
from configurations.schemas.actor_schema import Actor as ActorData, CognitiveCore as CognitiveCoreData, Goal
from engine.llm_services.llm_provider import LLmClientInterface
from engine.systems.action_system import ActionManager, ActionOutcome, ActionResult

# --- Logger ---
logger = logging.getLogger(__name__)
# Ensure logger is configured (e.g., in your main script or here for standalone testing)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Agno Model Wrapper for ScrAI's LLM Interface ---
class ScrAILLMModelWrapper(AgnoModelBase):
    """
    Wraps ScrAI's LLmClientInterface to be compatible with Agno's model system.
    """
    def __init__(self, llm_provider: LLmClientInterface, actor_data_provider: Callable[[], ActorData]):
        model_id = llm_provider.OPENROUTER_MODEL if hasattr(llm_provider, 'OPENROUTER_MODEL') else "scrai_custom_llm"
        super().__init__(id=model_id, name=model_id, provider="ScrAI_Custom")
        self.llm_provider = llm_provider
        self.actor_data_provider = actor_data_provider
        logger.info(f"ScrAILLMModelWrapper initialized with provider: {llm_provider.__class__.__name__} for model_id: {model_id}")

    def _generate_prompt_for_llm(self, messages: List[AgnoMessage]) -> str:
        actor_data = self.actor_data_provider()
        goals_str = "; ".join([goal.description for goal in actor_data.cognitive_core.current_goals])
        
        recent_messages_str_list = []
        for m in messages[-5:]: 
            content_str = ""
            if isinstance(m.content, str):
                content_str = m.content
            elif isinstance(m.content, list): 
                for part in m.content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        content_str += part.get("text", "") + " "
            
            if hasattr(m, 'tool_calls') and m.tool_calls: 
                for tc in m.tool_calls: 
                    func_details = tc.get("function", {})
                    recent_messages_str_list.append(f"{m.role} called tool {func_details.get('name','unknown')} with args {func_details.get('arguments','{}')}")
            elif m.role == "tool" and content_str: 
                 recent_messages_str_list.append(f"tool {m.name} responded: {content_str.strip()}")
            elif content_str:
                 recent_messages_str_list.append(f"{m.role}: {content_str.strip()}")


        memory_str = "; ".join(filter(None, recent_messages_str_list))
        
        emotions_str = ", ".join([f"{k}: {v}" for k,v in actor_data.cognitive_core.emotions.items()])

        prompt = (
            f"You are {actor_data.name}. Your description: {actor_data.description}.\n"
            f"Your current role/state: {actor_data.state.get('actor_state', actor_data.state.get('status', 'neutral'))}.\n"
            f"Your current goals are: [{goals_str}].\n"
            f"Your recent conversation history (treat as short-term memory): [{memory_str}].\n"
            f"Your current emotions are: [{emotions_str}].\n\n"
            f"Based on this and the latest user message, what is your immediate, single next action? "
            f"The system will provide you with a list of available tools (actions). "
            f"If you decide to use a tool, respond ONLY with a JSON object in the format: "
            f'{{"action_name": "your_chosen_action_tool_name", "parameters": {{"param1": "value1", ...}}}}.\n'
            f"If you decide to respond directly without using a tool, provide your textual response in a JSON object like: "
            f'{{"response_text": "Your natural language response here."}}.\n'
            f"Choose one tool or provide a direct response. Your JSON response:"
        )
        return prompt

    def parse_provider_response(self, llm_output_dict: Dict[str, Any], run_id: Optional[str] = None, response_format: Optional[Any] = None) -> AgnoMessage: # Added response_format
        """
        Parses the dictionary output from the LLM provider and converts it into an AgnoMessage.
        The 'response_format' argument is accepted to match Agno's signature, but not actively used here
        as our LLMClientInterface already produces structured JSON based on json_schema.
        """
        logger.debug(f"parse_provider_response called with llm_output_dict: {llm_output_dict}, response_format: {response_format}")
        if "action_name" in llm_output_dict:
            tool_name = llm_output_dict["action_name"]
            tool_arguments_dict = llm_output_dict.get("parameters", {})
            tool_arguments_json_str = json.dumps(tool_arguments_dict)
            
            tool_call_id = f"scrai_tool_call_{uuid.uuid4().hex[:8]}"
            tool_calls_payload = [
                {
                    "id": tool_call_id,
                    "type": "function", 
                    "function": { 
                        "name": tool_name,
                        "arguments": tool_arguments_json_str,
                    },
                }
            ]
            logger.info(f"LLM chose tool: {tool_name} with args: {tool_arguments_dict}. Payload for Agno: {tool_calls_payload}")
            return AgnoMessage(role="assistant", content=None, tool_calls=tool_calls_payload)
        elif "response_text" in llm_output_dict:
            logger.info(f"LLM provided direct response: {llm_output_dict['response_text']}")
            return AgnoMessage(role="assistant", content=llm_output_dict["response_text"])
        else:
            logger.warning(f"LLM output an unexpected format: {llm_output_dict}. Treating as text.")
            return AgnoMessage(role="assistant", content=str(llm_output_dict))

    # --- Implementation of AgnoModelBase abstract methods ---
    def invoke(self, messages: List[AgnoMessage], **kwargs) -> AgnoMessage:
        logger.debug(f"Invoke called with {len(messages)} messages. Kwargs: {kwargs}")
        prompt_str = self._generate_prompt_for_llm(messages)
        
        action_output_schema = {
            "type": "object",
            "properties": {
                "action_name": {"type": "string"},
                "parameters": {"type": "object"},
                "response_text": {"type": "string"} 
            },
        }
        
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 500)
        run_id = kwargs.get("run_id") 
        # Agno's Base Model's _process_model_response passes response_format to parse_provider_response
        response_format_from_agno = kwargs.get("response_format")


        try:
            llm_output_dict, metadata = self.llm_provider.complete_json(
                prompt=prompt_str,
                json_schema=action_output_schema, # This is for our LLM's output
                temperature=temperature,
                max_tokens=max_tokens
            )
            logger.debug(f"LLM provider returned: {llm_output_dict}, metadata: {metadata}")
            # Pass response_format_from_agno if it's needed by the parsing logic, though current logic doesn't use it.
            return self.parse_provider_response(llm_output_dict, run_id=run_id, response_format=response_format_from_agno)
        except Exception as e:
            logger.error(f"Error in ScrAILLMModelWrapper.invoke: {e}", exc_info=True)
            return AgnoMessage(role="assistant", content=json.dumps({"error": f"LLM invocation failed: {str(e)}"}))

    async def ainvoke(self, messages: List[AgnoMessage], **kwargs) -> AgnoMessage:
        logger.debug(f"Ainvoke called with {len(messages)} messages. Kwargs: {kwargs}")
        loop = asyncio.get_event_loop()
        try:
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in ["temperature", "max_tokens", "run_id", "response_format"]}
            return await loop.run_in_executor(None, self.invoke, messages, **filtered_kwargs)
        except Exception as e:
            logger.error(f"Error in ScrAILLMModelWrapper.ainvoke: {e}", exc_info=True)
            return AgnoMessage(role="assistant", content=json.dumps({"error": f"Async LLM invocation failed: {str(e)}"}))

    def invoke_stream(self, messages: List[AgnoMessage], **kwargs) -> Iterator[AgnoMessage]:
        logger.info("invoke_stream called. Underlying provider does not support streaming. Falling back to non-streaming.")
        yield self.invoke(messages, **kwargs)

    async def ainvoke_stream(self, messages: List[AgnoMessage], **kwargs) -> AsyncIterator[AgnoMessage]:
        logger.info("ainvoke_stream called. Underlying provider does not support streaming. Falling back to non-streaming.")
        yield await self.ainvoke(messages, **kwargs) 
        
    def parse_provider_response_delta(self, delta: Any, run_id: Optional[str] = None, response_format: Optional[Any] = None) -> AgnoMessage: # Added response_format
        logger.warning("parse_provider_response_delta called but streaming not implemented.")
        if isinstance(delta, AgnoMessage): 
            return delta
        return AgnoMessage(role="assistant", content=str(delta) if delta else "")


# --- Tool Functions for Agno ---
def _create_agno_tool(action_name: str, action_manager: ActionManager, actor_pydantic_data_ref: ActorData) -> Callable:
    @agno_tool 
    def agno_action_tool(parameters: Optional[Dict[str, Any]] = None) -> str: 
        action_dict = {
            "action_name": action_name,
            "parameters": parameters or {}
        }
        logger.info(f"Agno tool '{action_name}' called with params: {parameters} for actor '{actor_pydantic_data_ref.name}'")
        
        outcome: ActionOutcome = action_manager.execute_action(action_dict, actor_pydantic_data_ref)
        
        if outcome.state_changes:
            logger.info(f"Applying state changes for action '{action_name}' to '{actor_pydantic_data_ref.name}': {outcome.state_changes}")
            for key, value in outcome.state_changes.items():
                if key == "emotion_changes":
                    if hasattr(actor_pydantic_data_ref.cognitive_core, 'emotions'):
                         for emotion, new_value in value.items():
                            actor_pydantic_data_ref.cognitive_core.emotions[emotion] = new_value
                else: 
                    actor_pydantic_data_ref.state[key] = value
        
        logger.info(f"Outcome for '{action_name}' for actor '{actor_pydantic_data_ref.name}': {outcome.message}")
        return outcome.message 

    agno_action_tool.__name__ = action_name
    action_handler = action_manager._action_handlers.get(action_name)
    param_details_str = "Accepts a dictionary of parameters." 
    if action_handler:
        try:
            param_hints = getattr(action_handler, '__annotations__', {}).get('params', 'Dict[str, Any]')
            param_details_str = f"Parameters expected: {param_hints}."
        except Exception:
            pass 

    agno_action_tool.__doc__ = (f"Performs the ScrAI action: '{action_name}'. "
                                f"{param_details_str} "
                                f"This action will affect the state of actor {actor_pydantic_data_ref.name}.")
    return agno_action_tool


# --- Main Actor Class (Agno Agent) ---
class ScrAIActor(Agent):
    def __init__(self, actor_pydantic_data: ActorData, llm_provider_instance: LLmClientInterface, action_manager_instance: ActionManager):
        self.pydantic_data = actor_pydantic_data 
        self.llm_provider = llm_provider_instance
        self.action_manager = action_manager_instance
        
        scrai_llm_model = ScrAILLMModelWrapper(self.llm_provider, lambda: self.pydantic_data)

        prepared_tools = []
        for action_name in self.action_manager.get_available_actions():
            tool_func = _create_agno_tool(action_name, self.action_manager, self.pydantic_data)
            prepared_tools.append(tool_func)
        
        super().__init__(
            name=self.pydantic_data.name,
            description=self.pydantic_data.description,
            model=scrai_llm_model,
            tools=prepared_tools,
            instructions=self._get_dynamic_instructions, 
            markdown=True, 
            debug_mode=True,
        )
        logger.info(f"ScrAIActor '{self.pydantic_data.name}' initialized as Agno Agent with {len(prepared_tools)} tools.")

    def _get_dynamic_instructions(self, agent: 'ScrAIActor') -> List[str]: 
        actor_data = agent.pydantic_data 
        goals_str = "; ".join([goal.description for goal in actor_data.cognitive_core.current_goals])
        emotions_str = ", ".join([f"{k}: {v}" for k,v in actor_data.cognitive_core.emotions.items()])

        instructions = [
            f"You are the character: {actor_data.name}. Your detailed description: {actor_data.description}.",
            f"Your current internal state is: {actor_data.state.get('actor_state', actor_data.state.get('status', 'neutral'))}.",
            f"Your active goals are: [{goals_str}].",
            f"Your current emotional disposition is: [{emotions_str}].",
            "Carefully consider the ongoing conversation and your situation. Then, select the most appropriate action (tool) from the list of available tools to perform next.",
            "If no tool is suitable for a direct reply to the user, you can also respond naturally in character."
        ]
        return instructions

    def run_cycle(self, perception_input: str, **kwargs) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        logger.info(f"\nActor '{self.pydantic_data.name}' (Agno) perceives: '{perception_input}'")
        
        response_from_agno = super().run(message=perception_input, **kwargs) 
        
        chosen_action_details = None
        assistant_message = None

        if response_from_agno:
            if hasattr(response_from_agno, 'tool_calls') and response_from_agno.tool_calls: 
                tool_call_data = response_from_agno.tool_calls[0] 
                
                function_details = tool_call_data.get("function", {})
                tool_name = function_details.get("name")
                tool_args_str = function_details.get("arguments", "{}")
                
                tool_output_message = response_from_agno.content 

                chosen_action_details = {
                    "action_name": tool_name,
                    "parameters": json.loads(tool_args_str) if isinstance(tool_args_str, str) else {},
                    "tool_call_id": tool_call_data.get("id"),
                    "tool_output": tool_output_message
                }
                logger.info(f"Tool '{tool_name}' was executed by Agno. Output: {tool_output_message}")
                assistant_message = str(tool_output_message) 
            
            elif isinstance(response_from_agno.content, str) and response_from_agno.content:
                assistant_message = response_from_agno.content
                logger.info(f"Agno Agent direct textual response: {assistant_message}")
            elif response_from_agno.content is not None: 
                assistant_message = str(response_from_agno.content)
                logger.info(f"Agno Agent non-string/non-tool_call content: {assistant_message}")
        
        return chosen_action_details, assistant_message

    def get_current_status(self) -> Dict[str, Any]:
        return {
            "name": self.pydantic_data.name,
            "current_state": self.pydantic_data.state,
            "emotions": self.pydantic_data.cognitive_core.emotions,
            "goals": [g.description for g in self.pydantic_data.cognitive_core.current_goals],
            "available_actions_count": len(self.tools) if self.tools else 0
        }

# --- Example Usage (for testing this file directly) ---
if __name__ == "__main__":
    logger.info("Running basic_runtime_agno_v1.py directly for testing.")

    class MockLLmClientInterface(LLmClientInterface):
        def __init__(self, provider="mock", model="mock_model"):
            self.provider = provider
            self.OPENROUTER_MODEL = model 
            self.call_count = 0
            self.mock_llm_action_outputs = [
                {"action_name": "pray", "parameters": {"intensity": "high", "duration": "long"}},
                {"action_name": "record_vision", "parameters": {"detail": "divine light", "method": "mental_record"}},
                {"action_name": "speak", "parameters": {"message": "I must document this vision."}},
                {"response_text": "I ponder the meaning of these events deeply."}, 
            ]
            logger.info(f"MockLLmClientInterface initialized for {provider} with model {model}")

        def complete_json(self, prompt: str, json_schema: Optional[Dict[str, Any]] = None, **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            logger.info(f"MockLLmClientInterface.complete_json called. Prompt (start): {prompt[:250]}...")
            chosen_output_by_llm = self.mock_llm_action_outputs[self.call_count % len(self.mock_llm_action_outputs)]
            self.call_count += 1
            logger.info(f"MockLLmClientInterface 'generating' output: {chosen_output_by_llm}")
            return chosen_output_by_llm, {"model": "mock_model_direct_test", "usage": {}}

    try:
        mock_llm_provider = MockLLmClientInterface()
        action_manager = ActionManager() 

        pope_actor_data = ActorData(
            name="Pope Leo XIII (AgnoV1)",
            description="Experiencing a vision, integrated with Agno.",
            cognitive_core=CognitiveCoreData(
                current_goals=[Goal(description="Understand the vision via Agno framework.")],
                emotions={"awe": 0.96, "determination": 0.7},
            ),
            state={"spiritual_state": "in_agno_vision_v1", "actor_state": "contemplating"} 
        )

        pope_agno_actor = ScrAIActor(
            actor_pydantic_data=pope_actor_data,
            llm_provider_instance=mock_llm_provider,
            action_manager_instance=action_manager
        )

        logger.info(f"\n=== Initial Status of {pope_agno_actor.name} ===")
        logger.info(pope_agno_actor.get_current_status())
        
        perception1 = "A profound silence fills the chapel, then a whisper: 'The Church will face trials.'"
        logger.info(f"\n=== Cycle 1: Perception: '{perception1}' ===")
        action_taken1, response_text1 = pope_agno_actor.run_cycle(perception1)
        
        logger.info(f"Action Taken in Cycle 1: {action_taken1}")
        logger.info(f"Response Text in Cycle 1: {response_text1}") 
        logger.info(f"Pydantic State after Cycle 1: {pope_agno_actor.pydantic_data.state}")
        logger.info(f"Pydantic Emotions after Cycle 1: {pope_agno_actor.pydantic_data.cognitive_core.emotions}")

        perception2 = "A vision of a future council appears, discussing matters of faith."
        logger.info(f"\n=== Cycle 2: Perception: '{perception2}' ===")
        action_taken2, response_text2 = pope_agno_actor.run_cycle(perception2)

        logger.info(f"Action Taken in Cycle 2: {action_taken2}")
        logger.info(f"Response Text in Cycle 2: {response_text2}")
        logger.info(f"Pydantic State after Cycle 2: {pope_agno_actor.pydantic_data.state}")
        
        perception3 = "What should be my next step regarding this vision?" 
        logger.info(f"\n=== Cycle 3: Perception: '{perception3}' ===")
        action_taken3, response_text3 = pope_agno_actor.run_cycle(perception3)
        logger.info(f"Action Taken in Cycle 3: {action_taken3}") 
        logger.info(f"Response Text in Cycle 3: {response_text3}") 
        logger.info(f"Pydantic State after Cycle 3: {pope_agno_actor.pydantic_data.state}")


        logger.info(f"\n=== Final Status of {pope_agno_actor.name} ===")
        logger.info(pope_agno_actor.get_current_status())

    except ImportError as e:
        logger.error(f"ImportError: {e}. Could not run Agno direct test. Ensure Agno is installed and schemas are importable.")
    except Exception as e:
        logger.error(f"An error occurred during Agno direct test: {e}", exc_info=True)