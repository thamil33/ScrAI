# ScrAI Actors Module

This module provides actor implementations for the ScrAI simulation environment, including cognitive actors powered by LLMs via the Agno framework.

## Key Components

- `ScrAIActor`: Base actor class that provides the perception-decision-action cycle
- `ScrAIActorAgno`: Actor powered by an Agno agent with LLM capabilities

## Setup

### Prerequisites

To use the Agno-powered actors, you need to install the Agno library:

```powershell
# Activate the virtual environment
& C:\Users\tyler\dev\ScrAI\scrai\ScrAI\.venv\Scripts\Activate.ps1

# Install Agno
pip install agno
```

### Configuration

You can configure LLM providers through environment variables:

1. Create a `.env` file in the project root directory
2. Add your API keys to the file:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Usage Example

```python
import asyncio
from engine.actors.basic_runtime import ScrAIActorAgno

# Create an Agno-powered actor
actor = ScrAIActorAgno(
    actor_id="character_001",
    name="Assistant",
    description="A helpful assistant",
    llm_provider="openrouter",
    llm_model_id="meta-llama/llama-4-maverick:free",  # Free model for testing
    system_prompt="You are a helpful assistant that answers questions concisely."
)

# Run a perception-decision-action cycle
async def run_interaction():
    observation = {"query": "What's the capital of France?"}
    result = await actor.run_cycle(observation)
    print(f"Response: {result['actor_reply']}")

# Execute the interaction
asyncio.run(run_interaction())
```

## Available LLM Providers

- `openrouter`: Access to many models through OpenRouter
- `lmstudio`: Local models via LM Studio

## Available Models

For OpenRouter:
- `meta-llama/llama-4-maverick:free` - Free Llama model
- `anthropic/claude-3-haiku` - Fast Claude model

Check the [OpenRouter playground](https://openrouter.ai/playground) for more available models.
