# File: scrai/engine/actors/basic_runtime_agno_v2.py
# Description: RuntimeActor using Agno's native model classes.

import uuid
import logging
import json
import os # For API keys
from typing import Dict, Any, Optional, List, Tuple, Callable

# --- Imports from Agno ---
try:
    from agno.agent import Agent
    from agno.tools.decorator import tool as agno_tool
    # Import Agno's specific model classes
    from agno.models.openrouter import OpenRouter as AgnoOpenRouterModel
    from agno.models.lmstudio import LMStudio as AgnoLMStudioModel
    # Message for type hinting if needed in instructions or context
    from agno.models.message import Message as AgnoMessage
    # For Agno's ToolCall and FunctionCall structures if needed for RunResponse parsing
    from agno.models.message import ToolCall as AgnoToolCallData # Assuming this might be the dict structure
    
except ImportError as e:
    print(f"WARNING: Agno library not found or core components missing: {e}. This code will not run without Agno.")
    # Define dummy classes for static analysis
    class Agent: pass
    class AgnoOpenRouterModel:
        def __init__(self, id: str, api_key: Optional[str] = None, **kwargs): pass
    class AgnoLMStudioModel:
        def __init__(self, id: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs): pass
    class AgnoMessage: pass
    class AgnoToolCallData: pass # Placeholder
    def agno_tool(func): return func

# --- Imports from ScrAI ---
from configurations.schemas.actor_schema import Actor as ActorData, CognitiveCore as CognitiveCoreData, Goal
# LLmClientInterface might not be directly used by ScrAIActor anymore, but ActionManager is.
from engine.llm_services.llm_provider import LLmClientInterface # Kept for type hint in main, but not used by actor
from engine.systems.action_system import ActionManager, ActionOutcome, ActionResult

# --- Logger ---
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Tool Functions for Agno (Unchanged from v1) ---
def _create_agno_tool(action_name: str, action_manager: ActionManager, actor_pydantic_data_ref: ActorData) -> Callable:
    @agno_tool 
    def agno_action_tool(parameters: Optional[Dict[str, Any]] = None) -> str: 
        action_dict = {"action_name": action_name, "parameters": parameters or {}}
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
    def __init__(self, actor_pydantic_data: ActorData, action_manager_instance: ActionManager):
        self.pydantic_data = actor_pydantic_data 
        self.action_manager = action_manager_instance
        
        # Select and instantiate the Agno model based on actor_pydantic_data
        llm_settings = self.pydantic_data.cognitive_core.llm_provider_settings
        provider_type = llm_settings.get("provider_type", "openrouter").lower() # Default to openrouter
        model_id = llm_settings.get("model")
        
        agno_llm_model_instance: Any # Should be AgnoModelBase compatible
        if provider_type == "openrouter":
            if not model_id:
                model_id = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-4-maverick:free")
                logger.warning(f"OpenRouter model_id not found in llm_settings, using default/env: {model_id}")
            api_key = llm_settings.get("api_key", os.getenv("OPENROUTER_API_KEY"))
            agno_llm_model_instance = AgnoOpenRouterModel(id=model_id, api_key=api_key)
            logger.info(f"Initialized AgnoOpenRouterModel with id: {model_id}")
        elif provider_type == "lmstudio":
            if not model_id:
                model_id = os.getenv("LOCAL_MODEL", "local-model") # LMStudio model IDs are often just names
                logger.warning(f"LMStudio model_id not found in llm_settings, using default/env: {model_id}")
            base_url = llm_settings.get("base_url", os.getenv("LOCAL_BASE_URL", "http://localhost:1234/v1"))
            api_key = llm_settings.get("api_key", os.getenv("LOCAL_API_KEY", "not-required")) # Usually not required for local
            agno_llm_model_instance = AgnoLMStudioModel(id=model_id, base_url=base_url, api_key=api_key)
            logger.info(f"Initialized AgnoLMStudioModel with id: {model_id}, base_url: {base_url}")
        else:
            raise ValueError(f"Unsupported provider_type in llm_provider_settings: {provider_type}")

        prepared_tools = []
        for action_name in self.action_manager.get_available_actions():
            tool_func = _create_agno_tool(action_name, self.action_manager, self.pydantic_data)
            prepared_tools.append(tool_func)
        
        super().__init__(
            name=self.pydantic_data.name,
            description=self.pydantic_data.description,
            model=agno_llm_model_instance, # Use Agno's native model
            tools=prepared_tools,
            instructions=self._get_dynamic_instructions, 
            markdown=True, 
            debug_mode=True, 
        )
        logger.info(f"ScrAIActor '{self.pydantic_data.name}' initialized as Agno Agent with {len(prepared_tools)} tools using Agno's {provider_type} model.")

    def _get_dynamic_instructions(self, agent: 'ScrAIActor') -> List[str]: 
        # In Agno, `agent` is `self` when instructions is a method.
        actor_data = self.pydantic_data # Access directly
        goals_str = "; ".join([goal.description for goal in actor_data.cognitive_core.current_goals])
        emotions_str = ", ".join([f"{k}: {v}" for k,v in actor_data.cognitive_core.emotions.items()])
        # Short-term memory (last few conversation turns) is automatically handled by Agno's agent.run()
        # and included in the prompt to the LLM. We don't need to manually add it to instructions.

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
        
        # Context for Agno tools to access actor_pydantic_data (though our tools use closure for now)
        # For Agno to pass this to tools, tools would need to accept `agent: Agent` and use `agent.context`.
        # Our current tool implementation `_create_agno_tool` closes over `actor_pydantic_data_ref`.
        # This means `context` here is more for `_get_dynamic_instructions` if it were not a method.
        # Since `_get_dynamic_instructions` is a method, it can access `self.pydantic_data`.
        # No explicit context passing needed for this setup if tools use closure.
        
        response_from_agno = super().run(message=perception_input, **kwargs) 
        
        chosen_action_details = None
        assistant_message = None

        if response_from_agno:
            # `response_from_agno.tool_calls` is a list of Agno's ToolCall objects (or dicts)
            # as per agno/models/message.py (Message.tool_calls) and confirmed by agno_docs.txt tool calling example.
            current_tool_calls = getattr(response_from_agno, 'tool_calls', None)
            if current_tool_calls: 
                tool_call_data = current_tool_calls[0] # Process first tool call for simplicity

                # Assuming tool_call_data is a dict-like object or an actual Agno ToolCall object
                tool_name = None
                tool_args_str = "{}"
                tool_call_id_val = None
                tool_output_val = getattr(tool_call_data, 'output', response_from_agno.content) # Tool output is often passed back in content or a specific field

                if isinstance(tool_call_data, dict):
                    function_details = tool_call_data.get("function", {})
                    tool_name = function_details.get("name")
                    tool_args_str = function_details.get("arguments", "{}")
                    tool_call_id_val = tool_call_data.get("id")
                elif hasattr(tool_call_data, 'function') and hasattr(tool_call_data, 'id'): # If it's an Agno ToolCall object
                    tool_name = tool_call_data.function.name
                    tool_args_str = tool_call_data.function.arguments
                    tool_call_id_val = tool_call_data.id
                
                if tool_name:
                    chosen_action_details = {
                        "action_name": tool_name,
                        "parameters": json.loads(tool_args_str) if tool_args_str and isinstance(tool_args_str, str) else {}, 
                        "tool_call_id": tool_call_id_val,
                        "tool_output": tool_output_val
                    }
                    logger.info(f"Tool '{tool_name}' was executed by Agno. Output: {tool_output_val}")
                    assistant_message = str(tool_output_val) # The tool's return message is the primary response here
            
            # Handle direct textual response if no tool was called or if content is primary
            if isinstance(response_from_agno.content, str) and response_from_agno.content:
                if assistant_message and assistant_message != response_from_agno.content: 
                    logger.info(f"Agno Agent additional textual response: {response_from_agno.content}")
                    assistant_message += "\n" + response_from_agno.content # Append if different
                elif not assistant_message:
                    assistant_message = response_from_agno.content
                    logger.info(f"Agno Agent direct textual response: {assistant_message}")
            elif response_from_agno.content is not None and not chosen_action_details: 
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
    logger.info("Running basic_runtime_agno_v2.py directly for testing.")
    
    # For this test to run, you'd need OPENROUTER_API_KEY in your .env or environment
    # or configure llm_provider_settings for LMStudio if you have it running.
    # We'll use a mock for the ActionManager part, but Agno will try to make a real LLM call.
    
    # For demonstration, let's set up llm_provider_settings for OpenRouter
    # Ensure your .env file has OPENROUTER_API_KEY and optionally OPENROUTER_MODEL
    # from dotenv import load_dotenv
    # load_dotenv()

    try:
        action_manager = ActionManager() 

        # Configure ActorData to use Agno's OpenRouter model
        pope_actor_data = ActorData(
            name="Pope Leo XIII (AgnoNative)",
            description="Experiencing a vision, using Agno's native OpenRouter model.",
            cognitive_core=CognitiveCoreData(
                current_goals=[Goal(description="Understand the vision via Agno framework and OpenRouter.")],
                emotions={"awe": 0.98, "anticipation": 0.7},
                llm_provider_settings={ # Settings for Agno's model
                    "provider_type": "openrouter", # Instructs ScrAIActor to use AgnoOpenRouterModel
                    "model": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct:free"), # Or any other model
                    # "api_key": os.getenv("OPENROUTER_API_KEY") # Agno's OpenRouterModel likely picks this from env
                }
            ),
            state={"spiritual_state": "in_agno_vision_v2", "actor_state": "expectant"} 
        )
        
        # We no longer pass llm_provider_instance directly to ScrAIActor.
        # ScrAIActor now instantiates the Agno model internally.
        pope_agno_actor = ScrAIActor(
            actor_pydantic_data=pope_actor_data,
            action_manager_instance=action_manager
        )

        logger.info(f"\n=== Initial Status of {pope_agno_actor.name} ===")
        logger.info(pope_agno_actor.get_current_status())
        
        # --- IMPORTANT NOTE FOR TESTING ---
        # This test will make a REAL LLM call to OpenRouter (or LMStudio if configured)
        # because ScrAIActor now uses Agno's native model classes.
        # Ensure your API keys and model names are correctly set in .env or llm_provider_settings.
        # The MockLLmClientInterface is no longer used by ScrAIActor.
        
        # If you don't want to make real LLM calls for this test,
        # you would need to mock Agno's OpenRouterModel/LMStudioModel,
        # or mock the `requests.post` call they make internally. This is more complex.

        logger.info("NOTE: The following test cycles will attempt REAL LLM calls based on actor_pydantic_data.cognitive_core.llm_provider_settings.")

        perception1 = "A profound silence fills the chapel, then a whisper: 'The Church will face trials.' What should I do first?"
        logger.info(f"\n=== Cycle 1: Perception: '{perception1}' ===")
        # To test actual LLM behavior, run this. Be mindful of API calls.
        action_taken1, response_text1 = pope_agno_actor.run_cycle(perception1)
        
        logger.info(f"Action Taken in Cycle 1: {action_taken1}")
        logger.info(f"Response Text in Cycle 1: {response_text1}") 
        logger.info(f"Pydantic State after Cycle 1: {pope_agno_actor.pydantic_data.state}")
        logger.info(f"Pydantic Emotions after Cycle 1: {pope_agno_actor.pydantic_data.cognitive_core.emotions}")

        # Example of a follow-up (will also make a real LLM call)
        # perception2 = "The whisper fades, leaving a sense of urgency. What is the nature of these trials?"
        # logger.info(f"\n=== Cycle 2: Perception: '{perception2}' ===")
        # action_taken2, response_text2 = pope_agno_actor.run_cycle(perception2)
        # logger.info(f"Action Taken in Cycle 2: {action_taken2}")
        # logger.info(f"Response Text in Cycle 2: {response_text2}")
        # logger.info(f"Pydantic State after Cycle 2: {pope_agno_actor.pydantic_data.state}")


        logger.info(f"\n=== Final Status of {pope_agno_actor.name} ===")
        logger.info(pope_agno_actor.get_current_status())

    except ImportError as e:
        logger.error(f"ImportError: {e}. Could not run Agno direct test. Ensure Agno is installed and schemas are importable.")
    except ValueError as e: # Catch our provider_type ValueError
        logger.error(f"Configuration ValueError: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"An error occurred during Agno direct test: {e}", exc_info=True)

