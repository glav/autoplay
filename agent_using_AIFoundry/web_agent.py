from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import BingGroundingTool
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import config

#token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
az_model_client = AzureOpenAIChatCompletionClient(
    #azure_deployment="gpt-4o-mini",
    api_version="2024-08-01-preview",
    model = "gpt-4o-mini",
    #azure_endpoint="Your AOAI endpoint",
    #azure_ad_token_provider=token_provider,  # Optional if you choose key-based authentication.
    # api_key="sk-...", # For key-based authentication.
)
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=config.AZURE_AI_FOUNDRY_CONNECTION_STRING,
)
bing_connection = project_client.connections.get(
    connection_name='glav-bing-search'
)

conn_id = bing_connection.id
async def web_ai_agent(query: str) -> str:
    print("This is Bing for Azure AI Agent Service .......")
    bing = BingGroundingTool(connection_id=conn_id)
    with project_client:
        agent = project_client.agents.create_agent(
            model="gpt-4",
            name="my-assistant",
            instructions="""
                You are a web search agent.
                Your only tool is search_tool - use it to find information.
                You make only one search call at a time.
                Once you have the results, you never do calculations based on them.
            """,
            tools=bing.definitions,
            headers={"x-ms-enable-preview": "true"}
        )
        print(f"Created agent, ID: {agent.id}")

        # Create thread for communication
        thread = project_client.agents.create_thread()
        print(f"Created thread, ID: {thread.id}")

        # Create message to thread
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=query,
        )
        print(f"SMS: {message}")
        # Create and process agent run in thread with tools
        run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Delete the assistant when done
        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        # Fetch and log all messages
        messages = project_client.agents.list_messages(thread_id=thread.id)
        print("Messages:"+ messages["data"][0]["content"][0]["text"]["value"])
    return messages["data"][0]["content"][0]["text"]["value"]
