from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
import logging
from autogen_core import TRACE_LOGGER_NAME
import config
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from simple_agent import SimpleAgent

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

simple_agent = SimpleAgent(name="pirate", instructions="You are a helpful assistant that answers any query imitating a pirate.")
dumb_agent = SimpleAgent(name="doofus", instructions="You are a helpful assistant that answers any query imitating a dumb person.")

async def setup_agents():
  await simple_agent.setup()
  await dumb_agent.setup()

pirate_agent = AssistantAgent(
  name="pirate",
  description="You are a helpful assistant that answers any query imitating a pirate.",
  model_client=chatCompletionClient,
  tools=[simple_agent.submit_query],
  system_message="""You are a helpful assistant that answers any query imitating a pirate""")
                  # If you have provided a sufficient answer to a question about github repository files, you can respond with TERMINATE
                  # to end the conversation.""") # Important: If you do not provide this instruction to terminate, the agents will continue trying to converse and answer questions.

chatty_agent = AssistantAgent(
  name="Doofus",
  description="You are a helpful assistant that answers any query imitating a dumb person..",
  model_client=chatCompletionClient,
  tools=[dumb_agent.submit_query],
  system_message="""You are a helpful assistant that answers any query imitating a dumb person..""")
                  # If you have provided a sufficient answer to a question about github repository files, you can respond with TERMINATE
                  # to end the conversation.""") # Important: If you do not provide this instruction to terminate, the agents will continue trying to converse and answer questions.

text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=8)
termination = text_mention_termination | max_messages_termination

team = SelectorGroupChat(
  [pirate_agent, chatty_agent],
  model_client=chatCompletionClient,
  termination_condition=termination,
)

