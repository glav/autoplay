import agent_common
import os
import config
from base_sk_agent import base_sk_agent
from semantic_kernel.agents import ChatCompletionAgent
from autogen_core import MessageContext
from autogen_core import RoutedAgent, message_handler, type_subscription
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
import logging
from autogen_core import DefaultTopicId, RoutedAgent, default_subscription, message_handler
from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory, ChatMessageContent
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)


#@type_subscription(topic_type=agent_common.AGENT_TOPIC_LOCALDIR)
#@default_subscription
@type_subscription(topic_type=agent_common.AGENT_TOPIC_LOCALDIR)
class LocalDirAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient, logger: logging.Logger) -> None:
    #def __init__(self,logger: logging.Logger) -> None:
        super().__init__(agent_common.AGENT_LOCAL_FILE)
        self._system_messages = [SystemMessage(content="You are a helpful AI assistant.", source="system")]
        self._model_client = model_client
        self._logger = logger
        self.sk_agent = LocalDirAgent_SK(logger=logger)

    @message_handler
    async def handle_user_message(self, message: agent_common.AgentMessage, ctx: MessageContext) -> agent_common.LocalDirMessage:

        self._logger.info(f"LocalDirAgent_AG received message: {message.content}")

        response = await self.sk_agent.process_local_file_request(message.content)

        assert isinstance(response.content, str)
        return agent_common.LocalDirMessage(content=response.content)

class LocalDirAgent_SK(base_sk_agent):
    def __init__(self, logger: logging.Logger):
        super().__init__(logger=logger, service_id="local_dir_chat_service", agent_name="localdirchatagent", agent_instruction="You are a helpful AI assistant")

    async def process_local_file_request(self, query: str):
        # get dir contents
        files = os.listdir('/')
        context = ""
        for file in files:
            context += f"FilePath: {file}\n"

        # Prepare input to the chat completion model.
        response = await self.submit_query(query + "\nContext:\n" + context)

        self.logger.info(f"LocalDirAgent_SK response: {response}")
        print(response)
        # Return with the model's response.
        return response

