import agent_common
import os
from base_sk_agent import base_sk_agent
from autogen_core import MessageContext
from autogen_core import RoutedAgent, message_handler, type_subscription
from autogen_core.models import ChatCompletionClient, SystemMessage
import logging


@type_subscription(topic_type=agent_common.AGENT_TOPIC_LOCALDIR)
class LocalDirAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient, logger: logging.Logger) -> None:
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
    """
    An agent that processes queries about local directory contents using Semantic Kernel.

    This agent lists files in the root directory and provides contextual information
    about the directory contents when responding to queries.

    Args:
        logger (logging.Logger): Logger instance for recording the agent's activities.

    Attributes:
        logger (logging.Logger): Logger for recording agent activities.
    """
    def __init__(self, logger: logging.Logger):
        super().__init__(logger=logger, service_id="local_dir_chat_service", agent_name="localdirchatagent", agent_instruction="You are a helpful AI assistant")

    async def process_local_file_request(self, query: str):
        """
        Process a query about local directory contents.

        This method lists files in the root directory, creates a context
        string with file paths, and submits the query with this context
        to obtain a response.

        Args:
            query (str): The user's query about local directory contents.

        Returns:
            Response containing information about the requested files/directories.
        """
        # get dir contents
        files = os.listdir('/')
        context = ""
        for file in files:
            context += f"FilePath: {file}\n"

        # Prepare input to the chat completion model.
        response = await self.submit_query(query + "\nContext:\n" + context)

        self.logger.info(f"LocalDirAgent_SK response: {response}")

        # Return with the model's response.
        return response

