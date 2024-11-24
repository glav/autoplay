import agent_common
from local_dir_agent import LocalDirAgent
from github_agent import GithubAgent
from autogen_ext.models import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from router_agent import RouterAgent


async def register_agents(runtime):
  await GithubAgent.register(
      runtime,
      agent_common.AGENT_GITHIB,
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
          ),
  )
  await LocalDirAgent.register(
      runtime,
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
          ),
  )
  await RouterAgent.register(
      runtime,
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
          ),
  )
