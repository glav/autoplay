import logging
import asyncio

from autogen_agentchat import EVENT_LOGGER_NAME
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient

# set up logging. You can define your own logger
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.setLevel(logging.INFO)


# define a tool
async def get_weather(city: str) -> str:
    return f"The weather in {city} is 73 degrees and Sunny."


# define an agent
weather_agent = AssistantAgent(
    name="weather_agent",
    model_client=AzureOpenAIChatCompletionClient(model="gpt-4o",
                                                 #api_version='2024-02-15-preview', # set this if you DO NOT have the OPENAI_API_VERSION environment variable set
                                                 #azure_endpoint='https://somename.openai.azure.com', # set this if you DO NOT have the AZURE_OPENAI_ENDPOINT environment variable set
                                                 #api_key="<AZURE_OPENAI_API_KEY>", # set this if you DO NOT have the AZURE_OPENAI_API_KEY environment variable set
                                                 model_capabilities={
                                                    "vision": False,
                                                    "function_calling": True,
                                                    "json_output": False,
                                                }),
    tools=[get_weather],
)

# add the agent to a team
termination = MaxMessageTermination(max_messages=2)
agent_team = RoundRobinGroupChat([weather_agent], termination_condition=termination)

async def main() -> None:
    result = await agent_team.run(task="What is the weather in Sydney?")
    print("\n", result)

asyncio.run(main())
