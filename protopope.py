# File: run_leo_vision_prototype.py
# (Place in project root or a 'prototypes' directory)

import logging

# --- 1. Import necessary components ---
# A. LLM Service
# Assuming llm_interface.py is in engine/llm_services/
from engine.llm_services.llm_interface import OpenRouterLLM, LLMInterface 

# B. Runtime Actor and Cognitive Core classes
# Assuming basic_runtime.py is in engine/actors/
from engine.actors.basic_runtime import RuntimeActor 
# Note: basic_runtime.py needs to import actual Pydantic schemas, not its internal placeholders

# C. Scenario definition function
# Assuming pope_leo_xiii_vision_scenario.py is in configurations/scenarios/
from configurations.scenarios.pope_vision_scenario import get_pope_leo_xiii_vision_scenario

# D. Pydantic models (primarily for type hinting if needed, actual data comes from scenario)
# from configurations.schemas.actor_schema import Actor as ActorData

def setup_logging():
    """Sets up basic logging for the prototype."""
    logging.basicConfig(level=logging.DEBUG, # Change to DEBUG for more verbose LLMInterface logs
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    # Reduce verbosity of httpx if it's too noisy at INFO level
    logging.getLogger("httpx").setLevel(logging.WARNING)


def run_prototype():
    """
    Runs the Pope Leo XIII vision prototype.
    """
    logger = logging.getLogger("LeoVisionPrototype")
    logger.info("Starting Pope Leo XIII Vision Prototype...")

    # --- 2. Initialize the LLM Interface ---
    # This will use settings from your .env file (OPENROUTER_API_KEY, or_model, etc.)
    try:
        # You can choose which LLM provider to use or let it auto-select
        # llm_interface = LLMInterface(provider="openrouter") # or "lmstudio" or "auto"
        llm_interface = OpenRouterLLM() 
        logger.info(f"LLM Interface initialized with provider: {llm_interface.provider}, model: {llm_interface.or_model}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM Interface: {e}")
        logger.error("Please ensure your .env file is correctly set up with API keys and model names.")
        logger.error("For OpenRouter, OPENROUTER_API_KEY and or_model (e.g., 'openai/gpt-4o') are needed.")
        return

    # --- 3. Load Scenario Data ---
    # This function returns the fully populated Scenario Pydantic model
    scenario_data = get_pope_leo_xiii_vision_scenario()
    logger.info(f"Loaded Scenario: {scenario_data.name}")

    # --- 4. Extract and Instantiate the Main Actor (Pope Leo XIII) ---
    if not scenario_data.initial_actors:
        logger.error("No initial actors defined in the scenario.")
        return
    
    # Assuming Pope Leo XIII is the first actor defined in the scenario
    pope_leo_pydantic_data = scenario_data.initial_actors[0]
    
    # Instantiate the RuntimeActor
    # The RuntimeActor's __init__ will create its RuntimeCognitiveCore
    pope_runtime_actor = RuntimeActor(
        actor_pydantic_data=pope_leo_pydantic_data,
        llm_interface=llm_interface
    )
    logger.info(f"RuntimeActor '{pope_runtime_actor.pydantic_data.name}' created.")

    # --- 5. Simulate the Initial Perception and Actor's Response ---
    initial_perception_text = None
    if scenario_data.predefined_events:
        first_event = scenario_data.predefined_events[0]
        if first_event.event_type == "SupernaturalPhenomenon" and first_event.data:
            initial_perception_text = first_event.data.get("initial_perception_for_leo")
    
    if not initial_perception_text:
        logger.warning("Could not find initial perception text in scenario's predefined events. Using a default.")
        initial_perception_text = "You are in your private chapel. Suddenly, you hear a guttural voice, full of pride: 'I can destroy your Church.'"

    # Actor perceives the initial event/situation
    pope_runtime_actor.perceive(initial_perception_text)

    # Actor decides on an action (this will trigger the LLM call via CognitiveCore)
    logger.info(f"Requesting '{pope_runtime_actor.pydantic_data.name}' to decide and act...")
    chosen_action = pope_runtime_actor.decide_and_act()

    logger.info(f"--- Prototype Run Complete ---")
    logger.info(f"Actor: {pope_runtime_actor.pydantic_data.name}")
    logger.info(f"Initial Perception: {initial_perception_text}")
    logger.info(f"Chosen Action (from LLM): {chosen_action}")

    if "error" in chosen_action.get("action_name", "").lower():
        logger.warning("The LLM interaction resulted in an error or fallback action.")
        if chosen_action.get("parameters", {}).get("error_message"):
             logger.warning(f"Error details: {chosen_action['parameters']['error_message']}")
        elif chosen_action.get("parameters", {}).get("reason"):
            logger.warning(f"Fallback reason: {chosen_action['parameters']['reason']}")


if __name__ == "__main__":
    setup_logging()
    run_prototype()

    # Note: This is a simple prototype. In a full application, you might want to handle exceptions more gracefully,