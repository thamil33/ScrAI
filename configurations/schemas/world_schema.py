# File: scrai/configurations/schemas/world_schema.py

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


class Coordinates(BaseModel):
    """
    Represents 2D or 3D coordinates.
    """
    x: float
    y: float
    z: Optional[float] = None

    class Config:
        from_attributes = True


class WorldLocation(Entity):
    """
    Represents a distinct location within the simulation world.
    Inherits from Entity and adds location-specific attributes.
    """
    # Override entity_type with a default for WorldLocation
    entity_type: str = Field("WorldLocation", description="The type of the entity, fixed to 'WorldLocation'.")

    coordinates: Optional[Coordinates] = Field(None, description="The geographical coordinates of the location within its parent region or global space.")
    
    # List of IDs of entities (Actors, Objects) currently present in this location.
    # The WorldStateManager would be responsible for maintaining the accuracy of this list.
    contained_entity_ids: List[uuid.UUID] = Field(default_factory=list, description="List of IDs of entities present in this location.")
    
    # Defines connections to other locations.
    # Key: A descriptive name for the exit (e.g., "north_door", "forest_path_east").
    # Value: The UUID of the WorldLocation this exit leads to.
    connections: Dict[str, uuid.UUID] = Field(default_factory=dict, description="Connections to other locations.")
    
    location_category: str = Field("Undefined", description="A category for the location (e.g., 'BuildingInterior', 'OutdoorWilderness', 'UrbanStreet', 'Mystical').")
    
    # Examples of location-specific properties (can also be in the inherited 'properties' dict):
    # ambient_sound: Optional[str] = Field(None, description="Dominant ambient sound in the location.")
    # lighting_level: float = Field(0.5, description="Normalized lighting level (0.0 dark to 1.0 bright).")

    class Config:
        """
        Pydantic model configuration for WorldLocation.
        """
        validate_assignment = True
        from_attributes = True # Inherited, but explicit

# Example Usage:
if __name__ == "__main__":
    # Create some dummy UUIDs for connections and contained entities for the example
    connected_location_id_north = uuid.uuid4()
    connected_location_id_east_path = uuid.uuid4()
    actor_id_in_tavern = uuid.uuid4()
    object_id_in_tavern = uuid.uuid4()

    tavern_common_room = WorldLocation(
        name="The Prancing Pony - Common Room",
        description="A bustling common room filled with the scent of ale and woodsmoke. A large fireplace crackles merrily.",
        coordinates=Coordinates(x=10.5, y=22.3, z=0.0), # Assuming ground floor
        properties={
            "capacity": 30,
            "furnishings": ["tables", "chairs", "bar counter"],
            "ambient_sound": "chatter_and_clinking_mugs"
        },
        state={
            "current_occupancy": 15,
            "fireplace_lit": True
        },
        contained_entity_ids=[actor_id_in_tavern, object_id_in_tavern],
        connections={
            "door_to_street": connected_location_id_north, # Leads to a street location
            "kitchen_door": uuid.uuid4() # Leads to the tavern kitchen
        },
        location_category="BuildingInterior"
    )

    print("--- Tavern Common Room Location ---")
    print(tavern_common_room.model_dump_json(indent=2))
    print(f"\nLocation Name: {tavern_common_room.name}")
    print(f"Location ID: {tavern_common_room.id}")
    print(f"Location Category: {tavern_common_room.location_category}")
    if tavern_common_room.coordinates:
        print(f"Coordinates: x={tavern_common_room.coordinates.x}, y={tavern_common_room.coordinates.y}")
    print(f"Entities inside: {tavern_common_room.contained_entity_ids}")
    print(f"Connections: {tavern_common_room.connections}")


    forest_clearing = WorldLocation(
        name="Whispering Woods - Sunken Clearing",
        description="A quiet clearing where ancient stones jut from the mossy earth. Sunlight filters through the canopy.",
        coordinates=Coordinates(x=150.0, y=-75.2), # No z needed if it's a 2D map representation for this area
        properties={
            "flora": ["ancient_oaks", "moss", "wildflowers"],
            "fauna_signs": ["deer_tracks", "birdsong"]
        },
        state={
            "weather_effect": "dappled_sunlight",
            "time_of_day_effect": "serene"
        },
        connections={
            "path_north": connected_location_id_north, # Could lead back to the tavern's region or another part of the woods
            "hidden_trail_east": connected_location_id_east_path
        },
        location_category="OutdoorWilderness"
    )
    print("\n--- Forest Clearing Location ---")
    print(forest_clearing.model_dump_json(indent=2))