
### Files

- **basic/basic.py**: Contains an asynchronous function to get weather information and an agent setup to query weather using Azure OpenAI.
- **simple_agent/*.py: Code to execute a simple agent co-ordinating using a simple runtime.
- **list-openai-models.py**: Lists available OpenAI models using the OpenAI API.
- **requirements.txt**: Lists the Python dependencies required for the project.

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


