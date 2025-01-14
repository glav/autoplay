import agent_common
from local_dir_agent_tool import get_local_disk_files
from github_agent_tool import get_repository_files
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from router_agent import RouterAgent
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
  description="This agent helps with Github repository related tasks only. This agent will only answer questions related to files within Github repositories.",
  model_client=chatCompletionClient,
  tools=[get_repository_files],
  system_message="You are aan agent that uses tools to solve tasks related to the files within Github repositories. Yoo do not answer questions to anything apart from files within github repositories.")

ldAgent = AssistantAgent(
  name=agent_common.AGENT_TOPIC_LOCALDIR,
  description="This agent helps with local disk related tasks. This agent will only answer questions related to files on local disks.",
  model_client=chatCompletionClient,
  tools=[get_local_disk_files],
  system_message="You are a an agent that uses tools to solve tasks related to files on local disks. You do not solve tasks or answer questions for anything apart from files on a local disk.")

text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination

team = SelectorGroupChat(
  [ghAgent, ldAgent],
  model_client=chatCompletionClient,
  termination_condition=termination,
)
