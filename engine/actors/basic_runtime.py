# File: scrai/engine/actors/basic_runtime.py

import uuid
import datetime # Not directly used here but good for context with other modules
from typing import Dict, Any, Optional, List, Tuple

# --- 1. Import REAL Pydantic Schemas ---
# These paths assume your project root is added to PYTHONPATH or you're running
# scripts from a context where these are discoverable.
# Adjust paths if your execution context is different.
from configurations.schemas.actor_schema import Actor as ActorData, CognitiveCore as CognitiveCoreData, Goal
# from configurations.schemas.event_schema import Event # Not directly used by these classes yet

# --- 2. Import REAL LLMInterface ---
from engine.llm_services.llm_interface import LLMInterface # Base class for type hinting
# Specific implementation (like OpenRouterLLM) will be passed in during instantiation.


class RuntimeCognitiveCore:
    """
    Manages the Actor's thinking process, including LLM interaction.
    """
    def __init__(self, actor_pydantic_data: ActorData, llm_interface: LLMInterface):
        """
        Initializes the RuntimeCognitiveCore.
        Args:
            actor_pydantic_data: The Pydantic model instance for the actor's data.
            llm_interface: An instance of a class that implements LLMInterface (e.g., OpenRouterLLM).
        """
        self.actor_data = actor_pydantic_data  # This is the Pydantic model instance
        self.llm_interface = llm_interface
        # The Pydantic model actor_data.cognitive_core holds the state like goals, emotions, memory

    def add_perception_to_memory(self, perception: str):
        """Adds a new perception to the short-term memory."""
        if not hasattr(self.actor_data.cognitive_core, 'short_term_memory') or \
           self.actor_data.cognitive_core.short_term_memory is None:
            self.actor_data.cognitive_core.short_term_memory = []
            
        self.actor_data.cognitive_core.short_term_memory.append(perception)
        # Optional: Trim memory if it gets too long
        max_memory_items = 10 # Example limit
        if len(self.actor_data.cognitive_core.short_term_memory) > max_memory_items:
            self.actor_data.cognitive_core.short_term_memory = \
                self.actor_data.cognitive_core.short_term_memory[-max_memory_items:]

    def _formulate_prompt(self) -> str:
        """
        Formulates a prompt for the LLM based on the actor's current state,
        goals, and recent perceptions.
        """
        goals_str = "; ".join([goal.description for goal in self.actor_data.cognitive_core.current_goals])
        
        # Ensure short_term_memory exists and is a list
        if not hasattr(self.actor_data.cognitive_core, 'short_term_memory') or \
           self.actor_data.cognitive_core.short_term_memory is None:
            self.actor_data.cognitive_core.short_term_memory = []
        memory_str = "; ".join(self.actor_data.cognitive_core.short_term_memory)
        
        emotions_str = ", ".join([f"{k}: {v}" for k,v in self.actor_data.cognitive_core.emotions.items()])

        prompt = (
            f"You are {self.actor_data.name}. Your description: {self.actor_data.description}.\n"
            f"Your current role/state: {self.actor_data.state.get('spiritual_state', self.actor_data.state.get('status', 'neutral'))}.\n"
            f"Your current goals are: [{goals_str}].\n"
            f"Your recent observations/thoughts (memory): [{memory_str}].\n"
            f"Your current emotions are: [{emotions_str}].\n\n"
            f"Based on this, what is your immediate, single next action? "
            f"Respond ONLY with a JSON object in the format: "
            f'{{"action_name": "your_action", "parameters": {{"param1": "value1", ...}}}}.\n'
            f"Example actions: 'pray', 'speak', 'observe_surroundings', 'record_vision', 'show_emotion_fear', 'compose_prayer'.\n"
            f"Your JSON response:"
        )
        return prompt

    def think_and_decide_action(self) -> Dict[str, Any]:
        """
        Formulates a prompt, queries the LLM, and returns a structured action.
        """
        prompt = self._formulate_prompt()
        
        action_json_schema = {
            "type": "object",
            "properties": {
                "action_name": {"type": "string"},
                "parameters": {"type": "object"}
            },
            "required": ["action_name"]
        }

        try:
            # The llm_interface instance is already configured (e.g. OpenRouterLLM knows its model and API key)
            # Specific per-call overrides could be passed if supported by LLMInterface.complete_json
            # llm_call_settings = self.actor_data.cognitive_core.llm_provider_settings
            
            action_json, metadata = self.llm_interface.complete_json(
                prompt,
                json_schema=action_json_schema
                # **llm_call_settings # If you want to pass temperature, max_tokens etc. per call
            )
            
            if "action_name" not in action_json:
                print(f"Warning: LLM response missing 'action_name'. Response: {action_json}")
                return {"action_name": "error_invalid_response", "parameters": {"reason": "Missing action_name", "raw_response": action_json}}
            
            # Consider clearing or managing short_term_memory after successful use
            # self.actor_data.cognitive_core.short_term_memory.clear()

            return action_json

        except Exception as e:
            print(f"Error during LLM call or response processing in CognitiveCore: {e}")
            return {"action_name": "error_llm_unavailable", "parameters": {"error_message": str(e)}}


class RuntimeActor:
    """
    Represents an Actor in the simulation at runtime.
    This class will eventually integrate with the Agno agent framework.
    """
    def __init__(self, actor_pydantic_data: ActorData, llm_interface: LLMInterface):
        """
        Initializes the RuntimeActor.
        Args:
            actor_pydantic_data: The Pydantic model instance for the actor's initial data.
            llm_interface: An instance of a class that implements LLMInterface.
        """
        self.pydantic_data = actor_pydantic_data 
        self.cognitive_core = RuntimeCognitiveCore(self.pydantic_data, llm_interface)
        
        print(f"RuntimeActor '{self.pydantic_data.name}' initialized with ID: {self.pydantic_data.id}.")

    def perceive(self, perception_input: str):
        """
        The actor perceives something from the environment or an event.
        """
        print(f"\nActor '{self.pydantic_data.name}' perceives: '{perception_input}'")
        self.cognitive_core.add_perception_to_memory(perception_input)

    def decide_and_act(self) -> Dict[str, Any]:
        """
        The actor uses its cognitive core to decide on an action.
        """
        print(f"Actor '{self.pydantic_data.name}' is thinking...")
        chosen_action = self.cognitive_core.think_and_decide_action()
        
        print(f"Actor '{self.pydantic_data.name}' decided action: {chosen_action}")
        return chosen_action

# Example of how you might use these (would be in a main simulation script)
# This __main__ block is for quick testing of this file itself,
# but the main execution will be from protopope.py
if __name__ == "__main__":
    # This block requires the actual schema and LLMInterface files to be importable.
    # For a quick test of this file, you might need to temporarily re-add
    # simplified Pydantic models and a mock LLMInterface here if imports fail.
    
    print("Running basic_runtime.py directly (for testing purposes).")
    print("Ensure Pydantic schemas and LLMInterface are correctly importable.")

    # --- Mock LLMInterface for direct testing of this file ---
    class MockLLMInterface(LLMInterface): # Inherit to satisfy type hint
        def __init__(self, provider="mock", model="mock_model"):
            self.provider = provider
            self.or_model = model # For compatibility if run_leo_vision_prototype checks it
            print(f"MockLLMInterface initialized for {provider} with model {model}")

        def complete_json(self, prompt: str, json_schema: Optional[Dict[str, Any]] = None, **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            print(f"\n--- MockLLMInterface ---")
            print(f"Received prompt for JSON completion:\n{prompt[:200]}...") # Truncate long prompts
            action = {"action_name": "mock_pray", "parameters": {"intensity": "high"}}
            print(f"Mocked LLM JSON Response: {action}")
            return action, {"model": "mock_model_direct_test", "usage": {}}

    # --- Test ---
    try:
        mock_llm = MockLLMInterface()
        
        # Create ActorData (Pydantic model instance)
        pope_actor_data_test = ActorData(
            name="Pope Leo XIII (Test)",
            description="Experiencing a vision.",
            cognitive_core=CognitiveCoreData( # Use the imported Pydantic model
                current_goals=[Goal(description="Understand the vision.")],
                emotions={"awe": 0.9, "fear": 0.7},
                short_term_memory=[] # Initialize explicitly
            ),
            state={"spiritual_state": "in_vision"}
        )

        pope_runtime_actor_test = RuntimeActor(pope_actor_data_test, mock_llm)
        initial_perception_test = "A test perception for direct execution."
        pope_runtime_actor_test.perceive(initial_perception_test)
        action_taken_test = pope_runtime_actor_test.decide_and_act()
        print(f"--- Direct Test Complete for {pope_runtime_actor_test.pydantic_data.name} ---")
        print(f"Action: {action_taken_test}")

    except ImportError as e:
        print(f"ImportError: {e}. Could not run direct test. Ensure schema files are in PYTHONPATH.")
    except Exception as e:
        print(f"An error occurred during direct test: {e}")

