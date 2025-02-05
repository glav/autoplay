from semantic_kernel.agents import ChatCompletionAgent
import logging
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
class base_sk_agent():
    def __init__(self, logger: logging.Logger, service_id: str, agent_name: str, agent_instruction: str):
        self.kernel = Kernel()
        self.service_id = service_id
        self.logger = logger
        self.history = ChatHistory()
        self.agent_name = agent_name
        self.agent_instruction = agent_instruction
        # self.chat_completion = AzureChatCompletion(
        #     deployment_name=config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
        #     api_key=config.AZURE_OPENAI_API_KEY,
        #     base_url=config.AZURE_OPENAI_ENDPOINT,
        #     service_id=self.service_id,
        # )
        self.chat_completion = AzureChatCompletion(service_id=self.service_id)

        self.kernel.add_service(self.chat_completion)
        self.execution_settings = AzureChatPromptExecutionSettings()
        self.execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        self.agent = ChatCompletionAgent(
            service_id=self.service_id, kernel=self.kernel, name=self.agent_name,
            instructions=self.agent_instruction, execution_settings=self.execution_settings)

    async def submit_query(self, query: str):
        self.history.add_user_message(query)
        # Get the response from the AI
        try:
            self.logger.info(f"{self.agent_name} - Processing query: {query}")
            results = self.agent.invoke(history=self.history)
            self.logger.info(f"{self.agent_name} -Query submitted.")
            response_content = ""
            async for content in results:
                self.logger.debug(f"# {content.role} - {content.name or '*'}: '{content.content}'")
                response_content += content.content

            self.history.add_message(ChatMessageContent(content=response_content, role="assistant"))
            # result = await self.chat_completion.get_chat_message_content(
            #     chat_history=self.history,
            #     settings=execution_settings,
            #     kernel=self.kernel,
            # )
        except Exception as e:
            self.logger.error(f"{self.agent_name} - Error during chat completion: {e}")
            #result = SystemMessage(content="An error occurred while processing your request.", source="system")

        return response_content
