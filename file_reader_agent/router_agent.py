import agent_common
import os

from autogen_core.base import MessageContext
from autogen_core.components import RoutedAgent, message_handler, type_subscription
from autogen_core.components.models import ChatCompletionClient, SystemMessage, UserMessage

@type_subscription(topic_type=agent_common.AGENT_TOPIC_USER_REQUEST)
class RouterAgent(RoutedAgent):
    # def __init__(self) -> None:
    #     super().__init__(agent_common.AGENT_ROUTER)
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__(agent_common.AGENT_ROUTER)
        self._system_messages = [SystemMessage("You are a helpful AI assistant.")]
        self._model_client = model_client

    @message_handler
    async def handle_user_message(self, message: agent_common.UserRequestMessage, ctx: MessageContext) -> None:

        print(f"RouterAgent received message: {message.content}")

         # Prepare input to the chat completion model.
        message = "Can you determine whether the context is referrinng to a local directory query or a github repository query? If a local directory, then simply reply 'local', if Gitgub then simply reply 'github' otherwise reply 'unknown'\nContext:\n" + message.content
        user_message = UserMessage(content=message, source="user")
        response = await self._model_client.create(
            self._system_messages + [user_message], cancellation_token=ctx.cancellation_token)

        print(f"RouterAgent response: {response.content}")


