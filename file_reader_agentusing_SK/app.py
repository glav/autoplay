# Create the runtime and register the agent.
from dataclasses import dataclass
import agent_common
from agent_init import setup_sk_logging
from dotenv import load_dotenv
env_loaded = load_dotenv(dotenv_path="../.env", override=True)
print(f"Env variables loaded: {env_loaded}")


from autogen_core import SingleThreadedAgentRuntime
from autogen_core import AgentId, TopicId
from autogen_core import AgentId, BaseAgent, MessageContext

import asyncio
from autogen_core import TRACE_LOGGER_NAME
from runtime_init import SingleRuntimeFacade, DistributedRuntimeFacade
from autogen_core import DefaultTopicId, RoutedAgent, default_subscription, message_handler

runtime = SingleRuntimeFacade()
#runtime = DistributedRuntimeFacade()

async def main() -> None:
  ( execution_settings, history, logger) = await setup_sk_logging()

  #await register_agents(runtime.get_runtime)
  await runtime.start()
  await runtime.register_agents(logger=logger)

  # Start the runtime processing messages.
  #await runtime.start()

  while True:
    # Read a line of text from the console.
    #user_input = input("Enter a message for the agent: ")
    user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Enter a message for the agent: ")  # Unless you do input this way, message processing is blocked while waiting for input

    if not user_input or user_input.lower() == "exit":
      break

    # Send a message to the agent and get the response.
    #message = agent_common.UserRequestMessage(user_input)
    message = agent_common.AgentMessage(user_input)

    # Message Direct to agent
    #response = await runtime.send_message(message, AgentId(agent_common.AGENT_LOCAL_FILE, "default"))
    #response = await runtime.send_message(message, AgentId(agent_common.AGENT_ROUTER,"default"))

    await runtime.publish_message(message=message, topic_id=TopicId(type=agent_common.AGENT_TOPIC_USER_REQUEST, source="default"))
    #await runtime.publish_message(message=message, topic_id=DefaultTopicId())

    # Allow time for message processing
    await asyncio.sleep(5)

    # wait for the agent batch to complete,. then restart the runtime
    # await runtime.stop_when_idle()  # without this, messages dont get sent or processed unless you use sleep(..)
    # await runtime.start()

  # Stop the runtime processing messages.
  # This is the magic sauce. Without this, the loop keeps going around
  # and messages don't get sent or processed.
  await runtime.stop()  #


asyncio.run(main())
