import agent_common
import config
from base_sk_agent import base_sk_agent
from autogen_core import MessageContext
from autogen_core import RoutedAgent, message_handler, type_subscription
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from githubreader.githubreader import GithubReader
from githubreader.githubrepo import GithubRepo
from githubreader.githubreporeader import GithubRepoReader
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

@type_subscription(topic_type=agent_common.AGENT_TOPIC_GITHUB)
class GithubAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient, logger: logging.Logger) -> None:
        super().__init__(agent_common.AGENT_GITHUB)
        self._system_messages = [SystemMessage(content="You are a helpful AI assistant.", source="system")]
        self._model_client = model_client
        self._logger = logger
        self.sk_agent = GithubAgent_SK(logger=logger)

    @message_handler
    async def handle_user_message(self, message: agent_common.AgentMessage, ctx: MessageContext) -> agent_common.GithubMessage:
        self._logger.info(f"GithubAgent received message: {message.content}")

        # Delegate all processing to the Semantic Kernel agent
        response = await self.sk_agent.process_github_request(message.content)

        self._logger.info(f"GithubAgent response: {response.content}")
        assert isinstance(response.content, str)
        return agent_common.GithubMessage(content=response.content)


class GithubAgent_SK(base_sk_agent):
    """
    A Semantic Kernel-based GitHub agent that processes queries related to GitHub repositories.

    This agent retrieves contents from GitHub repositories using the GitHub API and provides
    context-enriched responses to user queries by submitting the repository information and
    user query to a language model. It handles authentication, error management, and
    formats responses appropriately.
    """
    def __init__(self, logger: logging.Logger):
        super().__init__(logger=logger, service_id="github_chat_service", agent_name="githubchatagent", agent_instruction="You are a helpful AI assistant")
        self.logger = logger

    async def process_github_request(self, query: str):
        """Process a GitHub repository query by retrieving repo contents and submitting to the language model."""
        try:
            # Validate GitHub token
            if not config.GITHUB_TOKEN:
                raise ValueError("No GITHUB_TOKEN defined in the environment.")

            # Get GitHub repository context
            context = await self._get_github_repo_context()

            # Submit query with context to the language model
            response = await self.submit_query(query + "\nContext:\n" + context)

            self.logger.info(f"GithubAgent_SK response: {response}")
            return response

        except Exception as e:
            self.logger.error(f"Error processing GitHub request: {str(e)}")
            error_message = f"Error accessing GitHub repository: {str(e)}"
            # Return error as a response object similar to what submit_query would return
            return UserMessage(content=error_message, source="system")

    async def _get_github_repo_context(self):
        """Retrieve GitHub repository contents and create context string."""
        # Create GitHub reader
        github_reader = await GithubReader.create(config.GITHUB_TOKEN, config.GITHUB_ORG)
        repo = GithubRepo(config.GITHUB_REPONAME)
        repo_reader = await GithubRepoReader.create(github_reader.org_to_use, github_reader.user, repo)

        # Get the repo contents as context
        repo_contents = await repo_reader.get_repo_contents_async()

        # Build context string with file paths
        context = ""
        for file in repo_contents:
            context += f"FilePath: {file.name}\n"

        self.logger.info(f"Retrieved context from GitHub repository with {len(repo_contents)} files")
        return context
