# File: scrai/configurations/schemas/event_schema.py (or similar path like engine/narrative/event_system.py)

import uuid
import datetime
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class Event(BaseModel):
    """
    Represents a generic event that occurs within the simulation.
    Specific event types can inherit from this base model or be represented
    by a specific 'event_type' string and a structured 'data' payload.
    """
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for this specific event instance.")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp of when the event occurred or was created.")
    
    event_type: str = Field(..., description="A string identifying the type of event (e.g., 'ActorActionChosen', 'EnvironmentChange', 'TimeTick').")
    
    # The data payload can be a flexible dictionary. For more specific event types,
    # this could be a Union of other Pydantic models, or a more structured model itself
    # if all events share a common data structure beyond basic types.
    data: Dict[str, Any] = Field(default_factory=dict, description="Payload containing event-specific data.")
    
    source_entity_id: Optional[uuid.UUID] = Field(None, description="ID of the entity that initiated or caused the event (if applicable).")
    target_entity_id: Optional[uuid.UUID] = Field(None, description="ID of the entity primarily affected by the event (if applicable).")
    
    # Optional field for future use, e.g., for event processing priority or metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the event.")

    class Config:
        validate_assignment = True
        from_attributes = True # For potential ORM integration or creating from other objects

# Example Usage (for testing or demonstration):

# --- Example of a specific event type using the generic Event model ---
# Let's say an Actor performs an action.
class ActorActionEventData(BaseModel):
    """
    Specific data structure for an actor action event.
    This could be part of the 'data' field in the generic Event model,
    or a more complex Event model could use Union types for 'data'.
    """
    actor_id: uuid.UUID
    action_name: str
    action_params: Dict[str, Any]
    outcome_description: Optional[str] = None

    class Config:
        from_attributes = True


if __name__ == "__main__":
    # Generic TimeTick event
    time_tick_event = Event(
        event_type="TimeTick",
        data={"current_round": 105, "time_increment_seconds": 60}
    )
    print("--- TimeTick Event ---")
    print(time_tick_event.model_dump_json(indent=2))

    # Actor Action Event (using the generic Event model with a structured 'data' field)
    actor_id_example = uuid.uuid4()
    target_item_id = uuid.uuid4()
    
    action_data_payload = ActorActionEventData(
        actor_id=actor_id_example,
        action_name="use_item",
        action_params={"item_id": target_item_id, "target": "self"}
    )

    actor_action_event = Event(
        event_type="ActorActionChosen",
        data=action_data_payload.model_dump(), # Store the specific data model as a dict
        source_entity_id=actor_id_example,
        target_entity_id=target_item_id,
        metadata={"priority": 10}
    )
    print("\n--- Actor Action Event ---")
    print(actor_action_event.model_dump_json(indent=2))
    # To access structured data:
    # parsed_action_data = ActorActionEventData(**actor_action_event.data)
    # print(f"Action performed by actor {parsed_action_data.actor_id}: {parsed_action_data.action_name}")


    # Environment Change Event
    environment_change_event = Event(
        event_type="EnvironmentStateChanged",
        data={"location_id": uuid.uuid4(), "changed_property": "weather", "new_value": "raining"},
        metadata={"change_source": "WeatherSystem"}
    )
    print("\n--- Environment Change Event ---")
    print(environment_change_event.model_dump_json(indent=2))

    # Zeus Intervention Event (as per Blueprint.md)
    zeus_intervention_event = Event(
        event_type="ZeusInterventionEvent",
        data={"command": "possess_actor", "actor_id_to_possess": actor_id_example, "user_id": "developer_zeus"},
        source_entity_id=uuid.uuid4() # Could be a system ID for Zeus
    )
    print("\n--- Zeus Intervention Event ---")
    print(zeus_intervention_event.model_dump_json(indent=2))