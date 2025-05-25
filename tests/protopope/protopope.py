# File: protopope.py

import logging
import asyncio
import os

# --- 1. Import necessary components ---
# A. LLM Service
# Assuming llm_provider.py is in engine/llm_services/
from engine.llm_services.llm_provider import OpenRouterLLM, LLmClientInterface 

# B. Runtime Actor and Cognitive Core classes
# Assuming basic_runtime.py is in engine/actors/
from engine.actors.basic_runtime import ScrAIActorAgno
# Note: basic_runtime.py needs to import actual Pydantic schemas, not its internal placeholders

# C. Scenario definition function
# Assuming pope_leo_xiii_vision_scenario.py is in configurations/scenarios/
from configurations.scenarios.pope_vision_scenario import get_pope_leo_xiii_vision_scenario

# D. Pydantic models (primarily for type hinting if needed, actual data comes from scenario)
# from configurations.schemas.actor_schema import Actor as ActorData

def setup_logging():
    """Sets up basic logging for the prototype."""
    logging.basicConfig(level=logging.DEBUG, # Change to DEBUG for more verbose LLmClientInterface logs
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    # Reduce verbosity of httpx if it's too noisy at INFO level
    logging.getLogger("httpx").setLevel(logging.WARNING)


async def run_prototype():
    """
    Runs the Pope Leo XIII vision prototype.
    """
    logger = logging.getLogger("LeoVisionPrototype")
    logger.info("Starting Pope Leo XIII Vision Prototype...")

    # --- 2. Initialize the LLM Interface ---
    # This will use settings from your .env file (OPENROUTER_API_KEY, OPENROUTER_MODEL, etc.)
    try:
        # You can choose which LLM provider to use or let it auto-select
        # llm_provider = LLmClientInterface(provider="openrouter") # or "lmstudio" or "auto"
        llm_provider = OpenRouterLLM() 
        logger.info(f"LLM Interface initialized with provider: {llm_provider.provider}, model: {llm_provider.OPENROUTER_MODEL}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM Interface: {e}")
        logger.error("Please ensure your .env file is correctly set up with API keys and model names.")
        logger.error("For OpenRouter, OPENROUTER_API_KEY and OPENROUTER_MODEL (e.g., 'openai/gpt-4o') are needed.")
        return

    # --- 3. Load Scenario Data ---
    # This function returns the fully populated Scenario Pydantic model
    scenario_data = get_pope_leo_xiii_vision_scenario()
    logger.info(f"Loaded Scenario: {scenario_data.name}")
    
    # --- 3.1. Validate Pydantic Models ---
    logger.info("=== Validating Real Pydantic Model Usage ===")
    logger.info(f"Scenario ID: {scenario_data.scenario_id}")
    logger.info(f"Scenario Type: {type(scenario_data).__name__}")
    logger.info(f"Number of initial actors: {len(scenario_data.initial_actors)}")
    logger.info(f"Number of initial locations: {len(scenario_data.initial_locations)}")
    logger.info(f"Number of predefined events: {len(scenario_data.predefined_events)}")

    # --- 4. Extract and Instantiate the Main Actor (Pope Leo XIII) ---
    if not scenario_data.initial_actors:
        logger.error("No initial actors defined in the scenario.")
        return
    
    # Assuming Pope Leo XIII is the first actor defined in the scenario
    pope_leo_pydantic_data = scenario_data.initial_actors[0]
    
    # --- 4.1. Validate Actor Pydantic Model ---
    # logger.info("=== Actor Pydantic Model Validation ===")
    # logger.info(f"Actor Name: {pope_leo_pydantic_data.name}")
    # logger.info(f"Actor ID: {pope_leo_pydantic_data.id}")
    # logger.info(f"Actor Type: {type(pope_leo_pydantic_data).__name__}")
    # logger.info(f"Actor Entity Type: {pope_leo_pydantic_data.entity_type}")
    # logger.info(f"Has Agency: {pope_leo_pydantic_data.has_agency}")
    # logger.info(f"Number of Goals: {len(pope_leo_pydantic_data.cognitive_core.current_goals)}")
    # logger.info(f"Emotions: {pope_leo_pydantic_data.cognitive_core.emotions}")
    # logger.info(f"LLM Settings: {pope_leo_pydantic_data.cognitive_core.llm_provider_settings}")
    
    # Instantiate the ScrAIActor
    # The ScrAIActor's __init__ will create its RuntimeCognitiveCore
    model_id = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-4-maverick:free")
    pope_agno_actor = ScrAIActorAgno(
                actor_id="pope_agno_001",
                name="PopeAgno",
                description="An Agno-powered Pope providing divine guidance.",
                llm_provider="openrouter",
                llm_model_id=model_id,  # Use string model ID, not the provider object
                system_prompt="You are the Pope, offering wisdom and guidance. Respond concisely and with authority."
            )
    logger.info(f"ScrAIActorAgno'{pope_agno_actor.name}' created with model: {model_id}")

    # --- 5. Simulate the Initial Perception and Actor's Response ---
    current_perception_text = None
    if scenario_data.predefined_events:
        first_event = scenario_data.predefined_events[0]
        logger.info(f"Processing predefined event: {first_event.event_type}")
        logger.info(f"Event ID: {first_event.event_id}")
        logger.info(f"Event Timestamp: {first_event.timestamp}")
        if first_event.event_type == "SupernaturalPhenomenon" and first_event.data:
            current_perception_text = first_event.data.get("initial_perception_for_leo")
    
    if not current_perception_text:
        logger.warning("Could not find initial perception text in scenario's predefined events. Using a default.")
        current_perception_text = "You are in your private chapel. Suddenly, you hear a guttural voice, full of pride: 'I can destroy your Church.'"

    num_turns = 3
    chosen_action = None
    action_result = None

    for turn in range(1, num_turns + 1):
        logger.info(f"--- Turn {turn}/{num_turns} ---")

        # --- 5.1. Actor Perceives ---
        logger.info(f"Perception for turn {turn}: {current_perception_text}")
        perception_input = {"content": current_perception_text}
        pope_agno_actor.perceive(perception_input)
        
        # --- 5.2. Actor Decides ---
        logger.info(f"Requesting '{pope_agno_actor.name}' to decide...")
        chosen_action = await pope_agno_actor.decide()
        logger.info(f"Chosen Action (Turn {turn}): {chosen_action}")
        
        # --- 5.3. Actor Acts ---
        logger.info(f"Actor '{pope_agno_actor.name}' is performing action (Turn {turn})...")
        action_result = await pope_agno_actor.act(chosen_action)
        logger.info(f"Action Result (Turn {turn}): {action_result}")

        if "error" in chosen_action.get("action_name", "").lower():
            logger.warning(f"LLM interaction resulted in an error or fallback action on turn {turn}.")
            break # Exit loop on error

        # Prepare perception for the next turn based on the actor's reply
        if action_result and action_result.get("actor_reply"):
            current_perception_text = f"You previously stated: \"{action_result['actor_reply']}\". What is your reflection or next thought?"
        else:
            current_perception_text = "The previous action yielded no specific reply to reflect upon. What do you do next?"
        
        if turn < num_turns:
            logger.info("=== End of Turn State (Intermediate) ===")
            # Potentially log more detailed state if needed
        
    # --- 6. Results and Analysis (after all turns or error) ---
    logger.info(f"--- Prototype Run Complete ---")
    logger.info(f"Actor: {pope_agno_actor.name}")
    logger.info(f"Initial Perception (First Turn): {current_perception_text if current_perception_text else 'Default used'}")
    if chosen_action: # Ensure chosen_action is not None
        logger.info(f"Last Chosen Action (from LLM): {chosen_action}")
        success_flag = "error" not in chosen_action.get("action_name", "").lower()
    else:
        logger.info("No action was chosen (e.g., due to an early error).")
        success_flag = False


    if success_flag:
        logger.info("✅ SUCCESS: Real LLM successfully processed the scenario and provided a valid action for all turns or the last turn!")
    else:
        logger.warning("The LLM interaction resulted in an error or fallback action during one of the turns.")
        logger.warning("Check your .env file and network connectivity if errors persist.")
        
    # --- 7. Demonstrate Pydantic Model Serialization ---
    # logger.info("=== Pydantic Model Serialization Demo ===")
    # actor_json = pope_agno_actor.model_dump_json(indent=2)
    # logger.info(f"Actor can be serialized to JSON: {len(actor_json)} characters")
    
    # scenario_json = scenario_data.model_dump_json(indent=2)
    # logger.info(f"Scenario can be serialized to JSON: {len(scenario_json)} characters")
    
    # --- 8. Summary of Real vs Mock Usage ---
    # logger.info("=== Summary: Real Pydantic Models & LLM Usage ===")
    # logger.info("✅ Using real Pydantic schemas from configurations.schemas.*")
    # logger.info("✅ Using real LLM API calls via engine.llm_services.llm_provider")
    # logger.info("✅ Actor state is properly managed through Pydantic models")
    # logger.info("✅ Memory, emotions, and goals are tracked in the CognitiveCore")
    # logger.info("✅ JSON schema validation ensures proper LLM response format")
    # logger.info("✅ Error handling provides fallback actions if LLM fails")
    
    return {
        "scenario": scenario_data,
        "actor": pope_agno_actor,
        "last_action_taken": chosen_action, # Reflects the last action
        "last_action_result": action_result, # Reflects the result of the last action
        "success": success_flag
    }


if __name__ == "__main__":
    setup_logging()
    asyncio.run(run_prototype())

    # Note: This is a simple prototype. In a full application, you might want to handle exceptions more gracefully,