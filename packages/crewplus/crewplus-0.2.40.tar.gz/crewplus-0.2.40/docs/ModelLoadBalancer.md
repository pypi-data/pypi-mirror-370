# ModelLoadBalancer Documentation

## 1. Introduction

The `ModelLoadBalancer` is a utility class designed to manage and provide access to various language models from different providers, such as Azure OpenAI and Google GenAI. It loads model configurations from a JSON file and allows you to retrieve specific models by their deployment name or a combination of provider and type.

### Key Features:
- **Centralized Model Management**: Manage all your model configurations in a single JSON file.
- **On-demand Model Loading**: Models are instantiated and loaded when requested.
- **Provider Agnostic**: Supports multiple model providers.
- **Flexible Retrieval**: Get models by a unique deployment name.

## 2. Initialization

To use the `ModelLoadBalancer`, you need to initialize it with the path to your model configuration file.

```python
from crewplus.services.model_load_balancer import ModelLoadBalancer

# Initialize the balancer with the path to your config file
config_path = "tests/models_config.json" # Adjust the path as needed
balancer = ModelLoadBalancer(config_path=config_path)

# Load the configurations and instantiate the models
balancer.load_config()
```

## 3. Configuration File

The `ModelLoadBalancer` uses a JSON file to configure the available models. Here is an example of what the configuration file looks like. The `deployment_name` is used to retrieve a specific model.

```json
{
    "models": [
        {
            "id": 3,
            "provider": "azure-openai",
            "type": "inference",
            "deployment_name": "gpt-4.1",
            "api_version": "2025-01-01-preview",
            "api_base": "https://crewplus-eastus2.openai.azure.com",
            "api_key": "your-api-key"
        },
        {
            "id": 7,
            "provider": "google-genai",
            "type": "inference",
            "deployment_name": "gemini-2.5-flash",
            "api_key": "your-google-api-key"
        },
        {
            "id": 8,
            "provider": "google-genai",
            "type": "ingestion",
            "deployment_name": "gemini-2.5-pro",
            "api_key": "your-google-api-key"
        }
    ]
}
```

## 4. Getting a Model

You can retrieve a model instance using the `get_model` method and passing the `deployment_name`.

### Get `gemini-2.5-flash`
```python
gemini_flash_model = balancer.get_model(deployment_name="gemini-2.5-flash")

# Now you can use the model
# from langchain_core.messages import HumanMessage
# response = gemini_flash_model.invoke([HumanMessage(content="Hello!")])
# print(response.content)
```

### Get `gemini-2.5-pro`
```python
gemini_pro_model = balancer.get_model(deployment_name="gemini-2.5-pro")
```

### Get `gpt-4.1`
```python
gpt41_model = balancer.get_model(deployment_name="gpt-4.1")
```

### Get `o3mini`
The model `o3mini` is identified by the deployment name `gpt-o3mini-eastus2-RPM25`.
```python
o3mini_model = balancer.get_model(deployment_name="gpt-o3mini-eastus2-RPM25")
```

## 5. Global Access with `init_load_balancer`

The `init_load_balancer` function provides a convenient singleton pattern for accessing the `ModelLoadBalancer` throughout your application without passing the instance around.

First, you initialize the balancer once at the start of your application.

### Initialization

You can initialize it in several ways:

**1. Default Initialization**

This will look for the `MODEL_CONFIG_PATH` environment variable, or use the default path `_config/models_config.json`.

```python
from crewplus.services.init_services import init_load_balancer

init_load_balancer()
```

**2. Initialization with a Custom Path**

You can also provide a direct path to your configuration file.

```python
from crewplus.services.init_services import init_load_balancer

init_load_balancer(config_path="path/to/your/models_config.json")
```

### Getting the Balancer and Models

Once initialized, you can retrieve the `ModelLoadBalancer` instance from anywhere in your code using `get_model_balancer`.

```python
from crewplus.services.init_services import get_model_balancer

# Get the balancer instance
balancer = get_model_balancer()

# Get a model by deployment name
gemini_flash_model = balancer.get_model(deployment_name="gemini-2.5-flash")
```
