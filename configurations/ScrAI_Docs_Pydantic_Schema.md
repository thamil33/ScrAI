# **ScrAI V-Next: Core Data Schemas Documentation**

Version: 0.1.0 (aligned with Blueprint Phase I)  
Last Updated: May 21, 2025

## **Introduction**

This document provides an exhaustive guide to the core Pydantic data schemas used in the ScrAI V-Next simulation engine. These schemas define the structure, validation, and serialization for the fundamental entities, actors, locations, events, scenarios, and simulation definitions that underpin the ScrAI world.

All schemas are designed with Pydantic V2, incorporating from\_attributes \= True in their Config for potential Object-Relational Mapper (ORM) integration and validate\_assignment \= True to ensure data integrity upon field modification.

This is a living document and will evolve as the ScrAI project progresses.

## **1\. Entity Schema (configurations/schemas/entity\_schema.py)**

The Entity schema is the most fundamental building block in ScrAI, representing any distinct item within the simulation.

### **1.1. Entity Model**

The base Pydantic model for any distinct item in the simulation. An Entity possesses an identity, properties, and state.

* **Fields:**  
  * id: uuid.UUID  
    * **Default:** uuid.uuid4() (auto-generated)  
    * **Description:** Unique identifier for the entity.  
  * name: str  
    * **Default:** None (Required field)  
    * **Description:** Human-readable name of the entity.  
  * description: Optional\[str\]  
    * **Default:** None  
    * **Description:** A brief description of the entity.  
  * properties: Dict\[str, Any\]  
    * **Default:** dict() (empty dictionary)  
    * **Description:** A flexible dictionary to store various characteristics and attributes of the entity (e.g., {"material": "wood", "weight\_kg": 10, "interactive": True}).  
  * state: Dict\[str, Any\]  
    * **Default:** dict() (empty dictionary)  
    * **Description:** A dictionary representing the current state of the entity (e.g., {"condition": "new", "position": {"x": 0, "y": 0}, "activated": False}).  
  * entity\_type: str  
    * **Default:** "GenericEntity"  
    * **Description:** The type of the entity, e.g., 'Actor', 'Object', 'LocationFeature'. This will typically be overridden by inheriting models.  
* **Config:**  
  * validate\_assignment \= True  
  * from\_attributes \= True

## **2\. Actor Schemas (configurations/schemas/actor\_schema.py)**

These schemas define the structure for intelligent agents (Actors) within the simulation, including their cognitive capabilities.

### **2.1. Goal Model**

Represents a goal an Actor might have.

* **Fields:**  
  * id: uuid.UUID  
    * **Default:** uuid.uuid4()  
    * **Description:** Unique identifier for the goal.  
  * description: str  
    * **Default:** None (Required field)  
    * **Description:** Description of the goal.  
  * status: str  
    * **Default:** "pending"  
    * **Description:** Status of the goal (e.g., pending, active, completed, failed).  
  * priority: int  
    * **Default:** 0  
    * **Description:** Priority of the goal (higher means more important).  
* **Config:**  
  * validate\_assignment \= True  
  * from\_attributes \= True

### **2.2. CognitiveCore Model**

Represents the 'mind' of an Actor. Responsible for perception processing, LLM interfacing, internal state management, and planning. This is an initial, basic placeholder and will be expanded significantly.

* **Fields:**  
  * current\_goals: List\[Goal\]  
    * **Default:** \[\] (empty list)  
    * **Description:** List of the actor's current goals.  
  * emotions: Dict\[str, float\]  
    * **Default:** dict()  
    * **Description:** Actor's emotional state (e.g., {'happiness': 0.7, 'anger': 0.1}).  
  * llm\_provider\_settings: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Settings for LLM interaction (e.g., model, temperature). Placeholder.  
  * current\_plan: Optional\[List\[str\]\]  
    * **Default:** None  
    * **Description:** A list of planned actions. Placeholder.  
  * short\_term\_memory: List\[str\]  
    * **Default:** \[\] (empty list)  
    * **Description:** Recent observations or thoughts. Placeholder.  
* **Config:**  
  * validate\_assignment \= True  
  * from\_attributes \= True

### **2.3. Actor Model**

A specialized type of Entity that possesses agency and a CognitiveCore. Actors are typically LLM-driven and capable of perception, decision-making, and goal-oriented action. Inherits from Entity.

* **Fields (in addition to Entity fields):**  
  * entity\_type: str  
    * **Default:** "Actor" (Overrides Entity default)  
    * **Description:** The type of the entity, fixed to 'Actor'.  
  * has\_agency: bool  
    * **Default:** True  
    * **Description:** Indicates if the actor can make decisions and act autonomously.  
  * cognitive\_core: CognitiveCore  
    * **Default:** CognitiveCore() (a new CognitiveCore instance)  
    * **Description:** The cognitive core (mind) of the actor.  
* **Config:**  
  * validate\_assignment \= True  
  * from\_attributes \= True

## **3\. World Schemas (configurations/schemas/world\_schema.py)**

These schemas define the structure for locations and coordinates within the simulation world.

### **3.1. Coordinates Model**

Represents 2D or 3D coordinates.

* **Fields:**  
  * x: float  
    * **Default:** None (Required field)  
    * **Description:** The X-coordinate.  
  * y: float  
    * **Default:** None (Required field)  
    * **Description:** The Y-coordinate.  
  * z: Optional\[float\]  
    * **Default:** None  
    * **Description:** The Z-coordinate (optional, for 3D spaces).  
* **Config:**  
  * from\_attributes \= True

### **3.2. WorldLocation Model**

Represents a distinct location within the simulation world. Inherits from Entity.

* **Fields (in addition to Entity fields):**  
  * entity\_type: str  
    * **Default:** "WorldLocation" (Overrides Entity default)  
    * **Description:** The type of the entity, fixed to 'WorldLocation'.  
  * coordinates: Optional\[Coordinates\]  
    * **Default:** None  
    * **Description:** The geographical coordinates of the location using the Coordinates model.  
  * contained\_entity\_ids: List\[uuid.UUID\]  
    * **Default:** \[\] (empty list)  
    * **Description:** List of IDs of entities (Actors, Objects) present in this location.  
  * connections: Dict\[str, uuid.UUID\]  
    * **Default:** dict()  
    * **Description:** Connections to other locations. Key is a descriptive name for the exit (e.g., "north\_door"), Value is the UUID of the WorldLocation it leads to.  
  * location\_category: str  
    * **Default:** "Undefined"  
    * **Description:** A category for the location (e.g., 'BuildingInterior', 'OutdoorWilderness', 'UrbanStreet').  
* **Config:**  
  * validate\_assignment \= True  
  * from\_attributes \= True

## **4\. Event Schema (configurations/schemas/event\_schema.py)**

Defines the structure for events that occur within the simulation, crucial for the event-driven architecture.

### **4.1. Event Model**

Represents a generic event that occurs within the simulation.

* **Fields:**  
  * event\_id: uuid.UUID  
    * **Default:** uuid.uuid4()  
    * **Description:** Unique identifier for this specific event instance.  
  * timestamp: datetime.datetime  
    * **Default:** datetime.datetime.now()  
    * **Description:** Timestamp of when the event occurred or was created.  
  * event\_type: str  
    * **Default:** None (Required field)  
    * **Description:** A string identifying the type of event (e.g., 'ActorActionChosen', 'EnvironmentChange', 'TimeTick').  
  * data: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Payload containing event-specific data. This can be a simple dictionary or a dump of another Pydantic model.  
  * source\_entity\_id: Optional\[uuid.UUID\]  
    * **Default:** None  
    * **Description:** ID of the entity that initiated or caused the event (if applicable).  
  * target\_entity\_id: Optional\[uuid.UUID\]  
    * **Default:** None  
    * **Description:** ID of the entity primarily affected by the event (if applicable).  
  * metadata: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Additional metadata about the event.  
* **Config:**  
  * validate\_assignment \= True  
  * from\_attributes \= True

## **5\. Scenario Schemas (configurations/schemas/scenario\_schema.py)**

These schemas define the structure for specific simulation setups, including initial states, actors, locations, and objectives.

### **5.1. ActorPlacement Model**

Defines where an actor is initially placed in the scenario.

* **Fields:**  
  * actor\_key\_or\_id: str  
    * **Default:** None (Required field)  
    * **Description:** A unique key or ID for the actor as defined in the scenario's initial\_actors list.  
  * starting\_location\_id: uuid.UUID  
    * **Default:** None (Required field)  
    * **Description:** The ID of the WorldLocation where the actor starts.  
* **Config:**  
  * validate\_assignment \= True  
  * from\_attributes \= True

### **5.2. Scenario Model**

Defines a specific setup or story within a SimulationDefinition. Details a particular starting state, Actors involved, initial goals, predefined events, and narrative settings.

* **Fields:**  
  * scenario\_id: uuid.UUID  
    * **Default:** uuid.uuid4()  
    * **Description:** Unique identifier for the scenario.  
  * name: str  
    * **Default:** None (Required field)  
    * **Description:** Human-readable name of the scenario.  
  * description: Optional\[str\]  
    * **Default:** None  
    * **Description:** A detailed description of the scenario, its premise, and objectives.  
  * initial\_actors: List\[Actor\]  
    * **Default:** \[\] (empty list)  
    * **Description:** List of Actor model instances involved in the scenario with their initial configurations.  
  * initial\_locations: List\[WorldLocation\]  
    * **Default:** \[\] (empty list)  
    * **Description:** List of WorldLocation model instances relevant to the scenario with their initial configurations.  
  * actor\_placements: List\[ActorPlacement\]  
    * **Default:** \[\] (empty list)  
    * **Description:** Specifies the starting location for each actor using ActorPlacement objects.  
  * predefined\_events: List\[Event\]  
    * **Default:** \[\] (empty list)  
    * **Description:** List of Event model instances that are predefined for this scenario.  
  * scenario\_objectives: List\[str\]  
    * **Default:** \[\] (empty list)  
    * **Description:** A list of objectives or goals for this scenario.  
  * narrative\_orchestrator\_config: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Configuration for the scenario's Narrative Orchestrator. Structure depends on the orchestrator's design.  
  * starting\_time: Optional\[datetime.datetime\]  
    * **Default:** None  
    * **Description:** The in-simulation starting date and time for the scenario.  
  * global\_scenario\_state: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Global state variables specific to this scenario (e.g., {"war\_status": "active"}).  
* **Config:**  
  * validate\_assignment \= True  
  * from\_attributes \= True

## **6\. Simulation Definition Schema (configurations/schemas/simulation\_definition\_schema.py)**

This schema defines the top-level configuration for an overarching simulation world or "metaverse."

### **6.1. SimulationDefinition Model**

Defines the top-level configuration for an overarching simulation world. It sets fundamental rules, physics, available actor archetypes, global LLM controller configurations, and references compatible scenarios.

* **Fields:**  
  * sim\_def\_id: uuid.UUID  
    * **Default:** uuid.uuid4()  
    * **Description:** Unique identifier for the simulation definition.  
  * name: str  
    * **Default:** None (Required field)  
    * **Description:** Human-readable name of the simulation definition (e.g., 'High Fantasy World').  
  * description: Optional\[str\]  
    * **Default:** None  
    * **Description:** A detailed description of the world, its themes, and core concepts.  
  * version: str  
    * **Default:** "0.1.0"  
    * **Description:** Version of this simulation definition.  
  * fundamental\_rules: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Core rules governing the simulation (e.g., {'time\_scale\_per\_round\_seconds': 60}).  
  * physics\_properties: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Basic physics or environmental properties (e.g., {'gravity\_multiplier': 1.0}).  
  * actor\_archetype\_references: List\[str\]  
    * **Default:** \[\] (empty list)  
    * **Description:** List of references (names or IDs) to available actor archetypes for this simulation definition.  
  * environment\_orchestrator\_config: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Default configuration for the Environment Orchestrator.  
  * narrative\_orchestrator\_config: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Default configuration for the Narrative Orchestrator.  
  * simulation\_governor\_config: Dict\[str, Any\]  
    * **Default:** dict()  
    * **Description:** Configuration for the Simulation Governor.  
  * compatible\_scenario\_references: List\[str\]  
    * **Default:** \[\] (empty list)  
    * **Description:** List of references (names or IDs) to scenarios compatible with this simulation definition.  
  * author: Optional\[str\]  
    * **Default:** None  
    * **Description:** Author or creator of this simulation definition.  
  * creation\_date: Optional\[str\]  
    * **Default:** None  
    * **Description:** Date when this simulation definition was created (ISO format string).  
* **Config:**  
  * validate\_assignment \= True  
  * from\_attributes \= True