## Immediate High-Priority Next Steps

### Agno Agent Framework Integration

**Rationale:**  
Integrating the Agno framework is a key architectural decision (see `README.md` and `ProtoPope.md`). This will provide robust actor lifecycle management, concurrency, and advanced agent capabilities.

**Actions:**
- Refactor `RuntimeActor` (`engine/actors/basic_runtime.py`) to inherit from or be managed by the Agno agent structure.
- Map current `perceive` and `decide_and_act` logic into Agno's lifecycle methods (see `ProtoPope.md`).
- Consult `agno_docs.txt` for best practices on agent implementation, state management, and tool usage.

#### Key Integration Details & Alignment with Agno

- **Model Wrapping:**  
    Create a `ScrAILLMModelWrapper` inheriting from `AgnoModelBase` to wrap your custom `LLmClientInterface`. This allows Agno's agent lifecycle and tool management to be leveraged while retaining ScrAI logic.
- **Tool Invocation:**  
    Ensure that your `_chat_completion` method in the model wrapper returns an `AgnoMessage` with a `tool_calls` attribute, matching Agno's expected structure for tool invocation (see Agno's OpenAI-compatible tool calling format).
- **Tool Creation:**  
    Use a factory to generate Python callables for each ScrAI action, decorated with `@agno_tool`, and provide detailed docstrings for LLM guidance.
- **Agent Structure:**  
    Inherit your actor class from `agno.agent.Agent`, passing the model, tools, and dynamic instructions. Use the agent's context to manage actor state.
- **Parameter Handling:**  
    If possible, generate more specific function signatures for tools to improve LLM parameter accuracy.

---

### Implement Core Simulation Loop Components  
*(Blueprint Phase I Items #8 & #9)*

**Rationale:**  
The prototype (`protopope.py`) runs a single perception-action cycle. To enable continuous, dynamic simulations, the following components are essential:

**Actions:**
- **EventSystem** (`engine/narrative/event_system.py`):  
        Develop a central event bus. Actors, the `ActionManager`, and future systems (e.g., `WorldStateManager`) will publish/subscribe to `Event` objects (`event_schema.py`). This decouples components.
- **TimeManager** (`engine/simulation/time_manager.py`):  
        Manage simulation time, progress rounds, and trigger time-based events.
- **Simulator** (`engine/simulation/simulator.py`):  
        Create the main simulation loop. Use `TimeManager` to advance time and `EventSystem` to manage event flow, coordinating actor turns and actions.

---

## Subsequent Foundational Steps

### Develop PerceptionManager  
*(Blueprint Phase I Item #5)*

**Rationale:**  
Perceptions are currently simple strings. A `PerceptionManager` will enable structured, complex perception data tailored to each actor's state and environment.

**Actions:**
- Design and implement `engine/simulation/perception_manager.py`.
- Define how perceptions are generated (e.g., based on events, actor location, sensory capabilities).
- Modify `RuntimeActor` to receive/process structured perceptions from the `PerceptionManager`.

---

### Develop WorldStateManager  
*(Blueprint Phase I Item #7)*

**Rationale:**  
The `ActionManager` currently modifies actor state directly. A `WorldStateManager` is needed to manage the ground truth of all entities, their properties, and locations, reflecting changes from actions/events.

**Actions:**
- Implement `engine/environment/world_state_manager.py`.
- Define storage and update logic for `WorldLocation` data and entity states.
- Integrate `ActionManager` with `WorldStateManager` so actions affect the broader simulation world (e.g., moving an actor updates their location).

---

### Enhance MemorySystem  
*(Blueprint Phase I Item #11)*

**Rationale:**  
Current short-term memory is a simple list in `CognitiveCore`. The blueprint calls for a more robust `MemorySystem`, with potential for vector DB integration.

**Actions:**
- Design and implement a basic `MemoryService` (`engine/systems/memory_system/`) for actors.
- Define interfaces for storing memories (perceptions, actions, reflections).
- Integrate this service with `RuntimeCognitiveCore`.

---

### Basic CLI Enhancements & "Zeus" Functionality  
*(Blueprint Phase I Items #10 & #13)*

**Rationale:**  
To support more complex simulations and user interaction.

**Actions:**
- Update the CLI (e.g., in `protopope.py` or a dedicated CLI module) to load `SimulationDefinition` and `Scenario` files.
- Allow the `Simulator` to run for multiple rounds via CLI commands.
- Implement the initial `InteractionSystem` (`engine/systems/interaction_system/`) as outlined in `README.md`, enabling basic "Zeus" text commands (e.g., `change Pope Leo XIII's goal to 'Seek guidance from a cardinal'`).

---

## Considerations During Development

- **Asynchronous Operations:**  
        Plan for `asyncio` use in components like `Simulator` and `EventSystem`, especially for LLM calls and concurrent actor processing (see `README.md`).
- **Testing:**  
        Continue building tests for new components to ensure stability (see `test_action_variety.py` for actor behavior testing).
- **Modularity:**  
        Maintain modularity by defining clear interfaces between new managers and systems.

---

## Overall Approach & Recommendations

- Focus on aligning your model wrapper's output with Agno's tool-calling conventions, especially ensuring the `tool_calls` attribute is correctly populated for tool invocation.
- Use dynamic instructions and context passing to maximize agent flexibility.
- Consider refining tool parameter signatures for better LLM guidance.
- Once Agno is installed, test the integration flow between your model wrapper and Agno's agent run loop to ensure seamless tool dispatching.

By prioritizing Agno integration and the core simulation loop, ScrAI will rapidly gain the ability to run dynamic, multi-turn simulations, paving the way for advanced features outlined in the blueprint.
