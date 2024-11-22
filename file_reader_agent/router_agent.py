import agent_common
import os
import asyncio

from autogen_core.base import MessageContext, TopicId
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
        router_message = "Can you determine whether the context is referrinng to a local directory query or a github repository query? If a local directory, then simply reply 'local', if Gitgub then simply reply 'github' otherwise reply 'unknown'\nContext:\n" + message.content
        user_message = UserMessage(content=router_message, source="user")
        response = await self._model_client.create(
            self._system_messages + [user_message], cancellation_token=ctx.cancellation_token)

        if response.content == "local":
            await self.publish_message(agent_common.LocalDirMessage(content=message.content), topic_id=TopicId(type=agent_common.AGENT_TOPIC_LOCALDIR, source="default"))
        elif response.content == "github":
            await self.publish_message(agent_common.GithubMessage(content=message.content), topic_id=TopicId(type=agent_common.AGENT_TOPIC_GITHUB, source="default"))
        else:
            print("Sorry, I could not determine whether you made a query about the local file system or a Github repository. COuld you rephrase the question.")


        #print(f"RouterAgent response: {response.content}")


