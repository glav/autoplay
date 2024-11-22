# Create the runtime and register the agent.
from dataclasses import dataclass
import agent_common
from local_dir_agent import LocalDirAgent
from github_agent import GithubAgent
from router_agent import RouterAgent

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId, TopicId
from dataclasses import dataclass
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId, BaseAgent, MessageContext
from autogen_core.components import TypeSubscription

import asyncio
from autogen_ext.models import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient

runtime = SingleThreadedAgentRuntime()

async def main() -> None:
  await GithubAgent.register(
      runtime,
      agent_common.AGENT_GITHIB,
      lambda: GithubAgent(
        AzureOpenAIChatCompletionClient(model="gpt-4o",
                  #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
                  #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
                  #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
                  model_capabilities={
                    "vision": False,
                    "function_calling": True,
                    "json_output": False,
                }),
          ),
  )
  await LocalDirAgent.register(
      runtime,
      agent_common.AGENT_LOCAL_FILE,
      lambda: LocalDirAgent(
        AzureOpenAIChatCompletionClient(model="gpt-4o",
                  #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
                  #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
                  #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
                  model_capabilities={
                    "vision": False,
                    "function_calling": True,
                    "json_output": False,
                }),
          ),
  )
  await RouterAgent.register(
      runtime,
      agent_common.AGENT_ROUTER,
      lambda: RouterAgent(
        AzureOpenAIChatCompletionClient(model="gpt-4o",
                  #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
                  #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
                  #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
                  model_capabilities={
                    "vision": False,
                    "function_calling": True,
                    "json_output": False,
                }),
          ),
  )

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