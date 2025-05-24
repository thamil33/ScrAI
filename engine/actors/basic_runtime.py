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

# --- 2. Import REAL LLmClientInterface ---
from engine.llm_services.llm_provider import LLmClientInterface # Base class for type hinting
# Specific implementation (like OpenRouterLLM) will be passed in during instantiation.

# --- 3. Import Action System ---
from engine.systems.action_system import ActionManager, ActionOutcome, ActionResult


class RuntimeCognitiveCore:
    """
    Manages the Actor's thinking process, including LLM interaction.
    """
    def __init__(self, actor_pydantic_data: ActorData, llm_provider: LLmClientInterface):
        """
        Initializes the RuntimeCognitiveCore.
        Args:
            actor_pydantic_data: The Pydantic model instance for the actor's data.
            llm_provider: An instance of a class that implements LLmClientInterface (e.g., OpenRouterLLM).
        """
        self.actor_data = actor_pydantic_data  # This is the Pydantic model instance
        self.llm_provider = llm_provider
        # The Pydantic model actor_data.cognitive_core holds the state like goals, emotions, memory
        
        # Validate that we're using real Pydantic models
        if not hasattr(self.actor_data, 'model_dump'):
            raise ValueError("actor_pydantic_data must be a real Pydantic model, not a mock")
        
        # Ensure short_term_memory is properly initialized
        if not hasattr(self.actor_data.cognitive_core, 'short_term_memory') or \
           self.actor_data.cognitive_core.short_term_memory is None:
            self.actor_data.cognitive_core.short_term_memory = []

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
            f"Your current role/state: {self.actor_data.state.get('actor_state', self.actor_data.state.get('status', 'neutral'))}.\n"
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
            # The llm_provider instance is already configured (e.g. OpenRouterLLM knows its model and API key)
            # Specific per-call overrides could be passed if supported by LLmClientInterface.complete_json
            # llm_call_settings = self.actor_data.cognitive_core.llm_provider_settings
            
            action_json, metadata = self.llm_provider.complete_json(
                prompt,
                json_schema=action_json_schema
                # **llm_call_settings # If you want to pass temperature, max_tokens etc. per call
            )
            
            if "action_name" not in action_json:
                print(f"Warning: LLM response missing 'action_name'. Response: {action_json}")
                return {"action_name": "error_invalid_response", "parameters": {"reason": "Missing action_name", "raw_response": action_json}}
            
            # Log successful LLM interaction for debugging
            print(f"✅ LLM successfully responded with action: {action_json.get('action_name')}")
            
            # Consider clearing or managing short_term_memory after successful use
            # self.actor_data.cognitive_core.short_term_memory.clear()

            return action_json

        except Exception as e:
            print(f"❌ Error during LLM call or response processing in CognitiveCore: {e}")
            return {"action_name": "error_llm_unavailable", "parameters": {"error_message": str(e)}}


class RuntimeActor:
    """
    Represents an Actor in the simulation at runtime.
    This class will eventually integrate with the Agno agent framework.
    """
    def __init__(self, actor_pydantic_data: ActorData, llm_provider: LLmClientInterface):
        """
        Initializes the RuntimeActor.
        Args:
            actor_pydantic_data: The Pydantic model instance for the actor's initial data.
            llm_provider: An instance of a class that implements LLmClientInterface.
        """
        self.pydantic_data = actor_pydantic_data 
        self.cognitive_core = RuntimeCognitiveCore(self.pydantic_data, llm_provider)
        self.action_manager = ActionManager()  # Initialize ActionManager
        
        print(f"RuntimeActor '{self.pydantic_data.name}' initialized with ID: {self.pydantic_data.id}.")

    def perceive(self, perception_input: str):
        """
        The actor perceives something from the environment or an event.
        """
        print(f"\nActor '{self.pydantic_data.name}' perceives: '{perception_input}'")
        self.cognitive_core.add_perception_to_memory(perception_input)

    def decide_and_act(self) -> Dict[str, Any]:
        """
        The actor uses its cognitive core to decide on an action, then executes it.
        """
        print(f"Actor '{self.pydantic_data.name}' is thinking...")
        chosen_action = self.cognitive_core.think_and_decide_action()
        
        print(f"Actor '{self.pydantic_data.name}' decided action: {chosen_action}")
        
        # Execute the action through ActionManager
        outcome = self.execute_action(chosen_action)
        
        # Apply state changes from action execution
        self.apply_action_outcome(outcome)
        
        return {"action": chosen_action, "outcome": outcome}
    
    def execute_action(self, action: Dict[str, Any]) -> ActionOutcome:
        """
        Execute an action using the ActionManager and return the outcome.
        """
        print(f"Executing action: {action.get('action_name', 'unknown')}")
        outcome = self.action_manager.execute_action(action, self.pydantic_data)
        
        # Log the outcome
        if outcome.result == ActionResult.SUCCESS:
            print(f"✅ Action executed successfully: {outcome.message}")
        else:
            print(f"❌ Action execution {outcome.result.value}: {outcome.message}")
        
        return outcome
    
    def apply_action_outcome(self, outcome: ActionOutcome):
        """
        Apply the state changes from an action outcome to the actor's data.
        """
        if not outcome.state_changes:
            return
        
        print(f"Applying state changes: {outcome.state_changes}")
        
        # Apply general state changes
        for key, value in outcome.state_changes.items():
            if key == "emotion_changes":
                # Apply emotion changes to cognitive core
                for emotion, new_value in value.items():
                    if hasattr(self.pydantic_data.cognitive_core, 'emotions'):
                        self.pydantic_data.cognitive_core.emotions[emotion] = new_value
                        print(f"  Updated emotion {emotion} to {new_value}")
            elif key in ["spiritual_state", "current_location_id"]:
                # Apply to actor state
                self.pydantic_data.state[key] = value
                print(f"  Updated {key} to {value}")
            else:
                # Apply other state changes to general state
                self.pydantic_data.state[key] = value
                print(f"  Updated {key} to {value}")
    
    def get_available_actions(self) -> List[str]:
        """
        Get list of all available actions this actor can perform.
        """
        return self.action_manager.get_available_actions()
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Get a summary of the actor's current status including recent actions and state.
        """
        return {
            "name": self.pydantic_data.name,
            "current_state": self.pydantic_data.state,
            "emotions": self.pydantic_data.cognitive_core.emotions,
            "recent_memory": getattr(self.pydantic_data.cognitive_core, 'short_term_memory', [])[-3:],
            "available_actions_count": len(self.get_available_actions())
        }

# Example of how you might use these (would be in a main simulation script)
# This __main__ block is for quick testing of this file itself,
# but the main execution will be from protopope.py
if __name__ == "__main__":
    # This block requires the actual schema and LLmClientInterface files to be importable.
    # For a quick test of this file, you might need to temporarily re-add
    # simplified Pydantic models and a mock LLmClientInterface here if imports fail.
    
    print("Running basic_runtime.py directly (for testing purposes).")
    print("Ensure Pydantic schemas and LLmClientInterface are correctly importable.")

    # --- Mock LLmClientInterface for direct testing of this file ---
    class MockLLmClientInterface(LLmClientInterface): # Inherit to satisfy type hint
        def __init__(self, provider="mock", model="mock_model"):
            self.provider = provider
            self.OPENROUTER_MODEL = model # For compatibility if run_protopope.py_prototype checks it
            self.call_count = 0
            print(f"MockLLmClientInterface initialized for {provider} with model {model}")

        def complete_json(self, prompt: str, json_schema: Optional[Dict[str, Any]] = None, **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
            print(f"\n--- MockLLmClientInterface ---")
            print(f"Received prompt for JSON completion:\n{prompt[:200]}...") # Truncate long prompts
            
            # Return different actions based on call count
            actions = [
                {"action_name": "pray", "parameters": {"intensity": "high", "duration": "long"}},
                {"action_name": "record_vision", "parameters": {"detail": "divine light and future visions", "method": "mental record"}},
                {"action_name": "contemplate", "parameters": {"subject": "meaning of the vision"}},
                {"action_name": "observe_surroundings", "parameters": {"focus": "spiritual presence"}}
            ]
            
            action = actions[self.call_count % len(actions)]
            self.call_count += 1
            
            print(f"Mocked LLM JSON Response: {action}")
            return action, {"model": "mock_model_direct_test", "usage": {}}

    # --- Test ---
    try:
        mock_llm = MockLLmClientInterface()
        
        # Create ActorData (Pydantic model instance)
        pope_actor_data_test = ActorData(
            name="Pope Leo XIII (Test)",
            description="Experiencing a vision.",
            cognitive_core=CognitiveCoreData( # Use the imported Pydantic model
                current_goals=[Goal(description="Understand the vision.")],
                emotions={"awe": 0.9, "fear": 0.7},
                short_term_memory=[] # Initialize explicitly
            ),            state={"spiritual_state": "in_vision"}
        )
        
        pope_runtime_actor_test = RuntimeActor(pope_actor_data_test, mock_llm)
        initial_perception_test = "A divine light appears before me, radiating peace and wisdom."
        pope_runtime_actor_test.perceive(initial_perception_test)
        
        print(f"\n=== Initial Status ===")
        print(f"Status: {pope_runtime_actor_test.get_current_status()}")
        print(f"Available actions: {len(pope_runtime_actor_test.get_available_actions())} total")
        
        print(f"\n=== Action Execution ===")
        action_result = pope_runtime_actor_test.decide_and_act()
        
        print(f"\n=== Final Status ===")
        print(f"Status: {pope_runtime_actor_test.get_current_status()}")
        
        print(f"\n--- Direct Test Complete for {pope_runtime_actor_test.pydantic_data.name} ---")
        print(f"Full Action Result: {action_result}")
        
        # Test another action cycle
        print(f"\n=== Second Action Cycle ===")
        pope_runtime_actor_test.perceive("The vision becomes clearer, showing scenes of future events.")
        action_result_2 = pope_runtime_actor_test.decide_and_act()
        print(f"Second action result: {action_result_2}")

    except ImportError as e:
        print(f"ImportError: {e}. Could not run direct test. Ensure schema files are in PYTHONPATH.")
    except Exception as e:
        print(f"An error occurred during direct test: {e}")

