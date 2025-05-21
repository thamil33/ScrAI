# ScrAI V-Next: Comprehensive Development Blueprint

**Version:** 0.1.0
**Date:** May 21, 2025

## 1. Introduction & Vision

This document outlines the comprehensive development blueprint for the next generation of ScrAI (referred to as ScrAI V-Next). The original ScrAI provided a foundational CLI framework for cognitive scenario simulated agents. This V-Next initiative aims to rebuild ScrAI from the ground up, focusing on creating a far more **robust, modular, scalable, and interactive experience.**

The core vision is to develop a sophisticated engine for simulating worlds populated by intelligent **Actors** (driven by Large Language Models and the Agno agent framework), capable of complex behaviors, interactions, and participation in emergent narratives. The system will support hierarchical LLM control, where LLMs not only drive individual Actors but also orchestrate environmental dynamics and narrative progression. A key aspect of the enhanced interactivity will be the inclusion of **"Zeus" (or God-mode/Possession) functionality**, allowing users to directly influence and participate in the simulation.

### 1.1. Core Philosophies

* **Modularity:** Components will be designed as loosely coupled modules with clear interfaces, facilitating independent development, testing, and replacement.
* **Scalability:** The architecture will be designed to handle increasingly complex simulations, larger numbers of Actors, and richer environments.
* **Extensibility:** The framework should be easily extendable with new Actor types, skills, environmental rules, LLM controllers, and plugins.
* **Interactivity & Direct Influence:** While starting API-first, the long-term goal includes rich developer dashboards and tools for observing, debugging, and directly interacting with simulations, including "Zeus" capabilities for direct intervention and Actor possession.
* **Developer-Friendly Naming:** Initial development will prioritize clear, descriptive, and consistent naming conventions for code elements. A project glossary will be maintained. Thematic renaming (e.g., "ScrAI Genesis," "Src||Y") can be considered as a separate, later initiative.

### 1.2. Key Technology Pillars & Development Environment

* **Programming Language:** **Python 3.12.x**. This version offers a balance of modern features, performance, and broad library compatibility.
* **Python Version Management:** **`pyenv-win`** is recommended for managing Python installations on Windows, allowing for easy switching between Python versions if needed and setting a project-specific version.
* **Package & Environment Management:** **`uv`** will be utilized for its speed and efficiency in creating virtual environments and installing/managing Python packages. Dependencies will be tracked, preferably in a `pyproject.toml` file, and can also be managed via `requirements.txt`.
* **Integrated Development Environment (IDE):** **Visual Studio Code (VS Code)** is the recommended IDE.
    * **Suggested VS Code Extensions:**
        * `Python` (by Microsoft): Essential for Python development, providing linting, debugging, IntelliSense, etc.
        * `Pylance` (by Microsoft): Offers enhanced language support, type checking, and autocompletion.
        * Consider others as needed for specific databases, Docker, etc.
* **Terminal Command Convention:** All terminal commands provided within this blueprint or subsequent documentation will assume usage of **Windows PowerShell**.
* **Agno Agent Framework:** To be used as the foundation for `Actor` implementations and potentially other autonomous LLM-driven components within the engine. (Reference: `https://docs.agno.com/introduction`)
* **Large Language Models (LLMs):** Central to Actor cognition and hierarchical control. The existing `LLM_interface.py` (supporting OpenRouter, LM Studio) will be retained and integrated.
* **Asynchronous Programming (`asyncio`):** For handling concurrent operations, especially LLM calls and multiple Actor processing.
* **Vector Databases:** For advanced semantic memory retrieval for Actors.
* **Pydantic:** For data validation, serialization, and configuration management.
* **Event-Driven Architecture:** Core to component decoupling.

## 2. Core Terminology & Concepts

Establishing clear terminology is crucial.

* **Entity:** The broadest term for any distinct item in the simulation possessing an identity, properties, and state. This includes Actors, interactive objects, groups, organizations, and even abstract concepts if they have defined characteristics and can be influenced.
* **Actor:** A specialized type of `Entity` that possesses **agency** and a **Cognitive Core**. Actors are typically LLM-driven (via their Cognitive Core) and capable of perception, decision-making, and goal-oriented action within the simulation. They will be implemented leveraging the Agno agent framework.
    * **Cognitive Core:** The "mind" of an `Actor`, responsible for processing perceptions, interfacing with its LLM to make decisions, manage internal state (emotions, goals), and plan actions.
* **Hierarchical LLM Controllers:** Beyond individual Actor minds, specialized LLMs will manage broader aspects of the simulation:
    * **Environment Orchestrator (or World Weaver/Architect):** An LLM responsible for dynamic environment descriptions, managing emergent environmental events, applying "soft laws" of the world, and reacting to collective Actor actions or global stimuli.
    * **Narrative Orchestrator (or Story Weaver/Director):** An LLM that guides the overall plot, introduces challenges/opportunities, adjusts pacing, and ensures narrative coherence or exploration of specific themes.
    * **Simulation Governor:** A top-level LLM or rule-based system that oversees the entire simulation, enforcing fundamental rules, managing simulation parameters, and potentially resolving high-level conflicts or paradoxes.
* **Simulation Definition (or World Setting):** A top-level configuration defining an overarching world, its fundamental rules, physics, available `Actor` archetypes, global LLM controllers (like the `EnvironmentOrchestrator`), and other foundational parameters. This forms the "metaverse" rules.
* **Scenario (or Story Pattern):** A specific setup or story *within* a `SimulationDefinition`. It details a particular starting state, the specific `Actors` involved, their initial goals, predefined events, and potentially a specialized `NarrativeOrchestrator` configuration. Multiple Scenarios can exist within one `SimulationDefinition`.
* **Project Glossary:** A document will be maintained to define these and other key terms as they are solidified, ensuring consistent usage across the project.

## 3. Proposed Directory Structure

This structure aims for clarity, modularity, and scalability.


/scrai/                         # Project Root
|
├── .venv/                          # Virtual environment created by uv
├── .python-version                 # File for pyenv to specify Python 3.12.x
|
├── /app/                           # Runnable applications (CLI, UI)
│   ├── /cli/                       # Command-Line Interface
│   │   ├── /commands/              # Modules for individual CLI commands
│   │   └── cli_main.py             # Main CLI entry point
│   └── /ui/                        # User Interface components (Web or TUI)
│       ├── /dashboard/             # Developer Dashboard / Zeus Interface
│       └── ui_main.py              # Main UI entry point
│
├── /engine/                        # Core simulation framework and logic
│   ├── /actors/                    # Definitions for in-simulation "Actors"
│   │   ├── actor_base.py           # Base class for Actors (integrating Agno Agent)
│   │   ├── cognitive_core.py       # Logic for LLM-driven decision making for Actors
│   │   └── /archetypes/            # Data/templates for pre-defined Actor types
│   │
│   ├── /environment/               # World structure, state, and dynamics
│   │   ├── world_base.py           # Base classes for world, regions, locations
│   │   ├── /structures/            # Global, Regional, Local environment class definitions
│   │   ├── /objects/               # In-world interactive objects (Entities)
│   │   └── /orchestrators/         # Environment Orchestrator LLM and logic
│   │       └── environment_orchestrator.py
│   │
│   ├── /narrative/                 # Story progression, event management
│   │   ├── event_system.py         # Event definitions, bus, and processing
│   │   ├── /orchestrators/         # Narrative Orchestrator LLM and logic
│   │   │   └── narrative_orchestrator.py
│   │   └── /elements/              # Quests, goals, narrative arcs
│   │
│   ├── /simulation/                # Orchestration of the simulation loop
│   │   ├── simulator.py            # Main simulation controller/loop
│   │   ├── time_manager.py         # Controls simulation time
│   │   ├── perception_manager.py   # Gathers/provides perception data to Actors
│   │   └── simulation_governor.py  # Top-level simulation LLM/rules
│   │
│   ├── /systems/                   # Cross-cutting foundational systems
│   │   ├── /memory_system/         # Interface & implementations for Actor memory (incl. vector DB)
│   │   ├── /message_system/        # Communication channels & message handling
│   │   ├── /action_system/         # Handling & consequences of Actor actions
│   │   ├── /interaction_system/    # Manages direct user ("Zeus") interactions
│   │   └── /rules_engine/          # (Optional) Codified rules or LLM adjudicator
│   │
│   ├── /interfaces/                # Abstract base classes/protocols for core components
│   └── /llm_services/              # Integration of the existing LLM_interface.py
│       └── llm_interface.py
│
├── /configurations/                # Default schemas, templates for defining simulations
│   ├── /schemas/                   # Pydantic models for validating user definitions
│   │   ├── entity_schema.py
│   │   ├── actor_schema.py
│   │   ├── world_schema.py
│   │   ├── simulation_definition_schema.py
│   │   └── scenario_schema.py
│   └── /templates/                 # YAML templates for quick-starting definitions
│       ├── /actors/
│       ├── /worlds/
│       ├── /simulation_definitions/
│       └── /scenarios/
│
├── /data_store/                    # Persisted data: user definitions, active simulation runs
│   ├── /library/                   # User-created definitions (blueprints)
│   │   ├── /actors/                # e.g., my_hero_profile.yaml
│   │   ├── /worlds/                # e.g., my_custom_world_pattern.yaml
│   │   ├── /simulation_definitions/# e.g., fantasy_ruleset.yaml
│   │   └── /scenarios/             # e.g., dragon_quest_scenario.yaml
│   └── /active_simulations/        # Data from specific, ongoing/paused simulation instances
│       └── /<simulation_run_id>/
│           ├── state_snapshots/    # For saving/resuming
│           ├── actor_memories/     # Backups or non-vector parts of memory
│           └── logs/               # Detailed logs for this run
│
├── /plugins/                       # For future extensibility
│   └── /example_plugin_name/
│       └── init.py
│
├── /tools/                         # Helper scripts, utilities, "Factories"
│   ├── /factories/                 # Scripts to generate boilerplate for assets
│   │   ├── actor_factory.py
│   │   ├── world_factory.py
│   │   └── scenario_factory.py
│   └── /validators/                # Scripts for structure/consistency checks
│
├── /docs/                          # Project documentation (including this blueprint)
├── /tests/                         # Unit and integration tests
│
├── .env                            # Environment variables
├── pyproject.toml                  # Project metadata and dependencies (for uv/pip)
├── README.md
└── blueprint.md                    # This document


## 4. Architecture & System Design Principles

* **Strongly Event-Driven:** The simulation will operate around a central event bus. Components (Actors, Orchestrators, Environment modules, UI) will publish events (e.g., `ActorActionChosenEvent`, `EnvironmentStateChangedEvent`, `TimeTickEvent`, `ZeusInterventionEvent`) and subscribe to relevant events. This promotes decoupling and reactive behavior.
* **Service-Oriented Internal Design:** Core functionalities will be exposed through well-defined internal services/managers:
    * `PerceptionManager`: Gathers and filters sensory information for each Actor based on its state, location, and abilities.
    * `ActionManager`: Validates, executes, and determines consequences of Actor actions.
    * `WorldStateManager`: Manages the ground truth of all Entities and environmental properties.
    * `TimeManager`: Controls the simulation clock, time progression, and time-based event triggers.
    * `ActorLifecycleManager`: Handles creation, registration, updates, and removal of Actors.
    * `MemoryService`: Provides an interface for Actors to store and retrieve memories, abstracting the underlying vector DB and other storage.
    * `InteractionManager` (New): Specifically handles inputs and effects from "Zeus" mode, translating user commands into simulation events or direct state changes.
* **Asynchronous Operations (`asyncio`):** Core simulation loops, LLM interactions, and potentially other I/O-bound or long-running tasks will be designed using `asyncio` to ensure responsiveness and allow for concurrent processing of multiple Actors and systems.
* **Dependency Injection:** Where appropriate, dependencies will be injected into components, allowing for easier testing (e.g., mocking services) and flexible configuration.
* **Clear Interfaces (`/engine/interfaces/`):** Abstract base classes or protocols will define the contracts for major components, ensuring substitutability and modularity.

## 5. Key System Components & Functionality

### 5.1. Engine Core (`/engine/`)

* **Actor Management (`/engine/actors/`)**
    * **`Actor` Base Class:** Implemented as an Agno agent. Will handle its own lifecycle (setup, run loop, cleanup).
    * **`CognitiveCore`:** Attached to each `Actor`.
        * Manages Actor-specific LLM interactions for decision-making.
        * Maintains internal state: dynamic goals, emotional state, plans.
        * Constructs prompts based on perception and internal state.
        * Parses and validates LLM action responses.
    * **Actor Archetypes (`/engine/actors/archetypes/`):** Pre-defined templates or factories for common Actor types.

* **Environment System (`/engine/environment/`)**
    * **Hierarchical Structure:** `GlobalEnvironment` > `RegionalEnvironment` > `LocalEnvironment`.
    * **`EnvironmentOrchestrator` (`/engine/environment/orchestrators/`):** LLM-driven component for managing dynamic aspects of the environment.
    * **Entities & Objects (`/engine/environment/objects/`):** Definition and state management for interactive and non-interactive Entities.
    * **World State Manager:** Central repository for environmental properties and Entity states.

* **Narrative System (`/engine/narrative/`)**
    * **Event System (`event_system.py`):** Central event bus. Standardized `Event` objects.
    * **`NarrativeOrchestrator` (`/engine/narrative/orchestrators/`):** LLM-driven component for guiding the overarching story.
    * **Quests & Goals (`/engine/narrative/elements/`):** System for defining, tracking, and resolving goals.

* **Simulation Control (`/engine/simulation/`)**
    * **`Simulator` (`simulator.py`):** Main coordinator of the simulation loop.
    * **`TimeManager` (`time_manager.py`):** Manages simulation clock and time-based events.
    * **`PerceptionManager` (`perception_manager.py`):** Constructs `perception` data for each `Actor`.
    * **`SimulationGovernor` (`simulation_governor.py`):** Top-level LLM/rule system for global parameters and rules.

* **Supporting Systems (`/engine/systems/`)**
    * **Memory System (`/memory_system/`):** Actor memory API, vector DB integration.
    * **Message System (`/message_system/`):** Manages communication channels.
    * **Action System (`/action_system/`):** Defines, validates, and executes Actor actions.
    * **Interaction System (`/interaction_system/`):** Specifically designed to handle "Zeus" mode inputs. This system will:
        * Provide an interface for the UI/CLI to submit user commands (e.g., possess Actor, modify Entity state, trigger event).
        * Translate these commands into appropriate actions or events within the simulation.
        * Manage permissions and scope of "Zeus" interventions.
    * **Rules Engine (`/rules_engine/`):** Optional for hard-coded mechanics.

* **LLM Services (`/engine/llm_services/`)**
    * Integration of the existing `llm_interface.py`.

### 5.2. Application Layer (`/app/`)

* **Command-Line Interface (`/cli/`):**
    * Primary interaction initially. Commands for simulation control, state inspection, "Zeus" commands (text-based).
* **User Interface / Developer Dashboard (`/ui/dashboard/`):** (Future, iterative development)
    * Web-based or advanced TUI (e.g., Textual).
    * **"Zeus" Mode / Direct Interaction Features:**
        * **Actor Possession:** Temporarily override an Actor's `CognitiveCore`, allowing the user to manually input its next action, type dialogue, or directly influence its internal state (goals, emotions).
        * **Entity Manipulation:** Directly view and modify the state/properties of any `Entity` in the simulation.
        * **Event Injection:** Manually trigger global, regional, or local events with custom parameters.
        * **Environment Modification:** Change weather, time of day, or other environmental variables.
        * **Resource Spawning/Control:** Add or remove resources or objects.
    * **Visualization:** Simulation state (maps, Actor statuses).
    * **Time Controls:** Pause, resume, step, speed.
    * **Agent Inspection:** View Actor memory, goals, perceptions.
    * **Log Exploration:** Interactive, filterable logs.

### 5.3. Configuration Management (`/configurations/`)

* **Pydantic Schemas (`/schemas/`):** For validating all user-creatable definitions.
* **Templates (`/templates/`):** YAML examples for quick-starting definitions.

### 5.4. Data Storage (`/data_store/`)

* **User Definition Library (`/library/`):** Storage for user-created YAML/JSON files.
* **Active Simulation Data (`/active_simulations/`):** State snapshots, Actor memories, logs.
* **Database Choices:** Vector Database (e.g., FAISS, ChromaDB) and Structured Data (SQLite, potentially PostgreSQL).

### 5.5. Tooling (`/tools/`)

* **Factories (`/factories/`):** Scripts to automate boilerplate creation.
* **Validators (`/validators/`):** Scripts for consistency checks.

## 6. Development Approach & Strategy

* **Initial Setup (Windows PowerShell):**
    1.  **Install `pyenv-win`:** Follow official instructions to install `pyenv-win` for managing Python versions.
    2.  **Install Python 3.12.x via `pyenv-win`:**
        ```powershell
        pyenv update
        pyenv install 3.12.x # Replace x with the latest patch version
        ```
    3.  **Navigate to Project Directory:** `cd path\to\scrai_genesis`
    4.  **Set Local Python Version:**
        ```powershell
        pyenv local 3.12.x
        ```
    5.  **Install `uv`:**
        ```powershell
        pip install uv  # Or use other installation methods from uv documentation
        # Ensure uv is in your PATH
        ```
    6.  **Create Virtual Environment with `uv`:**
        ```powershell
        uv venv
        # This creates a .venv directory
        ```
    7.  **Activate Virtual Environment (PowerShell):**
        ```powershell
        .\.venv\Scripts\Activate.ps1
        ```
    8.  **VS Code Interpreter:** Ensure VS Code is configured to use the Python interpreter from the `.venv` directory. (Usually `Ctrl+Shift+P` -> "Python: Select Interpreter").
* **Naming Conventions:**
    * **Initial Focus:** Clear, descriptive, consistent, developer-friendly names.
    * **Project Glossary:** Maintained to define terms.
    * **Thematic Refactoring (Future):** Considered a separate, post-core-development task.
* **API-First for Core Engine:** The `engine` components developed with clear internal Python APIs.
* **Iterative UI/Dashboard Development:**
    1.  Core engine with robust CLI (including basic "Zeus" text commands).
    2.  Stabilize engine API, then develop a simple developer dashboard for visualization and basic "Zeus" GUI interactions, expanding iteratively.
* **Testing Strategy:** Unit, integration, and end-to-end tests.
* **Version Control (Git):** Standard practice.
* **Documentation:** Continuous documentation. This blueprint is the start.

## 7. Phase I: Core Engine Implementation Priorities

1.  **Basic Project Setup:** Directory structure (as outlined), `pyproject.toml` for dependencies, initial `.env`, README.
2.  **Core Data Models (Pydantic):** `Entity`, `Actor`, `Event`, `WorldLocation`, `SimulationDefinition`, `Scenario`.
3.  **LLM Service Integration:** Integrate `llm_interface.py`.
4.  **Basic `Actor` Class:**
    * Agno agent integration (basic lifecycle).
    * Simple `CognitiveCore` (perception -> prompt -> LLM action -> basic validation).
5.  **Basic `PerceptionManager`:** Simple perception packet.
6.  **Basic `ActionManager`:** Handles "wait," "say_publicly."
7.  **Basic `WorldStateManager`:** Stores/retrieves locations, Actor positions.
8.  **Basic `EventSystem` & `TimeManager`:** Simple event bus, round progression.
9.  **Basic `Simulator`:** Core loop, Actor turns, action execution.
10. **Basic CLI:** Load simple `SimulationDefinition` & `Scenario`, run rounds, print actions.
11. **Basic `MemorySystem`:** In-memory list for observations.
12. **Logging:** Robust setup.
13. **Basic `InteractionSystem` (CLI-only):** Rudimentary text commands for "Zeus" to modify an Actor's goal or trigger a simple global event, to lay the groundwork for the `InteractionManager`.

This Phase I focuses on the absolute core loop with an Actor making LLM-driven decisions and performing simple actions, with initial hooks for "Zeus" interaction via CLI.

## 8. Future Considerations & Roadmap Ideas (Post-Phase I)

* **Advanced Memory System:** Full vector DB integration, memory lifecycle.
* **Sophisticated Actor Cognition:** Complex emotional models, multi-step planning, dynamic goal adaptation.
* **Hierarchical LLM Controllers:** Full implementation of `EnvironmentOrchestrator`, `NarrativeOrchestrator`, `SimulationGovernor`.
* **Rich Interactive Developer Dashboard with Full "Zeus" GUI.**
* **Plugin Architecture.**
* **Procedural Generation** for worlds/scenarios.
* **Scenario Editor GUI.**
* **Comprehensive Metrics & Analytics Dashboard.**
* **Multi-Actor Interactions & Social Dynamics.**
* **Persistent Environmental Changes.**

This blueprint provides a roadmap. It will evolve as development progresses and new insights are gained.
