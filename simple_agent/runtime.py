# Create the runtime and register the agent.
from dataclasses import dataclass

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId
from dataclasses import dataclass
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId, BaseAgent, MessageContext

import asyncio
from autogen_ext.models import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from agent import SimpleAgent, Message

runtime = SingleThreadedAgentRuntime()

async def main() -> None:
  await SimpleAgent.register(
      runtime,
      "simple_agent",
      lambda: SimpleAgent(
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
  # Send a message to the agent and get the response.
  message = Message("Hello, what are some fun things to do in Seattle?")
  response = await runtime.send_message(message, AgentId("simple_agent", "default"))
  print(response.content)
  # Stop the runtime processing messages.
  await runtime.stop()

asyncio.run(main())
