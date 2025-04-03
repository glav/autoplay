from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

import config

class SimpleAgent():
    def __init__(self, name="pirate", instructions="You are a helpful assistant that answers any query imitating a pirate."):
        self.project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=config.AZURE_AI_FOUNDRY_CONNECTION_STRING,
        )
        self.thread = None
        self.agent = None
        self.name = name
        self.instructions = instructions

    async def setup(self):
        print("Setting up agent")
        self.agent = self.project_client.agents.create_agent(
            model="gpt-4o-mini",
            name=self.name,
            instructions=self.instructions,
            headers={"x-ms-enable-preview": "true"}
        )
        print(f"Created agent, ID: {self.agent.id}")

        # Create thread for communication
        self.thread = self.project_client.agents.create_thread()
        print(f"Created thread, ID: {self.thread.id}")

        application_insights_connection_string = self.project_client.telemetry.get_connection_string()
        if not application_insights_connection_string:
            print("Application Insights was not enabled for this project.")
            print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
            exit()
        else:
            configure_azure_monitor(connection_string=application_insights_connection_string)
            print("Application Insights was enabled for this project.")


    async def submit_query(self, query: str) -> str:
        if (not self.agent) or (not self.thread):
            await self.setup()
        #with self.project_client:

        # Create message to thread
        message = self.project_client.agents.create_message(
            thread_id=self.thread.id,
            role="user",
            content=query,
        )
        print(f"SMS: {message}")
        # Create and process agent run in thread with tools
        run = self.project_client.agents.create_and_process_run(thread_id=self.thread.id, agent_id=self.agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")


        # Fetch and log all messages
        messages = self.project_client.agents.list_messages(thread_id=self.thread.id)
        #print("Messages:"+ messages["data"][0]["content"][0]["text"]["value"])
        return messages["data"][0]["content"][0]["text"]["value"]

    async def clean_up(self):
        self.project_client.agents.delete_agent(self.agent.id)
        print("Deleted agent")


