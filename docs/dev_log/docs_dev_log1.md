# **ScrAI Dev Log: Laying the Foundation \- Project Setup & Core Data Models**

Date: May 21, 2025  
Author: Tyler Hamilton & ScrAI Dev Team

Welcome to the first (internal) dev log for ScrAI\! We're embarking on an exciting journey to rebuild ScrAI into a robust engine for simulating worlds with intelligent, LLM-driven Actors. Our roadmap is the Blueprint.md, and we're thrilled to report that we've successfully navigated the first two major milestones of Phase I.

## **Milestone 1: Basic Project Setup Complete\! (Blueprint Item \#1)**

Before diving into the complex machinery of simulated consciousness and emergent narratives, we had to lay a solid groundwork. This "Basic Project Setup" phase was all about getting our house in order:

* **Directory Structure Established:** We've scaffolded the initial project directories as outlined in the blueprint. Key areas like /engine/llm\_services/ (for our llm\_interface.py) and /configurations/schemas/ (which will house our Pydantic data models) are now in place. This organization will be crucial as the project grows.  
* **Dependency Management with uv:** We're committed to using uv for its speed and efficiency. The pyproject.toml file is set up to manage our dependencies, ensuring a consistent and reproducible development environment.  
* **Configuration via .env:** Sensitive information and environment-specific settings (like API keys for OpenRouter, model names, and local LM Studio URLs) are being managed through an .env file at the project root. Our llm\_interface.py is already wired up to use this.  
* **Foundational Documents:** The README.md provides a high-level overview, and the Blueprint.md itself serves as our comprehensive guide and will continue to evolve.

This initial setup might not be the most glamorous part, but it's vital for a project of this scale. A clean, well-organized foundation makes everything that follows smoother.

## **Milestone 2: Core Data Models Forged with Pydantic\! (Blueprint Item \#2)**

With the project structure in place, we moved on to defining the very essence of our simulation: the core data models. We've chosen Pydantic for this task, leveraging its excellent data validation, type hinting, and serialization capabilities. Our philosophy here has been "lean but expandable" – defining what's necessary for Phase I while ensuring the models can grow.

Here's a rundown of the Pydantic schemas we've established, all residing in /configurations/schemas/:

* **Entity (entity\_schema.py):** The most fundamental building block. Every distinct item in our simulation (Actors, objects, etc.) will be an Entity. It includes:  
  * id (auto-generated UUID)  
  * name (string)  
  * description (optional string)  
  * properties (flexible Dict\[str, Any\])  
  * state (flexible Dict\[str, Any\])  
  * entity\_type (string, e.g., "GenericEntity")  
  * We've also configured it with from\_attributes \= True (Pydantic V2 style for ORM mode) for future database integration.  
* **Actor (actor\_schema.py):** Our intelligent agents. Actor inherits from Entity and adds:  
  * has\_agency (boolean)  
  * cognitive\_core: A nested CognitiveCore model.  
* **CognitiveCore (within actor\_schema.py):** The "mind" of the Actor. For now, it's a placeholder structure for:  
  * current\_goals: A list of Goal objects.  
  * emotions: A dictionary for emotional states.  
  * llm\_provider\_settings: Configuration for LLM interactions.  
  * current\_plan and short\_term\_memory as placeholders.  
* **Goal (within actor\_schema.py):** A simple model to define an Actor's objectives, with a description, status, and priority.  
* **WorldLocation (world\_schema.py):** Defines distinct places in the simulation. It also inherits from Entity and includes:  
  * coordinates: A nested Coordinates model (x, y, optional z).  
  * contained\_entity\_ids: A list of UUIDs for entities present.  
  * connections: A dictionary mapping exit descriptions to other WorldLocation UUIDs.  
  * location\_category: A string (e.g., "BuildingInterior").  
* **Coordinates (within world\_schema.py):** A helper model for x, y, z coordinates.  
* **Event (event\_schema.py):** The heart of our event-driven architecture. The base Event model includes:  
  * event\_id (UUID)  
  * timestamp (datetime)  
  * event\_type (string, e.g., "ActorActionChosen")  
  * data (flexible Dict\[str, Any\])  
  * source\_entity\_id and target\_entity\_id (optional UUIDs).  
* **Scenario (scenario\_schema.py):** This model is key for setting up specific simulation instances. It brings together:  
  * scenario\_id, name, description.  
  * initial\_actors: A list of full Actor model definitions.  
  * initial\_locations: A list of full WorldLocation model definitions.  
  * actor\_placements: A list of ActorPlacement objects to define where each actor starts.  
  * predefined\_events: A list of Event models.  
  * scenario\_objectives, narrative\_orchestrator\_config, starting\_time, and global\_scenario\_state.  
* **ActorPlacement (within scenario\_schema.py):** A helper model to clearly define an actor's starting location within a scenario.  
* **SimulationDefinition (simulation\_definition\_schema.py):** The top-level "metaverse" ruleset. It's designed to be lean, primarily holding:  
  * sim\_def\_id, name, description, version.  
  * fundamental\_rules and physics\_properties (flexible dictionaries).  
  * actor\_archetype\_references (list of strings/IDs).  
  * Placeholder configurations for global LLM controllers (EnvironmentOrchestrator, NarrativeOrchestrator, SimulationGovernor).  
  * compatible\_scenario\_references (list of strings/IDs).

### **Key Decisions & Learnings So Far:**

* **Pydantic V2 & ORM Compatibility:** Standardizing on Pydantic V2 and including from\_attributes \= True in our model configs prepares us well for potential ORM integration down the line, making it easier to map these data structures to database tables.  
* **Modeling Approach:** We adopted a generally bottom-up approach for the most fundamental entities (Entity, WorldLocation, Event) and then used these to compose the more complex Actor, Scenario, and SimulationDefinition models. This felt like a natural way to build.  
* **Schema Organization:** Consolidating all Pydantic schemas under /configurations/schemas/ provides a clear and consistent location for our data contracts.

### **Next Steps**

With this foundational work complete, we're now ready to tackle **Blueprint Item \#3: LLM Service Integration**. This involves ensuring our llm\_interface.py is properly integrated and can be utilized by the CognitiveCore of our Actors. Following that, we'll dive into implementing the basic Actor class logic and its interaction loop.

It's been a productive start\! The groundwork laid in these first two phases is critical for the complex and exciting features planned for ScrAI... Onwards\!