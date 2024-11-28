import agent_common
from local_dir_agent import LocalDirAgent
from github_agent import GithubAgent
from autogen_ext.models import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from router_agent import RouterAgent
import logging
from autogen_core.application.logging import TRACE_LOGGER_NAME
import config

async def register_agents(runtime1, runtime2, runtime3):

  if not config.ENABLE_TRACE_LOGGING:
    logging.basicConfig(level=logging.FATAL)  # Always have root logger set to FATAL
    logger = logging.getLogger(TRACE_LOGGER_NAME)
    logger.disabled = True
  else:
    logging.basicConfig(level=config.LOG_LEVEL)  # Always have root logger set to FATAL
    logger = logging.getLogger(TRACE_LOGGER_NAME)


  await GithubAgent.register(
      runtime1,
      agent_common.AGENT_GITHUB,
      lambda: GithubAgent(
        AzureOpenAIChatCompletionClient(model="gpt-4o",
                  #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
                  #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
                  #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
                  model_capabilities={
                    "vision": False,
                    "function_calling": True,
                    "json_output": False,
                }),
                logger=logger,
          ),
  )
  await LocalDirAgent.register(
      runtime2,
      agent_common.AGENT_LOCAL_FILE,
      lambda: LocalDirAgent(
        AzureOpenAIChatCompletionClient(model="gpt-4o",
                  #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
                  #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
                  #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
                  model_capabilities={
                    "vision": False,
                    "function_calling": True,
                    "json_output": False,
                }),
                logger=logger,
          ),
  )
  await RouterAgent.register(
      runtime3,
      agent_common.AGENT_ROUTER,
      lambda: RouterAgent(
        AzureOpenAIChatCompletionClient(model="gpt-4o",
                  #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
                  #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
                  #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
                  model_capabilities={
                    "vision": False,
                    "function_calling": True,
                    "json_output": False,
                }),
                logger=logger,
          ),
  )
