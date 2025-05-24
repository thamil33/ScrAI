import asyncio
import time

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.log import logger
from agno.models.lmstudio import LMStudio
from agno.models.openrouter import OpenRouter

#####################################
# Async execution
#####################################


model_local = LMStudio(id="darkidol-llama-3.1-8b-instruct-1.2-uncensored-iq-imatrix-request@q6_k")
model_openrouter = OpenRouter( id="meta-llama/llama-4-maverick:free", )


async def atask1(delay: int):
    """Simulate a task that takes a random amount of time to complete
    Args:
        delay (int): The amount of time to delay the task
    """
    logger.info("Task 1 has started")
    for _ in range(delay):
        await asyncio.sleep(1)
        logger.info("Task 1 has slept for 1s")
    logger.info("Task 1 has completed")
    return f"Task 1 completed in {delay:.2f}s"


async def atask2(delay: int):
    """Simulate a task that takes a random amount of time to complete
    Args:
        delay (int): The amount of time to delay the task
    """
    logger.info("Task 2 has started")
    for _ in range(delay):
        await asyncio.sleep(1)
        logger.info("Task 2 has slept for 1s")
    logger.info("Task 2 has completed")
    return f"Task 2 completed in {delay:.2f}s"


async def atask3(delay: int):
    """Simulate a task that takes a random amount of time to complete
    Args:
        delay (int): The amount of time to delay the task
    """
    logger.info("Task 3 has started")
    for _ in range(delay):
        await asyncio.sleep(1)
        logger.info("Task 3 has slept for 1s")
    logger.info("Task 3 has completed")
    return f"Task 3 completed in {delay:.2f}s"


async_agent = Agent(
    model=model_openrouter,
    tools=[atask2, atask1, atask3],
    show_tool_calls=True,
    markdown=True,
)

# Non-streaming response
# asyncio.run(async_agent.aprint_response("Please run all tasks with a delay of 3s"))
# Streaming response
asyncio.run(
    async_agent.aprint_response("Please run all tasks with a delay of 3s", stream=True)
)


#####################################
# Sync execution
#####################################
def task1(delay: int):
    """Simulate a task that takes a random amount of time to complete
    Args:
        delay (int): The amount of time to delay the task
    """
    logger.info("Task 1 has started")
    for _ in range(delay):
        time.sleep(1)
        logger.info("Task 1 has slept for 1s")
    logger.info("Task 1 has completed")
    return f"Task 1 completed in {delay:.2f}s"


def task2(delay: int):
    """Simulate a task that takes a random amount of time to complete
    Args:
        delay (int): The amount of time to delay the task
    """
    logger.info("Task 2 has started")
    for _ in range(delay):
        time.sleep(1)
        logger.info("Task 2 has slept for 1s")
    logger.info("Task 2 has completed")
    return f"Task 2 completed in {delay:.2f}s"


def task3(delay: int):
    """Simulate a task that takes a random amount of time to complete
    Args:
        delay (int): The amount of time to delay the task
    """
    logger.info("Task 3 has started")
    for _ in range(delay):
        time.sleep(1)
        logger.info("Task 3 has slept for 1s")
    logger.info("Task 3 has completed")
    return f"Task 3 completed in {delay:.2f}s"


sync_agent = Agent(
    model=model_local,
    tools=[task2, task1, task3],
    show_tool_calls=True,
    markdown=True,
)

# Non-streaming response
# sync_agent.print_response("Please run all tasks with a delay of 3s")
# Streaming response
sync_agent.print_response("Please run all tasks with a delay of 3s", stream=True)
