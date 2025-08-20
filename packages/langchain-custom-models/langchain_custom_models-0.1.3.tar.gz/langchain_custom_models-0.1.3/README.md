# Langchain Custom Models

This repository provides a collection of custom `ChatModel` integrations for `Langchain`, enabling support for various Large Language Model (LLM) service providers. The goal is to offer a unified interface for models that are not yet officially supported by Langchain.

Currently, the following provider is supported:
- **Volcengine Ark**

## Features

- **Seamless Integration**: Drop-in replacement for any Langchain `ChatModel`.
- **Volcengine Ark Support**: Full support for `ChatVolcEngine` to interact with Volcengine's Ark API.
- **Standard Interface**: Works with standard Langchain message types (`SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage`).
- **Tool Binding Support**: Full support for `bind_tools()` method for function calling capabilities.

## Installation

You can install the package directly from this repository:

```bash
pip install git+https://github.com/Hellozaq/langchain-custom-models.git
```

Additionally, ensure you have the Volcengine Ark SDK installed:

```bash
pip install volcengine-python-sdk[ark]
```

## Usage

### ChatVolcEngine

To use the `ChatVolcEngine` model, you need to provide your Volcengine Ark API key. The recommended approach is to use a `.env` file to manage your credentials securely.

**1. Create a `.env` file**

In your project's root directory, create a file named `.env` and add your API key:

```
VOLCANO_API_KEY="your-ark-api-key"
```

**2. Load Credentials and Use the Model**

Now, you can use `dotenv` to load the API key from the `.env` file into your environment.

Here is a basic example:

```python
from dotenv import load_dotenv
from langchain_custom_models import ChatVolcEngine
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables from .env file
load_dotenv()

# Initialize the chat model
# The API key is automatically read from the VOLCANO_API_KEY environment variable.
# Replace 'your-model-id' with the actual model ID from Volcengine Ark, e.g., 'deepseek-v3-250324'
llm = ChatVolcEngine(model="your-model-id")

# Prepare messages
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Hello, who are you?"),
]

# Get a response
response = llm.invoke(messages)

print(response.content)
```

### Parameters

- `model` (str): **Required**. The model ID from Volcengine Ark (e.g., `deepseek-v3-250324`).
- `ark_api_key` (Optional[str]): Your Volcengine Ark API key. If not provided, it will be read from the `VOLCANO_API_KEY` environment variable.
- `max_tokens` (int): The maximum number of tokens to generate. Defaults to `4096`.
- `temperature` (float): Controls the randomness of the output. Defaults to `0.7`.
- `top_p` (float): Nucleus sampling parameter. Defaults to `1.0`.

## Contributing

Contributions are welcome! If you would like to add support for a new LLM provider or improve existing integrations, please feel free to open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
