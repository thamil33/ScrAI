# engine/actors/basic_runtime.py
"""
Core runtime classes for actors, including those with cognitive cores powered by LLMs.
This module provides the foundational ScrAIActor class and its Agno-integrated counterpart.
"""

# Configure logging at the very top before any other imports
import logging
import sys
import dotenv
dotenv.load_dotenv()  # Load environment variables from .env file if present

# Force DEBUG level and ensure output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Force output to stdout
    ]
)
logger = logging.getLogger(__name__)
# Also log to root logger to ensure messages are shown
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

import os
import asyncio
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

# Attempt to import Agno and its components
print("Attempting to import Agno components...")
AGNO_AVAILABLE = False
try:
    from agno.agent import Agent as AgnoAgent
    from agno.models.openai import OpenAILike as AgnoOpenAIModel
    from agno.models.openrouter import OpenRouter as AgnoOpenRouterModel
    from agno.models.lmstudio import LMStudio as AgnoLMStudioModel
    from agno.models.message import Message
    from agno.tools.function import Function
    AGNO_AVAILABLE = True
    print("Successfully imported Agno components.")
    logger.info("Successfully imported Agno components.")
except ImportError as e:
    print(f"Agno import error: {e}")
    logger.warning(
        f"Agno library not found or core components missing: {e}. "
        "ScrAIActorAgno and related functionalities will not be available. "
        "This code will not run without Agno."
    )
except Exception as e:
    print(f"Unexpected Agno import error: {e}")
    logger.error(f"An unexpected error occurred during Agno import: {e}")


# Configure basic logging - increase level to DEBUG for more visibility
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

class ActorConfig(BaseModel):
    """Pydantic model for actor configuration."""
    actor_id: str = Field(..., description="Unique identifier for the actor.")
    name: str = Field(..., description="Name of the actor.")
    description: Optional[str] = Field(None, description="A brief description of the actor's role or purpose.")
    cognitive_core_type: str = Field("basic", description="Type of cognitive core (e.g., 'basic', 'agno_openai').")
    llm_model_id: Optional[str] = Field(None, description="Identifier for the LLM model, if applicable.")
    # Add other relevant configuration fields as needed

class ScrAIActor:
    """
    A base class for actors in the ScrAI simulation environment.
    Actors can perceive their environment, make decisions, and perform actions.
    """
    def __init__(self, actor_id: str, name: str, description: Optional[str] = None, **kwargs):
        """
        Initializes a ScrAIActor.

        Args:
            actor_id (str): Unique identifier for the actor.
            name (str): Name of the actor.
            description (Optional[str]): A brief description of the actor.
            **kwargs: Additional keyword arguments for extended functionality.
        """
        self.actor_id = actor_id
        self.name = name
        self.description = description
        self.state: Dict[str, Any] = {}  # To store actor-specific state information
        self.message_history: List[Dict[str, Any]] = [] # Stores a history of messages for context
        logger.info(f"Actor {self.name} (ID: {self.actor_id}) initialized.")

    def perceive(self, observation: Dict[str, Any]):
        """
        Allows the actor to perceive its environment.

        Args:
            observation (Dict[str, Any]): Data representing the actor's current perception.
        """
        logger.info(f"Actor {self.name} perceived: {observation}")
        # Basic actors might just store the latest observation
        self.state['last_observation'] = observation

    async def decide(self) -> Any:
        """
        The actor makes a decision based on its current state and perceptions.
        This method should be overridden by subclasses to implement specific decision-making logic.

        Returns:
            Any: The decision made by the actor (e.g., an action to perform).
        """
        logger.info(f"Actor {self.name} is making a decision.")
        # Basic decision logic (e.g., do nothing or a predefined action)
        return {"action": "idle", "reason": "Basic actor default decision"}

    async def act(self, action: Any):
        """
        The actor performs an action in the environment.
        This method might be overridden or extended by subclasses.

        Args:
            action (Any): The action to be performed.
        """
        logger.info(f"Actor {self.name} is performing action: {action}")
        # In a real simulation, this would interact with an environment controller.
        # For now, we'll just log it.
        return {"status": "success", "action_performed": action}

    async def run_cycle(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs a single perception-decision-action cycle for the actor.

        Args:
            observation (Dict[str, Any]): The current observation from the environment.

        Returns:
            Dict[str, Any]: The result of the action taken.
        """
        self.perceive(observation)
        decision = await self.decide()
        action_result = await self.act(decision)
        return action_result

# --- Agno Integrated Actor ---
if AGNO_AVAILABLE:
    class ScrAIActorAgno(ScrAIActor, AgnoAgent): # Inherits from ScrAIActor and AgnoAgent
        """
        An actor that uses an Agno Agent as its cognitive core for decision-making.
        This allows leveraging various LLMs and tools through the Agno framework.
        """
        def __init__(self,
                     actor_id: str,
                     name: str,
                     description: Optional[str] = None,
                     llm_model_id: str = "meta-llama/llama-4-maverick:free", # Default model
                     llm_provider: str = "openrouter", # or "lmstudio"
                     system_prompt: Optional[str] = "You are a helpful AI assistant.",
                     tools: Optional[List[Union[callable, Function]]] = None,
                     api_key: Optional[str] = None,
                     base_url: Optional[str] = None,
                     **kwargs):
            """
            Initializes an Agno-powered ScrAIActor.

            Args:
                actor_id (str): Unique identifier for the actor.
                name (str): Name of the actor.
                description (Optional[str]): A brief description of the actor.
                llm_model_id (str): The specific LLM model to use (e.g., "gpt-4", "meta-llama/llama-3-8b-instruct").
                llm_provider (str): The provider for the LLM ( "openrouter", "lmstudio").
                system_prompt (Optional[str]): The system prompt to guide the LLM's behavior.
                tools (Optional[List[Union[callable, Function]]]): Tools available to the Agno agent.
                api_key (Optional[str]): API key for the LLM provider.
                base_url (Optional[str]): Base URL for custom LLM providers (e.g., LMStudio).
                **kwargs: Additional arguments for AgnoAgent or ScrAIActor.
            """
            # Initialize ScrAIActor part
            # The error occurs here: super().__init__(...)
            # If ScrAIActor is the first in MRO that's not object, this calls ScrAIActor.__init__
            # If AgnoAgent is also a parent, its __init__ also needs to be called correctly.
            super().__init__(actor_id=actor_id, name=name, description=description, **kwargs) # Call ScrAIActor's init


            # Initialize AgnoAgent part
            if llm_provider == "openrouter":
                model_instance = AgnoOpenRouterModel(id=llm_model_id, api_key=api_key or os.getenv("OPENROUTER_API_KEY")) # Changed 'model' to 'id'
            elif llm_provider == "lmstudio":
                model_instance = AgnoLMStudioModel(model=llm_model_id, base_url=base_url or "http://localhost:1234/v1")
            else:
                raise ValueError(f"Unsupported LLM provider: {llm_provider}")
            
            # Create Agno agent with system_message instead of adding it separately later
            # This avoids duplicating the system message
            self.agno_agent = AgnoAgent(model=model_instance, system_message=system_prompt, tools=tools or [])
            self.message_history: List[Message] = [] # Override with Agno's Message type
            
            # Don't add system message to our history as Agno will handle it internally
            # if system_prompt:
            #     self.message_history.append(Message(role="system", content=system_prompt))

            logger.info(f"Agno Actor {self.name} (ID: {self.actor_id}) initialized with {llm_provider} model: {llm_model_id}.")

        def add_message(self, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None, tool_call_id: Optional[str] = None):
            """Adds a message to the Agno agent's history."""
            if role == "system":
                msg = Message(role="system", content=content)
            elif role == "user":
                msg = Message(role="user", content=content)
            elif role == "assistant":
                msg = Message(role="assistant", content=content, tool_calls=tool_calls)
            elif role == "tool":
                if tool_call_id is None:
                    raise ValueError("tool_call_id is required for tool messages.")
                msg = Message(role="tool", content=content, tool_call_id=tool_call_id)
            else:
                raise ValueError(f"Unknown message role: {role}")
            self.message_history.append(msg)

        async def decide(self) -> Any:
            """
            Uses the Agno agent to make a decision based on the current message history.
            """
            logger.info(f"Agno Actor {self.name} is making a decision using LLM.")
            logger.debug(f"Current message history: {self.message_history}")

            # The Agno agent's run method is synchronous and returns a RunResponse object
            try:
                # Try passing messages first
                logger.debug("Attempting to run Agno agent with message history")
                response = self.agno_agent.run(messages=self.message_history)
                logger.debug(f"Raw response object: {response}")
                logger.debug(f"Response type: {type(response)}")
                logger.debug(f"Response attributes: {dir(response)}")
            except TypeError as e:
                logger.debug(f"TypeError when passing messages: {e}")
                # If run() doesn't accept messages parameter, try without it
                logger.debug("Attempting to run Agno agent without message parameter")
                response = self.agno_agent.run()
                logger.debug(f"Raw response object: {response}")
                logger.debug(f"Response type: {type(response)}")
                logger.debug(f"Response attributes: {dir(response)}")
            except Exception as e:
                logger.error(f"Unexpected error running Agno agent: {e}")
                return {"action_type": "error", "content": f"Error running LLM: {str(e)}"}

            # Extract messages from the RunResponse object
            try:
                if hasattr(response, 'messages') and response.messages:
                    response_messages = response.messages
                    last_response = response_messages[-1] # Get the latest response from the agent
                    self.message_history.extend(response_messages) # Add new responses to our history

                    if hasattr(last_response, 'tool_calls') and last_response.tool_calls:
                        # If there are tool calls, the "decision" is to execute these tools.
                        logger.info(f"Agno Actor {self.name} decided to call tools: {last_response.tool_calls}")
                        return {"action_type": "tool_call", "tool_calls": last_response.tool_calls, "raw_response": last_response.content}
                    else:
                        # If no tool calls, the decision is the assistant's textual response.
                        logger.info(f"Agno Actor {self.name} decided with content: {last_response.content}")
                        return {"action_type": "message", "content": last_response.content}
                elif hasattr(response, 'content'):
                    # If the response has direct content, use that
                    logger.info(f"Agno Actor {self.name} decided with direct content: {response.content}")
                    return {"action_type": "message", "content": response.content}
                elif hasattr(response, 'message'):
                    # New case: if response has a single message attribute
                    logger.info(f"Agno Actor {self.name} decided with message: {response.message}")
                    return {"action_type": "message", "content": response.message.content if hasattr(response.message, 'content') else str(response.message)}
                elif hasattr(response, 'text') or hasattr(response, 'output'):
                    # Try other common output attributes
                    content = getattr(response, 'text', None) or getattr(response, 'output', str(response))
                    logger.info(f"Agno Actor {self.name} decided with alternative output: {content}")
                    return {"action_type": "message", "content": content}
                else:
                    # Try to get a useful string representation
                    logger.warning(f"Agno Actor {self.name} received unexpected response format: {response}")
                    logger.debug(f"Response dir: {dir(response)}")
                    return {"action_type": "error", "content": f"Unexpected response format: {type(response)}"}
            except Exception as e:
                logger.error(f"Error processing response: {e}", exc_info=True)
                return {"action_type": "error", "content": f"Error processing LLM response: {str(e)}"}

        # Override perceive to add user messages to the history for the LLM
        def perceive(self, observation: Dict[str, Any]):
            """
            Processes an observation and adds it as a user message to the Agno agent's history.
            """
            super().perceive(observation) # Call base class perceive if needed
            
            # Convert observation to a string format suitable for the LLM
            # This might need to be more sophisticated depending on the observation structure
            observation_content = f"Current observation: {observation}"
            
            # Add as a user message to the history
            self.add_message(role="user", content=observation_content)
            logger.info(f"Agno Actor {self.name} perceived and added to message history: {observation_content}")

        # act method might need to handle responses from tool calls if they happen here
        async def act(self, action: Any):
            """
            Performs an action. For Agno actors, this might involve interpreting the 'decision'
            which could be a message or a tool call.
            """
            logger.info(f"Agno Actor {self.name} is acting on decision: {action}")
            # If the action is a tool call, it would typically be handled by an external system
            # or by tools registered with the Agno agent.
            # If it's a message, it might be broadcast or logged.
            # For now, just log and return status.
            return {"status": "success", "action_performed": action, "actor_reply": action.get("content") if action.get("action_type") == "message" else None}

else:
    # Define a placeholder if Agno is not available to avoid runtime errors on class reference

        def __init__(self, *args, **kwargs):
            logger.error("Agno library is not available. ScrAIActorAgno cannot be initialized.")
            raise ImportError("Agno library is not available. Please install it to use ScrAIActorAgno.")

# --- Main execution block for testing ---
if __name__ == "__main__":
    print("Starting ScrAI basic_runtime.py script...")
    print("Logger level:", logger.level, "Root logger level:", root_logger.level)
    logger.info("Running basic_runtime.py directly for testing.")

    # Check logging is working with direct prints too
    print("Checking logging levels...")
    logger.debug("DEBUG level message")
    logger.info("INFO level message")
    logger.warning("WARNING level message")
    print("Finished checking logging levels")

    if AGNO_AVAILABLE:
        print("AGNO is available, proceeding with Agno tests")
        logger.info("AGNO is available, proceeding with Agno tests")
        try:
            # Test AgnoOpenRouterModel
            print("Setting up test model ID...")
            openrouter_model_id = "meta-llama/llama-4-maverick:free" # Example free model
            # openrouter_model_id = "anthropic/claude-3-haiku" # Example, ensure API key has access
            print(f"Model ID: {openrouter_model_id}")
            logger.info(f"Attempting to initialize AgnoOpenRouterModel with id: {openrouter_model_id}")
            
            # Check environment variable for API key
            print("Checking for OPENROUTER_API_KEY...")
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                print("OPENROUTER_API_KEY is set")
            else:
                print("WARNING: OPENROUTER_API_KEY is not set!")

            print("Creating ScrAIActorAgno instance...")
            # Test ScrAIActorAgno
            pope_agno_actor = ScrAIActorAgno(
                actor_id="pope_agno_001",
                name="PopeAgno",
                description="An Agno-powered Pope providing divine guidance.",
                llm_provider="openrouter",
                llm_model_id=openrouter_model_id,
                system_prompt="You are the Pope, offering wisdom and guidance. Respond concisely and with authority."
            )
            print(f"Successfully initialized ScrAIActorAgno: {pope_agno_actor.name}")
            logger.info(f"Successfully initialized ScrAIActorAgno: {pope_agno_actor.name}")

            # Example cycle
            print("Setting up test cycle...")
            async def run_pope_test():
                print("Inside run_pope_test() function")
                observation = {"query": "What is the meaning of life according to the church?"}
                print(f"Observation: {observation}")
                print("Running run_cycle...")
                try:
                    action_result = await pope_agno_actor.run_cycle(observation)
                    print(f"Action result: {action_result}")
                    logger.info(f"PopeAgno action result: {action_result}")
                except Exception as e:
                    print(f"Error in run_cycle: {e}")
                    import traceback
                    traceback.print_exc()

            print("Running asyncio.run()...")
            asyncio.run(run_pope_test()) # Execute the async test function
            print("Completed asyncio.run()")

        except ImportError as e:
            print(f"ImportError during Agno direct test: {e}")
            logger.error(f"ImportError during Agno direct test: {e}")
        except ValueError as e:
            print(f"ValueError during Agno direct test: {e}")
            logger.error(f"ValueError during Agno direct test: {e}")
        except Exception as e:
            print(f"An error occurred during Agno direct test: {e}")
            logger.error(f"An error occurred during Agno direct test: {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging
    else:
        print("Agno is not available, skipping Agno-specific tests.")
        logger.warning("Agno is not available, skipping Agno-specific tests.")

    # Test basic ScrAIActor
    print("Testing basic ScrAIActor...")
    basic_actor = ScrAIActor(actor_id="basic_001", name="BasicActor", description="A simple actor.")
    print(f"Successfully initialized ScrAIActor: {basic_actor.name}")
    logger.info(f"Successfully initialized ScrAIActor: {basic_actor.name}")
    print("Script completed successfully")

