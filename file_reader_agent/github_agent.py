import agent_common
import config
from autogen_core.base import MessageContext
from autogen_core import RoutedAgent, message_handler, type_subscription
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage
from githubreader.githubreader import GithubReader
from githubreader.githubrepo import GithubRepo
from githubreader.githubreporeader import GithubRepoReader
import logging
from autogen_core import DefaultTopicId, RoutedAgent, default_subscription, message_handler

#@type_subscription(topic_type=agent_common.AGENT_TOPIC_GITHUB)
#@default_subscription
@type_subscription(topic_type=agent_common.AGENT_TOPIC_GITHUB)
class GithubAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient, logger: logging.Logger) -> None:
        super().__init__(agent_common.AGENT_GITHUB)
        self._system_messages = [SystemMessage(content="You are a helpful AI assistant.", source="system")]
        self._model_client = model_client
        self._logger = logger

    @message_handler
    async def handle_user_message(self, message: agent_common.AgentMessage, ctx: MessageContext) -> agent_common.GithubMessage:
        if not config.GITHUB_TOKEN:
            raise ValueError("No GITHUB_TOKEN defined in the environment.")

        github_reader = await GithubReader.create(config.GITHUB_TOKEN, config.GITHUB_ORG)
        repo = GithubRepo(config.GITHUB_REPONAME)
        repo_reader = await GithubRepoReader.create(github_reader.org_to_use, github_reader.user, repo)

        # Get the repo contents as context
        repo_contents = await repo_reader.get_repo_contents_async()
        context = ""
        for file in repo_contents:
            context += f"FilePath: {file.name}\n"
            #print(f"File: {file.name}")

        # Prepare input to the chat completion model.
        message = message.content + "\nContext:\n" + context
        user_message = UserMessage(content=message, source="user")
        response = await self._model_client.create(
            self._system_messages + [user_message], cancellation_token=ctx.cancellation_token
        )

        self._logger.info(f"GithubAgent response: {response.content}")
        print(response.content)
        # Return with the model's response.
        assert isinstance(response.content, str)
        return agent_common.GithubMessage(content=response.content)
