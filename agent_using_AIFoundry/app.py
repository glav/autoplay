# Create the runtime and register the agent.
from dataclasses import dataclass

from dotenv import load_dotenv
env_loaded = load_dotenv(dotenv_path="../.env", override=True)
print(f"Env variables loaded: {env_loaded}")

import asyncio
from autogen_core import TRACE_LOGGER_NAME
from autogen_agentchat.ui import Console
from simple_agent import SimpleAgent
from agent_init import team, simple_agent, setup_agents


async def main() -> None:

  # foundryAgent = SimpleAgent()
  # await foundryAgent.setup()
  await setup_agents()
  while True:
    # Read a line of text from the console.
    user_input = input("Enter a message for the agent: ")
    #user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Enter a message for the agent: ")  # Unless you do input this way, message processing is blocked while waiting for input

    if not user_input or user_input.lower() == "exit":
      break

    #result = await foundryAgent.submit_query(user_input)
    #print("Result: ", result)
    stream = team.run_stream(
            task=user_input
        )  # what's the weather in New York?
    await Console(stream)

  await simple_agent.clean_up()



asyncio.run(main())
