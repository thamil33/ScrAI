# File: scrai/configurations/schemas/simulation_definition_schema.py

import uuid
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

# For standalone execution, we might need to define simplified versions
# of Actor and Scenario if we were to reference their full models.
# However, for SimulationDefinition, we'll mostly use references (like IDs or names)
# to keep it lean, so we might not need their full definitions here.

class SimulationDefinition(BaseModel):
    """
    Defines the top-level configuration for an overarching simulation world.
    It sets fundamental rules, physics, available actor archetypes,
    global LLM controller configurations, and references compatible scenarios.
    """
    sim_def_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the simulation definition.")
    name: str = Field(..., description="Human-readable name of the simulation definition (e.g., 'High Fantasy World', 'Sci-Fi Space Opera').")
    description: Optional[str] = Field(None, description="A detailed description of the world, its themes, and core concepts.")
    version: str = Field("0.1.0", description="Version of this simulation definition.")

    # Fundamental world rules and parameters
    # These are kept as flexible dictionaries for now.
    fundamental_rules: Dict[str, Any] = Field(
        default_factory=dict,
        description="Core rules governing the simulation (e.g., {'time_scale_per_round_seconds': 60, 'magic_system_enabled': True})."
    )
    physics_properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Basic physics or environmental properties (e.g., {'gravity_multiplier': 1.0, 'default_weather_pattern': 'temperate'})."
    )

    # References to actor archetypes/templates.
    # These could be names, IDs, or paths to archetype definition files.
    # Example: ["commoner_v1", "guard_v1", "merchant_v1"] or {"commoner_v1": "path/to/commoner.yaml"}
    actor_archetype_references: List[str] = Field(
        default_factory=list,
        description="List of references (names or IDs) to available actor archetypes for this simulation definition."
    )

    # Configurations for global LLM controllers (placeholders for now)
    environment_orchestrator_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default configuration for the Environment Orchestrator."
    )
    narrative_orchestrator_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default configuration for the Narrative Orchestrator."
    )
    simulation_governor_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration for the Simulation Governor."
    )

    # References to compatible scenarios.
    # These could be scenario names, IDs, or paths to scenario definition files.
    # Example: ["tutorial_quest", "dragon_lair_assault"]
    compatible_scenario_references: List[str] = Field(
        default_factory=list,
        description="List of references (names or IDs) to scenarios compatible with this simulation definition."
    )
    
    # Metadata
    author: Optional[str] = Field(None, description="Author or creator of this simulation definition.")
    creation_date: Optional[str] = Field(None, description="Date when this simulation definition was created (ISO format string).")


    class Config:
        validate_assignment = True
        from_attributes = True

# Example Usage:
if __name__ == "__main__":
    high_fantasy_world = SimulationDefinition(
        name="Aethelgard - Realm of Echoes",
        description="A high-fantasy world grappling with the remnants of an ancient magical war. Features powerful artifacts, diverse races, and political intrigue.",
        fundamental_rules={
            "time_scale_per_round_seconds": 300, # 5 minutes per round
            "magic_system": {
                "type": "elemental_and_arcane",
                "mana_regeneration_rate": 0.1 # points per second
            },
            "death_penalty": "respawn_at_shrine_with_debuff"
        },
        physics_properties={
            "gravity_multiplier": 1.0,
            "seasons_enabled": True,
            "day_night_cycle_hours": 24
        },
        actor_archetype_references=[
            "human_peasant_archetype",
            "elven_archer_archetype",
            "dwarven_warrior_archetype",
            "orc_shaman_archetype"
        ],
        environment_orchestrator_config={
            "llm_model": "gpt-4-environment-specialist",
            "event_frequency_multiplier": 1.0
        },
        narrative_orchestrator_config={
            "default_style": "player_driven_emergent",
            "conflict_introduction_rate": "medium"
        },
        simulation_governor_config={
            "max_actors_global": 200,
            "simulation_stability_checks_enabled": True
        },
        compatible_scenario_references=[
            "the_lost_artifact_of_eldoria_scenario",
            "siege_of_blackwood_keep_scenario",
            "journey_to_the_crystal_caves_scenario"
        ],
        author="ScrAI Dev Team",
        creation_date="2025-05-21"
    )

    print("--- High Fantasy World Simulation Definition ---")
    print(high_fantasy_world.model_dump_json(indent=2))

    print(f"\nSimulation Definition Name: {high_fantasy_world.name}")
    print(f"Version: {high_fantasy_world.version}")
    print(f"Available Actor Archetypes (references): {high_fantasy_world.actor_archetype_references}")
    print(f"Compatible Scenarios (references): {high_fantasy_world.compatible_scenario_references}")