# File: scrai/configurations/schemas/entity_schema.py

import uuid
from typing import Dict, Any, Optional, List # Added List for potential future use
from pydantic import BaseModel, Field

class Entity(BaseModel):
    """
    The base Pydantic model for any distinct item in the simulation.
    An Entity possesses an identity, properties, and state.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the entity.")
    name: str = Field(..., description="Human-readable name of the entity.")
    description: Optional[str] = Field(None, description="A brief description of the entity.")
    
    properties: Dict[str, Any] = Field(default_factory=dict, description="A flexible dictionary to store various characteristics and attributes of the entity.")
    # Example properties: {"material": "wood", "weight_kg": 10, "interactive": True}
    
    state: Dict[str, Any] = Field(default_factory=dict, description="A dictionary representing the current state of the entity.")
    # Example states: {"condition": "new", "position": {"x": 0, "y": 0}, "activated": False}

    entity_type: str = Field("GenericEntity", description="The type of the entity, e.g., 'Actor', 'Object', 'LocationFeature'.")

    class Config:
        """
        Pydantic model configuration.
        """
        validate_assignment = True # Ensures that fields are validated when assigned after model creation
        from_attributes = True # Enables creating models from ORM objects or other attribute-based objects (Pydantic V2+)

# Example Usage (for testing or demonstration):
if __name__ == "__main__":
    # Create a generic entity
    generic_item = Entity(name="Mysterious Box", description="A small, ornate wooden box.")
    generic_item.properties["material"] = "ancient wood"
    generic_item.properties["locked"] = True
    generic_item.state["condition"] = "dusty"
    generic_item.state["is_open"] = False
    
    print("--- Generic Entity ---")
    print(generic_item.model_dump_json(indent=2))
    print(f"Entity ID: {generic_item.id}")
    print(f"Entity Name: {generic_item.name}")
    print(f"Entity Type: {generic_item.entity_type}")

    # Example of an entity that might be an inanimate object
    rock = Entity(
        name="Large Boulder",
        description="A weathered grey boulder.",
        properties={"size_meters": 2.5, "movable": False, "climbable": True},
        state={"temperature_celsius": 15},
        entity_type="NaturalObject"
    )
    print("\n--- Rock Entity ---")
    print(rock.model_dump_json(indent=2))

    # Example of how an Actor might start (though Actor will be its own class)
    # This just shows how Entity can be a base.
    basic_actor_data = Entity(
        name="Guard Patrolling",
        description="A vigilant guard on patrol.",
        properties={"faction": "CityWatch", "role": "Sentry"},
        state={"status": "alert", "current_location_id": "gate_01"},
        entity_type="PotentialActorBase" # This would be 'Actor' once that model is defined
    )
    print("\n--- Basic Actor Data (as Entity) ---")
    print(basic_actor_data.model_dump_json(indent=2))

    try:
        # Test validation (if you had stricter types or validators)
        # For example, if name was not provided:
        # invalid_entity = Entity(description="This will fail") 
        pass
    except Exception as e:
        print(f"\nValidation Error Example: {e}")
    