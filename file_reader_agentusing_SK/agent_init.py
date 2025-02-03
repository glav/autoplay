import asyncio

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

import agent_common
from local_dir_agent import LocalDirAgent
from github_agent import GithubAgent
import logging

import config

loggerName = "kernel"
async def setup_kernel():
  kernel = Kernel()

    # Add Azure OpenAI chat completion
  chat_completion = AzureChatCompletion(
        deployment_name="your_models_deployment_name",
        api_key="your_api_key",
        base_url="your_base_url",
    )
  kernel.add_service(chat_completion)

    # Set the logging level for  semantic_kernel.kernel to DEBUG.
  if not config.ENABLE_TRACE_LOGGING:
    logging.basicConfig(level=logging.FATAL)  # Always have root logger set to FATAL
    logger = logging.getLogger(loggerName)
    logger.disabled = True
  else:
    logging.basicConfig(level=config.LOG_LEVEL)  # Always have root logger set to FATAL
    logger = logging.getLogger(loggerName)
    logger.setLevel(config.LOG_LEVEL)

  # Enable planning
  execution_settings = AzureChatPromptExecutionSettings()
  execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

  # Create a history of the conversation
  history = ChatHistory()

  return kernel, execution_settings, history

async def register_agents(runtime1, runtime2, runtime3):

  # await GithubAgent.register(
  #     runtime1,
  #     agent_common.AGENT_GITHUB,
  #     lambda: GithubAgent(
  #       AzureOpenAIChatCompletionClient(model="gpt-4o",
  #                 #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
  #                 #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
  #                 #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
  #                 model_capabilities={
  #                   "vision": False,
  #                   "function_calling": True,
  #                   "json_output": False,
  #               }),
  #               logger=logger,
  #         ),
  # )
  # await LocalDirAgent.register(
  #     runtime2,
  #     agent_common.AGENT_LOCAL_FILE,
  #     lambda: LocalDirAgent(
  #       AzureOpenAIChatCompletionClient(model="gpt-4o",
  #                 #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
  #                 #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
  #                 #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
  #                 model_capabilities={
  #                   "vision": False,
  #                   "function_calling": True,
  #                   "json_output": False,
  #               }),
  #               logger=logger,
  #         ),
  # )
  # await RouterAgent.register(
  #     runtime3,
  #     agent_common.AGENT_ROUTER,
  #     lambda: RouterAgent(
  #       AzureOpenAIChatCompletionClient(model="gpt-4o",
  #                 #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
  #                 #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
  #                 #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
  #                 model_capabilities={
  #                   "vision": False,
  #                   "function_calling": True,
  #                   "json_output": False,
  #               }),
  #               logger=logger,
  #         ),
  # )
