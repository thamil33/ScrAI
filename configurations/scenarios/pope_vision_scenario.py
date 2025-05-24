# File: scrai/configurations/scenarios/pope_leo_xiii_vision_scenario.py

import uuid
import datetime

# Import actual Pydantic schemas from the configurations.schemas modules
from configurations.schemas.actor_schema import Actor, Goal, CognitiveCore
from configurations.schemas.world_schema import WorldLocation, Coordinates
from configurations.schemas.event_schema import Event
from configurations.schemas.scenario_schema import Scenario, ActorPlacement


def get_pope_leo_xiii_vision_scenario() -> Scenario:
    """
    Defines and returns the Pydantic Scenario object for Pope Leo XIII's vision.
    """

    # 1. Define Actors
    pope_leo_xiii = Actor(
        name="Pope Leo XIII",
        description="The Supreme Pontiff, deeply spiritual and currently experiencing a profound vision.",
        properties={"title": "Pope", "age": 80}, # Example properties
        state={"physical_condition": "kneeling", "spiritual_state": "in_vision"},
        cognitive_core=CognitiveCore(
            current_goals=[
                Goal(description="Understand the meaning of this terrifying vision.", priority=10),
                Goal(description="Pray for the Church and humanity.", priority=9),
                Goal(description="Discern the appropriate response to the vision.", priority=8)
            ],
            emotions={"awe": 0.8, "fear": 0.6, "determination": 0.5, "sadness": 0.4},
            llm_provider_settings={"model": "should_be_overidden"} # Example, can be overridden
        )
    )

    # For this prototype, the "voices" are not full actors but will be delivered as perceptions/events.
    # If they were actors:
    # voice_of_satan = Actor(name="Voice of Satan", entity_type="SpiritualEntity", ...)
    # voice_of_lord = Actor(name="Voice of the Lord", entity_type="SpiritualEntity", ...)

    # 2. Define Locations
    private_chapel = WorldLocation(
        name="Pope Leo XIII's Private Chapel",
        description="A small, ornate chapel adjacent to the papal apartments. A sense of profound silence and sanctity usually pervades it, now disturbed.",
        location_category="SacredPlace_Interior",
        properties={"consecrated": True, "size": "small"},
        state={"lighting": "dim_candlelight", "atmosphere": "spiritually_charged_and_tense"}
    )

    # 3. Define Actor Placements
    leo_placement = ActorPlacement(
        actor_key_or_id=pope_leo_xiii.name, # Using name as key for simplicity
        starting_location_id=private_chapel.id
    )

    # 4. Define Predefined Events (to kickstart the vision narrative)
    # These events represent the initial stages of the vision being perceived by Pope Leo XIII.
    # In a full simulation, these might be triggered by a narrative orchestrator.
    
    event_vision_starts = Event(
        event_type="SupernaturalPhenomenon",
        data={
            "description": "A chilling vision begins to unfold. Two voices are heard.",
            "sensory_details": "A palpable darkness, a sense of dread, ethereal voices.",
            "initial_perception_for_leo": "Suddenly, the chapel seems to shift. You hear a guttural voice, full of pride: 'I can destroy your Church.'"
        },
        target_entity_id=pope_leo_xiii.id,
        metadata={"narrative_beat": "vision_onset"}
    )
    
    # This event could represent the Lord's reply, which Leo would then perceive.
    # For the prototype, we'll focus on Leo's reaction to the first voice.
    # event_lords_reply = Event(...) 


    # 5. Create the Scenario
    scenario_start_time = datetime.datetime(1884, 10, 13, 9, 0, 0) # Historically, the vision was on Oct 13, 1884. Time is arbitrary.

    pope_vision_scenario = Scenario(
        name="Pope Leo XIII's Vision of the Two Voices",
        description="A scenario depicting Pope Leo XIII experiencing his profound vision where he overhears a conversation between the Lord and Satan concerning the future of the Church.",
        initial_actors=[pope_leo_xiii],
        initial_locations=[private_chapel],
        actor_placements=[leo_placement],
        predefined_events=[event_vision_starts], # Start with the vision's onset
        scenario_objectives=[
            "Pope Leo XIII processes the initial parts of the vision.",
            "Pope Leo XIII decides on an initial spiritual or practical response (e.g., prayer, seeking to understand, composing a prayer)."
        ],
        narrative_orchestrator_config={
            "intensity": "high",
            "focus": "spiritual_conflict",
            "allow_player_intervention": False # Assuming this is a fixed narrative event for Leo
        },
        starting_time=scenario_start_time,
        global_scenario_state={
            "era": "late_19th_century"
        }
    )

    return pope_vision_scenario

if __name__ == "__main__":
    # This allows you to run this file directly to see the Pydantic model output
    scenario_data = get_pope_leo_xiii_vision_scenario()
    print("--- Pope Leo XIII's Vision Scenario Data ---")
    print(scenario_data.model_dump_json(indent=2))

    # Example: Accessing some data
    print(f"\nScenario Name: {scenario_data.name}")
    if scenario_data.initial_actors:
        pope = scenario_data.initial_actors[0]
        print(f"Main Actor: {pope.name}")
        if pope.cognitive_core.current_goals:
            print(f"Primary Goal: {pope.cognitive_core.current_goals[0].description}")
    if scenario_data.predefined_events:
        print(f"Initial Event Type: {scenario_data.predefined_events[0].event_type}")
        print(f"Initial Perception for Leo: {scenario_data.predefined_events[0].data.get('initial_perception_for_leo')}")

    # Note: In a real-world scenario, you would likely not print the entire scenario object,