# File: scrai/configurations/scenarios/pope_leo_xiii_vision_scenario.py

import uuid
import datetime

# Assuming Pydantic schemas are accessible.
# For a real project, these would be imported from their respective files in configurations.schemas
# e.g., from configurations.schemas.actor_schema import Actor, Goal, CognitiveCore
# from configurations.schemas.world_schema import WorldLocation, Coordinates
# from configurations.schemas.event_schema import Event
# from configurations.schemas.scenario_schema import Scenario, ActorPlacement

# --- Temporary Pydantic Model Definitions (for standalone execution) ---
# In a real setup, remove these and use proper imports from your schema files.
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class Entity(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)
    entity_type: str = "GenericEntity"
    class Config: from_attributes = True; validate_assignment = True

class Goal(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    description: str
    status: str = "pending"
    priority: int = 0
    class Config: from_attributes = True; validate_assignment = True

class CognitiveCore(BaseModel):
    current_goals: List[Goal] = Field(default_factory=list)
    emotions: Dict[str, float] = Field(default_factory=dict)
    llm_provider_settings: Dict[str, Any] = Field(default_factory=dict)
    current_plan: Optional[List[str]] = None
    short_term_memory: List[str] = Field(default_factory=list)
    class Config: from_attributes = True; validate_assignment = True

class Actor(Entity):
    entity_type: str = "Actor"
    has_agency: bool = True
    cognitive_core: CognitiveCore = Field(default_factory=CognitiveCore)
    class Config: from_attributes = True; validate_assignment = True

class Coordinates(BaseModel):
    x: float
    y: float
    z: Optional[float] = None
    class Config: from_attributes = True; validate_assignment = True

class WorldLocation(Entity):
    entity_type: str = "WorldLocation"
    coordinates: Optional[Coordinates] = None
    contained_entity_ids: List[uuid.UUID] = Field(default_factory=list)
    connections: Dict[str, uuid.UUID] = Field(default_factory=dict)
    location_category: str = "Undefined"
    class Config: from_attributes = True; validate_assignment = True

class Event(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    event_type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    source_entity_id: Optional[uuid.UUID] = None
    target_entity_id: Optional[uuid.UUID] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    class Config: from_attributes = True; validate_assignment = True

class ActorPlacement(BaseModel):
    actor_key_or_id: str 
    starting_location_id: uuid.UUID
    class Config: from_attributes = True; validate_assignment = True

class Scenario(BaseModel):
    scenario_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    description: Optional[str] = None
    initial_actors: List[Actor] = Field(default_factory=list)
    initial_locations: List[WorldLocation] = Field(default_factory=list)
    actor_placements: List[ActorPlacement] = Field(default_factory=list)
    predefined_events: List[Event] = Field(default_factory=list)
    scenario_objectives: List[str] = Field(default_factory=list)
    narrative_orchestrator_config: Dict[str, Any] = Field(default_factory=dict)
    starting_time: Optional[datetime.datetime] = None
    global_scenario_state: Dict[str, Any] = Field(default_factory=dict)
    class Config: from_attributes = True; validate_assignment = True
# --- End of Temporary Pydantic Model Definitions ---


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

    leo_vision_scenario = Scenario(
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
            "spiritual_veil_thin": True,
            "era": "late_19th_century"
        }
    )

    return leo_vision_scenario

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