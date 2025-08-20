# CrewPlus

[![PyPI version](https://badge.fury.io/py/crewplus.svg)](https://badge.fury.io/py/crewplus)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/crewplus.svg)](https://pypi.org/project/crewplus)
[![Build Status](https://img.shields.io/travis/com/your-org/crewplus-base.svg)](https://travis-ci.com/your-org/crewplus-base)

**CrewPlus** provides the foundational services and core components for building advanced AI applications. It is the heart of the CrewPlus ecosystem, designed for scalability, extensibility, and seamless integration.

## Overview

This repository, `crewplus-base`, contains the core `crewplus` Python package. It includes essential building blocks for interacting with large language models, managing vector databases, and handling application configuration. Whether you are building a simple chatbot or a complex multi-agent system, CrewPlus offers the robust foundation you need.

## The CrewPlus Ecosystem

CrewPlus is designed as a modular and extensible ecosystem of packages. This allows you to adopt only the components you need for your specific use case.

-   **`crewplus` (This package):** The core package containing foundational services for chat, model load balancing, and vector stores.
-   **`crewplus-agent`:** crewplus agent core: agentic task planner and executor, with context-aware memory.
-   **`crewplus-ingestion`:** Provides robust pipelines for knowledge ingestion and data processing.
-   **`crewplus-memory`:** Provides agent memory services for Crewplus AI Agents.
-   **`crewplus-integrations`:** A collection of third-party integrations to connect CrewPlus with other services and platforms.

## Features

-   **Chat Services:** A unified interface for interacting with various chat models (e.g., `GeminiChatModel`, `TracedAzureChatOpenAI`).
-   **Model Load Balancer:** Intelligently distribute requests across multiple LLM endpoints.
-   **Vector DB Services:** working with popular vector stores (e.g. Milvus, Zilliz Cloud) for retrieval-augmented generation (RAG) and agent memory.
-   **Observability & Tracing:** Automatic integration with tracing tools like Langfuse, with an extensible design for adding others (e.g., Helicone, ...).


## Documentation

For detailed guides and API references, please see the `docs/` folder.

-   **[GeminiChatModel Documentation](./docs/GeminiChatModel.md)**: A comprehensive guide to using the `GeminiChatModel` for text, image, and video understanding.

## Installation

To install the core `crewplus` package, run the following command:

```bash
pip install crewplus
```

## Getting Started

Here is a simple example of how to use the `GeminiChatModel` to start a conversation with an AI model.

```python
# main.py
from crewplus.services import GeminiChatModel

# Initialize the llm (API keys are typically handled by the configuration module)
llm = GeminiChatModel(google_api_key="your-google-api-key")

# Start a conversation
response = llm.chat("Hello, what is CrewPlus?")

print(response)
```

## Project Structure

The `crewplus-base` repository is organized to separate core logic, tests, and documentation. 

```
crewplus-base/                    # GitHub repo name
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── crewplus/                 # PyPI package name
│   └──  __init__.py
│   └──  services/
│       └──  __init__.py
│       └──  gemini_chat_model.py
│       └──  azure_chat_model.py
│       └──  model_load_balancer.py
│       └──  tracing_manager.py
│       └──  ...
│   └──  vectorstores/milvus
│       └──  __init__.py
│       └──  schema_milvus.py
│       └──  vdb_service.py
│   └──  utils/
│       └──  __init__.py
│       └──  schema_action.py
│       └──  ...
├── tests/
│   └── ...
├── docs/
│   └── ...
└── notebooks/
    └── ...

```

## Deploy to PyPI

Clean Previous Build Artifacts:
Remove the dist/, build/, and *.egg-info/ directories to ensure that no old files are included in the new build.

rm -rf dist build *.egg-info

# install deployment tool
pip install twine

# build package
python -m build

# deploy to TestPyPI (Test first)
python -m twine upload --repository testpypi dist/*

# install from TestPyPI 
pip install -i https://test.pypi.org/simple/ crewplus

# Deploy to official PyPI
python -m twine upload dist/*
