import agent_common
from local_dir_agent_tool import get_local_disk_files
from github_agent_tool import get_repository_files
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
import logging
from autogen_core import TRACE_LOGGER_NAME
import config
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat

if not config.ENABLE_TRACE_LOGGING:
  logging.basicConfig(level=logging.FATAL)  # Always have root logger set to FATAL
  logger = logging.getLogger(TRACE_LOGGER_NAME)
  logger.disabled = True
else:
  logging.basicConfig(level=config.LOG_LEVEL)  # Always have root logger set to FATAL
  logger = logging.getLogger(TRACE_LOGGER_NAME)
  logger.setLevel(config.LOG_LEVEL)


chatCompletionClient = AzureOpenAIChatCompletionClient(model="gpt-4o",
                #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
                #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
                #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
                model_capabilities={
                  "vision": False,
                  "function_calling": True,
                  "json_output": False,
              })

ghAgent = AssistantAgent(
  name=agent_common.AGENT_GITHUB,
  description="This agent helps with Github repository related tasks only and files within the repository.",
  model_client=chatCompletionClient,
  tools=[get_repository_files],
  system_message="""You are an agent that uses tools to solve tasks related to the files within Github repositories.
                  You do not answer questions to anything apart from files within github repositories.""")
                  # If you have provided a sufficient answer to a question about github repository files, you can respond with TERMINATE
                  # to end the conversation.""") # Important: If you do not provide this instruction to terminate, the agents will continue trying to converse and answer questions.


ldAgent = AssistantAgent(
  name=agent_common.AGENT_TOPIC_LOCALDIR,
  description="This agent helps with local disk related tasks and files.",
  model_client=chatCompletionClient,
  tools=[get_local_disk_files],
  system_message="""You are an agent that uses tools to solve tasks related to files on local disks.
              You do not solve tasks or answer questions for anything apart from files on a local disk.""")

evalAgent = AssistantAgent(
  name="EvaluationAgent",
  description="This agent evaluates the responses from other agents to determine if the answer supplied is sufficient to answer the  query",
  model_client=chatCompletionClient,
  #tools=[get_local_disk_files],
  system_message="""You are an agent that ensures that answers from other agents are sufficient to answer the query.
              You do not solve tasks or answer questions about the users query.
              You must ensure that the answer from another agent is correct and fully answers the query.
              If you believe the answer from an agent is correct and answers the query, you can respond with TERMINATE""")

text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination

team = SelectorGroupChat(
  [ghAgent, ldAgent, evalAgent],
  model_client=chatCompletionClient,
  termination_condition=termination,
)
