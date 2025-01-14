# Create the runtime and register the agent.
from dataclasses import dataclass

from dotenv import load_dotenv
env_loaded = load_dotenv(dotenv_path="../.env", override=True)
print(f"Env variables loaded: {env_loaded}")

import asyncio
from autogen_core import TRACE_LOGGER_NAME
from agent_init import team
from autogen_agentchat.ui import Console


async def main() -> None:

  while True:
    # Read a line of text from the console.
    user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Enter a message for the agent: ")  # Unless you do input this way, message processing is blocked while waiting for input

    if not user_input or user_input.lower() == "exit":
      break

    stream = team.run_stream(
            task=user_input
        )  # what's the weather in New York?
    await Console(stream)



asyncio.run(main())
