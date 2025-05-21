# File: scrai/configurations/schemas/actor_schema.py

import uuid
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

# Import the Entity model from its file
# Assuming entity_schema.py is in the same directory or accessible via Python path
# from .entity_schema import Entity 
# For standalone execution or if entity_schema is in the same file temporarily:
# (Remove this class definition if importing from entity_schema.py)
class Entity(BaseModel):
    """
    The base Pydantic model for any distinct item in the simulation.
    An Entity possesses an identity, properties, and state.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the entity.")
    name: str = Field(..., description="Human-readable name of the entity.")
    description: Optional[str] = Field(None, description="A brief description of the entity.")
    properties: Dict[str, Any] = Field(default_factory=dict, description="A flexible dictionary to store various characteristics and attributes of the entity.")
    state: Dict[str, Any] = Field(default_factory=dict, description="A dictionary representing the current state of the entity.")
    entity_type: str = Field("GenericEntity", description="The type of the entity, e.g., 'Actor', 'Object', 'LocationFeature'.")

    class Config:
        validate_assignment = True
        from_attributes = True


class Goal(BaseModel):
    """
    Represents a goal an Actor might have.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    description: str = Field(..., description="Description of the goal.")
    status: str = Field("pending", description="Status of the goal (e.g., pending, active, completed, failed).")
    priority: int = Field(0, description="Priority of the goal (higher means more important).")
    # Add other relevant fields like sub_goals, conditions for completion, etc.

class CognitiveCore(BaseModel):
    """
    Represents the 'mind' of an Actor.
    Responsible for perception processing, LLM interfacing, internal state management, and planning.
    This is a basic placeholder and will be expanded significantly.
    """
    # Internal state
    current_goals: List[Goal] = Field(default_factory=list, description="List of the actor's current goals.")
    emotions: Dict[str, float] = Field(default_factory=dict, description="Actor's emotional state (e.g., {'happiness': 0.7, 'anger': 0.1}).")
    
    # LLM interaction related (placeholders)
    llm_provider_settings: Dict[str, Any] = Field(default_factory=dict, description="Settings for LLM interaction (e.g., model, temperature).")
    
    # Planning related (placeholders)
    current_plan: Optional[List[str]] = Field(None, description="A list of planned actions.")
    
    # Memory system interface (placeholder - actual memory system will be more complex)
    short_term_memory: List[str] = Field(default_factory=list, description="Recent observations or thoughts.")
    
    class Config:
        validate_assignment = True
        from_attributes = True

class Actor(Entity):
    """
    A specialized type of Entity that possesses agency and a Cognitive Core.
    Actors are typically LLM-driven and capable of perception, decision-making,
    and goal-oriented action within the simulation.
    """
    # Override entity_type with a default for Actor
    entity_type: str = Field("Actor", description="The type of the entity, fixed to 'Actor'.")
    
    has_agency: bool = Field(True, description="Indicates if the actor can make decisions and act autonomously.")
    
    cognitive_core: CognitiveCore = Field(default_factory=CognitiveCore, description="The cognitive core (mind) of the actor.")

    # Actor-specific properties (can also be in 'properties' dict if preferred for more flexibility)
    # For example:
    # skills: Dict[str, int] = Field(default_factory=dict, description="Skills of the actor and their proficiency levels (e.g., {'combat': 5, 'persuasion': 3}).")
    # inventory: List[uuid.UUID] = Field(default_factory=list, description="List of entity IDs representing items in the actor's inventory.")

    class Config:
        """
        Pydantic model configuration for Actor.
        Ensures that Entity's config is also respected if not overridden.
        """
        validate_assignment = True
        from_attributes = True # Inherited from Entity's Config if not specified, but good to be explicit

# Example Usage:
if __name__ == "__main__":
    # Create a simple goal
    guard_goal = Goal(description="Patrol the west gate until dawn.", priority=10)

    # Create an Actor
    city_guard = Actor(
        name="Marcus",
        description="A stern-looking city guard.",
        properties={
            "faction": "CityWatch",
            "role": "Sentry",
            "armor_type": "Chainmail",
            "weapon": "Spear"
        },
        state={
            "status": "patrolling",
            "current_location_id": "west_gate_sector_1",
            "hp": 100,
            "stamina": 100
        },
        cognitive_core=CognitiveCore(
            current_goals=[guard_goal],
            emotions={"vigilance": 0.9, "boredom": 0.2},
            llm_provider_settings={"model": "meta-llama/Llama-3-8b-chat-hf:free", "temperature": 0.7}
        )
    )
    
    print("--- City Guard Actor ---")
    print(city_guard.model_dump_json(indent=2))
    
    print(f"\nGuard Name: {city_guard.name}")
    print(f"Guard ID: {city_guard.id}")
    print(f"Guard Entity Type: {city_guard.entity_type}")
    print(f"Guard has agency: {city_guard.has_agency}")
    if city_guard.cognitive_core.current_goals:
        print(f"Guard's primary goal: {city_guard.cognitive_core.current_goals[0].description}")
    
    # Modifying a field (thanks to validate_assignment=True)
    city_guard.state["status"] = "on_alert"
    city_guard.cognitive_core.emotions["suspicion"] = 0.5
    print("\n--- City Guard Actor (Updated State) ---")
    print(f"Guard status: {city_guard.state['status']}")
    print(f"Guard emotions: {city_guard.cognitive_core.emotions}")

    # Example of an actor with more detailed properties (if you choose to put them directly on Actor)
    # class ActorWithDirectProps(Entity):
    #     entity_type: str = Field("Actor", ...)
    #     has_agency: bool = Field(True, ...)
    #     cognitive_core: CognitiveCore = Field(default_factory=CognitiveCore, ...)
    #     skills: Dict[str, int] = Field(default_factory=dict)
    #
    # skilled_actor = ActorWithDirectProps(name="Elias", skills={"magic": 7, "alchemy": 4})
    # print(skilled_actor.model_dump_json(indent=2))
    # Note: The above example is for demonstration purposes. In a real application, you would likely have more complex logic