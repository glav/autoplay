# Create the runtime and register the agent.
from dataclasses import dataclass
import agent_common
from agent_init import register_agents

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId, TopicId
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId, BaseAgent, MessageContext

import asyncio
from autogen_ext.models import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient

runtime = SingleThreadedAgentRuntime()

async def main() -> None:
  await register_agents(runtime)

  # Start the runtime processing messages.
  runtime.start()

  while True:
    # Read a line of text from the console.
    user_input = input("Enter a message for the agent: ")

    if not user_input or user_input.lower() == "exit":
      break

    # Send a message to the agent and get the response.
    message = agent_common.UserRequestMessage(user_input)

    # Message Direct to agent
    #response = await runtime.send_message(message, AgentId(agent_common.AGENT_LOCAL_FILE, "default"))
    #response = await runtime.send_message(message, AgentId(agent_common.AGENT_ROUTER,"default"))

    await runtime.publish_message(message, topic_id=TopicId(type=agent_common.AGENT_TOPIC_USER_REQUEST, source="default"))

    # Allow time for message processing
    await asyncio.sleep(10)
    #await runtime.stop_when_idle()  # without this, messages dont get sent or processed unless you use sleep(..)

  # Stop the runtime processing messages.
  # This is the magic sauce. Without this, the loop keeps going around
  # and messages don't get sent or processed.
  await runtime.stop()  #


asyncio.run(main())
