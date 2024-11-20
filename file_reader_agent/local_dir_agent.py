import agent_common
import os

from autogen_core.base import MessageContext
from autogen_core.components import RoutedAgent, message_handler
from autogen_core.components.models import ChatCompletionClient, SystemMessage, UserMessage

class LocalDirAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(agent_common.AGENT_LOCAL_FILE)
        self._system_messages = [SystemMessage("You are a helpful AI assistant.")]
        self._model_client = model_client

    @message_handler
    async def handle_user_message(self, message: agent_common.Message, ctx: MessageContext) -> agent_common.Message:

        # get dir contents
        files = os.listdir('/')
        context = ""
        for file in files:
            context += f"FilePath: {file}\n"

        # Prepare input to the chat completion model.
        message = message.content + "\nContext:\n" + context
        user_message = UserMessage(content=message, source="user")
        response = await self._model_client.create(
            self._system_messages + [user_message], cancellation_token=ctx.cancellation_token
        )
        # Return with the model's response.
        assert isinstance(response.content, str)
        return agent_common.Message(content=response.content)
