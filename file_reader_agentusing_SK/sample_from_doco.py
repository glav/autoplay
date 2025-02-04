import asyncio
from dotenv import load_dotenv
env_loaded = load_dotenv(dotenv_path="../.env", override=True)
print(f"Env variables loaded: {env_loaded}")

import config
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

async def main():
    # Initialize the kernel
    kernel = Kernel()

    service_id = "azure_chat_service"
    # Add Azure OpenAI chat completion
    #chat_completion = AzureChatCompletion(service_id=service_id)
    chat_completion = AzureChatCompletion(service_id=service_id,
        deployment_name=config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
        api_key=config.AZURE_OPENAI_API_KEY,
        base_url=config.AZURE_OPENAI_ENDPOINT,
        #api_version=config.AZURE_OPENAI_API_VERSION

    )
    kernel.add_service(chat_completion)

    # Set the logging level for  semantic_kernel.kernel to DEBUG.
    setup_logging()
    #logging.getLogger("kernel").setLevel(logging.DEBUG)

    # Add a plugin (the LightsPlugin class is defined below)
    # kernel.add_plugin(
    #     LightsPlugin(),
    #     plugin_name="Lights",
    # )

    # Enable planning
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Create a history of the conversation
    history = ChatHistory()

    # Initiate a back-and-forth chat
    userInput = None
    while True:
        # Collect user input
        userInput = input("User > ")

        # Terminate the loop if the user says "exit"
        if userInput == "exit":
            break

        # Add user input to the history
        history.add_user_message(userInput)

        agent = ChatCompletionAgent(service_id=service_id, kernel=kernel, name="chatagent", instructions="You are a helpful AI assistant", execution_settings=execution_settings)
        results = agent.invoke(history=history)

        # Get the response from the AI
        # result = await chat_completion.get_chat_message_content(
        #     chat_history=history,
        #     settings=execution_settings,
        #     kernel=kernel,
        # )

        # Print the results
        async for content in results:
          print(f"# {content.role} - {content.name or '*'}: '{content.content}'")
          #chat.add_message(content)
        #print("Assistant > " + str(result))

        # Add the message from the agent to the chat history
        #history.add_message(result)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
