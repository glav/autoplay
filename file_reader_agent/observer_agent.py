import agent_common
import os
from autogen_core.application import SingleThreadedAgentRuntime, WorkerAgentRuntime, WorkerAgentRuntimeHost
from autogen_ext.models import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from autogen_core.base import MessageContext, Subscription
from autogen_core.components import RoutedAgent, message_handler, type_subscription, TypeSubscription
from autogen_core.components.models import ChatCompletionClient, SystemMessage, UserMessage
import logging
from autogen_core.components import DefaultTopicId, RoutedAgent, default_subscription, message_handler
from autogen_core.application.logging import TRACE_LOGGER_NAME
import asyncio

#@type_subscription(topic_type=agent_common.AGENT_TOPIC_LOCALDIR)
#@default_subscription

#@type_subscription(topic_type=agent_common.AGENT_TOPIC_GITHUB)
#@type_subscription(topic_type=agent_common.AGENT_TOPIC_LOCALDIR)
#@type_subscription(topic_type="userrequest")
class ObserverAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient, logger: logging.Logger) -> None:
        super().__init__("observer_agent")
        self._system_messages = [SystemMessage("You are a helpful AI assistant.")]
        self._model_client = model_client
        self._logger = logger
        self._logger.info(">>>>> ObserverAgent initialized")

    @message_handler
    async def handle_user_message(self, message: agent_common.AgentMessage, ctx: MessageContext) -> None:
        self._logger.info(f">>>>> ObserverAgent received message: {message.content}")
        print(f">>>>> ObserverAgent received message: {message.content}")


async def main():

    logging.basicConfig(level=logging.DEBUG)  # Always have root logger set to FATAL
    logger = logging.getLogger(TRACE_LOGGER_NAME)

    logger.info(">>>>> Starting ObserverAgent")
    runtime = WorkerAgentRuntime(host_address="localhost:50052")
    runtime.start()


    await ObserverAgent.register(
      runtime,
      "observer_agent",
      lambda: ObserverAgent(
        AzureOpenAIChatCompletionClient(model="gpt-4o",
                  #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
                  #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
                  #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
                  model_capabilities={
                    "vision": False,
                    "function_calling": True,
                    "json_output": False,
                }),
                logger=logger,
          ),
    )
    await runtime.add_subscription(TypeSubscription(topic_type=agent_common.AGENT_TOPIC_USER_REQUEST, agent_type="observer_agent"))

    while True:
        await asyncio.sleep(2)

    await runtime.stop()

asyncio.run(main())
