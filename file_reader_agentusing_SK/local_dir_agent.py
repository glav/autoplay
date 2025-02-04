import agent_common
import os
import config
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
        self.sk_agent = LocalDirAgent_SK(kernel=Kernel(), logger=logger)

    @message_handler
    async def handle_user_message(self, message: agent_common.AgentMessage, ctx: MessageContext) -> agent_common.LocalDirMessage:

        self._logger.info(f"LocalDirAgent_AG received message: {message.content}")

        response = await self.sk_agent.process_local_file_request(message.content)

        assert isinstance(response.content, str)
        return agent_common.LocalDirMessage(content=response.content)

class LocalDirAgent_SK():
    def __init__(self, kernel: Kernel, logger):
        self.kernel = kernel
        self.service_id = "local_dir_chat_service"
        self.logger = logger
        self.history = ChatHistory()
        # self.chat_completion = AzureChatCompletion(
        #     deployment_name=config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
        #     api_key=config.AZURE_OPENAI_API_KEY,
        #     base_url=config.AZURE_OPENAI_ENDPOINT,
        #     service_id=self.service_id,
        # )
        self.chat_completion = AzureChatCompletion(service_id=self.service_id)

        self.kernel.add_service(self.chat_completion)
        execution_settings = AzureChatPromptExecutionSettings()
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        self.agent = ChatCompletionAgent(
            service_id=self.service_id, kernel=kernel, name="localdirchatagent",
            instructions="You are a helpful AI assistant", execution_settings=execution_settings)

    async def submit_query(self, query: str):
        self.history.add_user_message(query)
        # Get the response from the AI
        try:
            results = self.agent.invoke(history=self.history)
            response_content = ""
            async for content in results:
                print(f"# {content.role} - {content.name or '*'}: '{content.content}'")
                response_content += content.content

            # result = await self.chat_completion.get_chat_message_content(
            #     chat_history=self.history,
            #     settings=execution_settings,
            #     kernel=self.kernel,
            # )
        except Exception as e:
            self.logger.error(f"Error during chat completion: {e}")
            result = SystemMessage(content="An error occurred while processing your request.", source="system")
        self.history.add_message(ChatMessageContent(content=response_content, role="assistant"))
        return response_content

    async def process_local_file_request(self, query: str):
        # get dir contents
        files = os.listdir('/')
        context = ""
        for file in files:
            context += f"FilePath: {file}\n"

        # Prepare input to the chat completion model.
        response = await self.submit_query(query + "\nContext:\n" + context)

        self._logger.info(f"LocalDirAgent_SK response: {response.content}")
        print(response.content)
        # Return with the model's response.
        return response.content

