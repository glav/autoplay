
### Files

- **basic/basic.py**: Contains an asynchronous function to get weather information and an agent setup to query weather using Azure OpenAI.
- **simple_agent/*.py**: Code to execute a simple agent co-ordinating using a simple runtime.
- **debug/example.py**: Directly from Autogen site to see a working example
- **file_reader_agent/*.py**: A slightly more complex custom thing with a router agent that selects between local disk operations and a github repository. Execute the `app.py` file to kick it all off. Github requires the following environment vars set:
  - `GITHUB_REPONAME="{repo_name}"`  <-- For example 'Glav.HelperScripts'
  - `GITHUB_TOKEN="{your_github_PAT}"`
- **list-openai-models.py**: Lists available OpenAI models using the OpenAI API.
- **requirements.txt**: Lists the Python dependencies required for the project.

#### Environment Variables
- Look at the `.env-sample` file to see what environment variables are required.
- Copy the `.env-sample` into a `.env` file and populate the variables with valid values.
- The code samples will load the environment vars from this file and use those.

## Setup

1. **Clone the repository**:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Set up the development container**:
    - Ensure you have Docker installed.
    - Open the repository in Visual Studio Code.
    - Use the `Remote - Containers` extension to open the folder in a container.

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - You need to have some environment variables set for this to work.
    - If using Open AI then
    ```sh
    export OPENAI_API_KEY="<your-open-ai-key>"
    ```
    - If using Azure Open AI then
    ```sh
    export AZURE_OPENAI_API_KEY="<your-azure-open-ai-key>"
    export AZURE_OPENAI_ENDPOINT="https://{azure-openai-name}.openai.azure.com"
    export OPENAI_API_VERSION="2024-02-15-preview"
    ```

## Usage

### Get Weather Information

Run the `basic.py` script to invoke the agent to get weather information:

```sh
python basic/basic.py
```

### Simple Agent
Run the `runtime.py` script to invoke the agent to get things to do in Sydney.
Uses runtime and agent concepts.

```sh
python simple_agent/runtime.py
```

### File Reader Agent
Run the `app.py` script to invoke the agent to answer questions about files on disk or files in a Github repo.
Uses runtime, agent concepts, topics for agent messaging, proper logging.

```sh
cd file_reader_agent
python app.py
```
Then ask a question like, "*What is the first file on disk that begins with the letter 'b'?*"
Note: You can easily switch between using a single or distributed runtimes using the following code in `app.py` by commenting and uncommenting the relevant line.
```python
#runtime = SingleRuntimeFacade()
runtime = DistributedRuntimeFacade()
```
Note: When running the application (via `python app.py`), you can then run the `observer_agent.py` in a separate process which simply demonstrates that you can run another agent in a different process and communicate easily.
The `observer_agent.py` will simply listen for messages (sent via topics) and print them out.

#### Telemetry note for File Reader agent
AppInsights telemetry is enabled (albeit a WIP) if the '```APPLICATION_INSIGHTS_CONNECTION_STRING```' env var is set to a valid connection string.

Set the env var  ```OTEL_EXPORTER_OTLP_ENDPOINT=http://host.docker.internal:4318```  # If running Aspire docker container locally

To run the the docker aspire dashboard, execute
```
docker run --rm -it -p 18888:18888 -p 4318:18889 -d --name aspire-dashboard     mcr.microsoft.com/dotnet/aspire-dashboard:9.0
```
Run this outside of devcontainer, dashboard then is accessible on http://localhost:18888

This will require a token, you can get this by examining the logs of the container and looking for the 't' parameter on the Url

eg. ```docker logs {container-id}```
Will see something like 'Login to the dashboard at ```http://localhost:18888/login?t=9583bf2935ee3d3538d54e676984e512``` where *9583bf2935ee3d3538d54e676984e512** is the access token


### File Reader Agent Using SelectorGroupChat
Run the `app.py` script to invoke the agent to answer questions about files on disk or files in a Github repo.
Uses higher level API `SelectorGroupChat` to register agents. This implementation is meant to contrast the implementation and functionality from the low level APIP shown in the `file_reader_agent` example mentioned above.

*Note: In `file_reader_agent_using_SelectorGroupChat/agent_init.py` is where the agents are initialised and where agent interaction termination is setup:
```python
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination
```
The SelectorGroupChat can often go on a long time as agents converse with each other, sometimes on irrelevant conversations so it is important to craft the system prompt and agent descriptions appropriately. You may need to explicitly get an agent to issue a terminate action in certain scenarios to prevent long running conversations.





