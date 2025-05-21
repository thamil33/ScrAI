# File: scrai/configurations/schemas/scenario_schema.py

import uuid
import datetime # Required for Event model
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

# Assuming other schemas are in the same directory or accessible via Python path
# from .entity_schema import Entity # Base for Actor and WorldLocation
# from .actor_schema import Actor, Goal, CognitiveCore
# from .world_schema import WorldLocation, Coordinates
# from .event_schema import Event, ActorActionEventData

# For standalone execution or if schemas are in the same file temporarily:
# (Remove these class definitions if importing from their respective schema files)
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
# End of temporary declarations for standalone execution


class ActorPlacement(BaseModel):
    """Defines where an actor is initially placed in the scenario."""
    # This could be the actor's name if names are unique within the scenario's actor list,
    # or the actor's pre-assigned ID if you generate IDs before scenario instantiation.
    # Using a string key for flexibility, assuming it maps to an actor defined in initial_actors.
    actor_key_or_id: str = Field(..., description="A unique key or ID for the actor as defined in this scenario's initial_actors list.")
    starting_location_id: uuid.UUID = Field(..., description="The ID of the WorldLocation where the actor starts.")
    # Optional: specific starting state overrides for this actor in this scenario,
    # beyond what's in their base definition.
    # starting_state_override: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        validate_assignment = True

class Scenario(BaseModel):
    """
    Defines a specific setup or story within a SimulationDefinition.
    Details a particular starting state, Actors involved, initial goals,
    predefined events, and narrative settings.
    """
    scenario_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the scenario.")
    name: str = Field(..., description="Human-readable name of the scenario.")
    description: Optional[str] = Field(None, description="A detailed description of the scenario, its premise, and objectives.")
    
    # Defines the actors that are part of this scenario with their initial state.
    # These are full Actor model definitions.
    initial_actors: List[Actor] = Field(default_factory=list, description="List of actors involved in the scenario with their initial configurations.")
    
    # Defines the locations that are part of this scenario.
    # These are full WorldLocation model definitions.
    initial_locations: List[WorldLocation] = Field(default_factory=list, description="List of locations relevant to the scenario with their initial configurations.")

    # Specifies the starting location for each actor.
    # The actor_key_or_id should match an actor defined in initial_actors.
    # The starting_location_id should match a location defined in initial_locations.
    actor_placements: List[ActorPlacement] = Field(default_factory=list, description="Specifies the starting location for each actor.")
        
    # Events that are scheduled to occur at the beginning of the scenario or at specific triggers.
    predefined_events: List[Event] = Field(default_factory=list, description="List of events that are predefined for this scenario.")
    
    # Overall goals or objectives for the scenario.
    # This could be a textual description or a more structured list of objectives.
    scenario_objectives: List[str] = Field(default_factory=list, description="A list of objectives or goals for this scenario.")
    
    # Configuration for the Narrative Orchestrator specific to this scenario.
    # This is a flexible dictionary; its structure would depend on the Narrative Orchestrator's design.
    narrative_orchestrator_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for the scenario's Narrative Orchestrator.")

    # Other scenario-specific settings
    starting_time: Optional[datetime.datetime] = Field(None, description="The in-simulation starting date and time for the scenario.")
    global_scenario_state: Dict[str, Any] = Field(default_factory=dict, description="Global state variables specific to this scenario (e.g., 'war_status': 'active').")

    class Config:
        validate_assignment = True
        from_attributes = True

# Example Usage:
if __name__ == "__main__":
    # 1. Define some initial actors
    guard_actor = Actor(
        name="Valerius",
        description="A seasoned legionary guarding the fort entrance.",
        cognitive_core=CognitiveCore(current_goals=[Goal(description="Prevent unauthorized access to the fort.")])
    )
    merchant_actor = Actor(
        name="Silas",
        description="A traveling merchant with a cart full of wares.",
        cognitive_core=CognitiveCore(current_goals=[Goal(description="Reach the city market by sundown.")])
    )

    # 2. Define some initial locations
    fort_gate = WorldLocation(
        name="Fort Entrance",
        description="A sturdy wooden gate, flanked by watchtowers.",
        location_category="MilitaryStructure"
    )
    crossroads = WorldLocation(
        name="Old Crossroads",
        description="A dusty crossroads where the King's Road meets the Forest Path.",
        location_category="Road",
        connections={"north_to_fort": fort_gate.id} # Connects to the fort gate
    )
    # Ensure fort_gate knows about the crossroads if it's a two-way connection
    fort_gate.connections["south_to_crossroads"] = crossroads.id


    # 3. Define actor placements
    valerius_placement = ActorPlacement(actor_key_or_id=guard_actor.name, starting_location_id=fort_gate.id) # Using name as key
    silas_placement = ActorPlacement(actor_key_or_id=merchant_actor.name, starting_location_id=crossroads.id)

    # 4. Define a predefined event
    initial_weather_event = Event(
        event_type="EnvironmentStateChanged",
        data={"location_id": "all", "changed_property": "weather", "new_value": "clear_sky"},
        metadata={"description": "Scenario starts with clear weather."}
    )

    # 5. Create the Scenario
    border_incident_scenario = Scenario(
        name="Border Incident",
        description="A merchant approaches a heavily guarded fort gate. Tensions are high due to recent bandit activity.",
        initial_actors=[guard_actor, merchant_actor],
        initial_locations=[fort_gate, crossroads],
        actor_placements=[valerius_placement, silas_placement],
        predefined_events=[initial_weather_event],
        scenario_objectives=[
            "Merchant Silas successfully passes the gate or is turned away.",
            "Guard Valerius maintains fort security."
        ],
        narrative_orchestrator_config={"tension_level": 0.7, "allow_escalation": True},
        starting_time=datetime.datetime(2025, 5, 21, 14, 30, 0), # Example: May 21, 2025, 2:30 PM
        global_scenario_state={"bandit_threat_level": "high"}
    )

    print("--- Border Incident Scenario ---")
    print(border_incident_scenario.model_dump_json(indent=2))

    print(f"\nScenario Name: {border_incident_scenario.name}")
    print(f"First actor: {border_incident_scenario.initial_actors[0].name} starting at location ID: {border_incident_scenario.actor_placements[0].starting_location_id}")
    print(f"First location defined: {border_incident_scenario.initial_locations[0].name}")