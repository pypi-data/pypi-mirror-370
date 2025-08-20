import json
import random
import logging
import threading
from typing import Dict, List, Optional, Union
from collections import defaultdict
from langchain_openai import ChatOpenAI, AzureOpenAIEmbeddings
from .gemini_chat_model import GeminiChatModel
from .azure_chat_model import TracedAzureChatOpenAI


class ModelLoadBalancer:
    def __init__(self,
                 config_path: Optional[str] = "config/models_config.json",
                 config_data: Optional[Dict] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initializes the ModelLoadBalancer.

        Args:
            config_path: Path to the JSON configuration file.
            config_data: A dictionary containing the model configuration.
            logger: An optional logger instance. If not provided, a default one is created.

        Raises:
            ValueError: If neither config_path nor config_data is provided.
        """
        if not config_path and not config_data:
            raise ValueError("Either 'config_path' or 'config_data' must be provided.")

        self.config_path = config_path
        self.config_data = config_data
        self.logger = logger or logging.getLogger(__name__)
        self.models_config: List[Dict] = []
        self.thread_local = threading.local()
        self._initialize_state()
        self._config_loaded = False  # Flag to check if config is loaded

    def load_config(self):
        """Load and validate model configurations from a file path or a dictionary."""
        self.logger.debug("Model balancer: loading configuration.")
        try:
            config = None
            if self.config_data:
                config = self.config_data
            elif self.config_path:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            else:
                # This case is handled in __init__, but as a safeguard:
                raise RuntimeError("No configuration source provided (path or data).")

            # Validate config
            if 'models' not in config or not isinstance(config['models'], list):
                raise ValueError("Configuration must contain a 'models' list.")

            for model in config.get('models', []):
                if 'provider' not in model or 'type' not in model or 'id' not in model:
                    self.logger.error("Model config must contain 'id', 'provider', and 'type' fields.")
                    raise ValueError("Model config must contain 'id', 'provider', and 'type' fields.")

            self.models_config = config['models']

            self._config_loaded = True
            self.logger.debug("Model balancer: configuration loaded successfully.")
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            self._config_loaded = False
            self.logger.error(f"Failed to load model configuration: {e}", exc_info=True)
            raise RuntimeError(f"Failed to load model configuration: {e}")

    def get_model(self, provider: str = None, model_type: str = None, deployment_name: str = None, with_metadata: bool = False, selection_strategy: str = 'random'):
        """
        Get a model instance.

        Can fetch a model in two ways:
        1. By its specific `deployment_name`.
        2. By `provider` and `model_type`, which will select a model using a specified strategy.

        Args:
            provider: The model provider (e.g., 'azure-openai', 'google-genai').
            model_type: The type of model (e.g., 'inference', 'embedding', 'embedding-large').
            deployment_name: The unique name for the model deployment.
            with_metadata: If True, returns a tuple of (model, deployment_name).
            selection_strategy: The selection strategy ('random', 'round_robin', or 'least_used'). Defaults to 'random'.

        Returns:
            An instantiated language model object, or a tuple if with_metadata is True.

        Raises:
            RuntimeError: If the model configuration has not been loaded.
            ValueError: If the requested model cannot be found or if parameters are insufficient.
        """
        if not self._config_loaded:
            self.logger.error("Model configuration not loaded")
            raise RuntimeError("Model configuration not loaded")

        if deployment_name:
            for model_config in self.models_config:
                if model_config.get('deployment_name') == deployment_name:
                    model = self._get_or_create_model(model_config)
                    if with_metadata:
                        return model, deployment_name
                    return model
                
            self.logger.error(f"No model found for deployment name: {deployment_name}")
            raise ValueError(f"No model found for deployment name: {deployment_name}")

        if provider and model_type:
            candidates = [model for model in self.models_config if model.get('provider') == provider and model.get('type') == model_type]
            if not candidates:
                self.logger.error(f"No models found for provider '{provider}' and type '{model_type}'")
                raise ValueError(f"No models found for provider '{provider}' and type '{model_type}'")

            if selection_strategy == 'random':
                selected_model_config = self._random_selection(candidates)
            elif selection_strategy == 'round_robin':
                selected_model_config = self._round_robin_selection(candidates)
            elif selection_strategy == 'least_used':
                selected_model_config = self._least_used_selection(candidates)
            else:
                self.logger.warning(f"Unsupported selection strategy: '{selection_strategy}'. Defaulting to 'random'.")
                selected_model_config = self._random_selection(candidates)
                
            model = self._get_or_create_model(selected_model_config)
            if with_metadata:
                return model, selected_model_config.get('deployment_name')
            return model

        raise ValueError("Either 'deployment_name' or both 'provider' and 'model_type' must be provided.")

    def _get_thread_local_models_cache(self) -> Dict:
        """Gets the model cache for the current thread, creating it if it doesn't exist."""
        if not hasattr(self.thread_local, 'models_cache'):
            self.thread_local.models_cache = {}
        return self.thread_local.models_cache

    def _get_or_create_model(self, model_config: Dict):
        """
        Gets a model instance from the thread-local cache. If it doesn't exist,
        it instantiates, caches, and returns it.
        """
        model_id = model_config['id']
        models_cache = self._get_thread_local_models_cache()

        if model_id not in models_cache:
            self.logger.debug(f"Creating new model instance for id {model_id} in thread {threading.get_ident()}")
            models_cache[model_id] = self._instantiate_model(model_config)
        
        return models_cache[model_id]

    def _instantiate_model(self, model_config: Dict):
        """Instantiate and return an LLM object based on the model configuration"""
        provider = model_config['provider']
        self.logger.debug(f"Model balancer: instantiating {provider} -- {model_config.get('deployment_name')}")

        if provider == 'azure-openai':
            kwargs = {
                'azure_deployment': model_config['deployment_name'],
                'openai_api_version': model_config['api_version'],
                'azure_endpoint': model_config['api_base'],
                'openai_api_key': model_config['api_key']
            }
            if 'temperature' in model_config:
                kwargs['temperature'] = model_config['temperature']
            if model_config.get('deployment_name') == 'o1-mini':
                kwargs['disable_streaming'] = True
            return TracedAzureChatOpenAI(**kwargs)
        elif provider == 'openai':
            kwargs = {
                'openai_api_key': model_config['api_key']
            }
            if 'temperature' in model_config:
                kwargs['temperature'] = model_config['temperature']
            return ChatOpenAI(**kwargs)
        elif provider == 'azure-openai-embeddings':
            try:
                emb_kwargs = dict(
                    model=model_config['model_name'],
                    azure_deployment=model_config['deployment_name'],
                    openai_api_version=model_config['api_version'],
                    api_key=model_config['api_key'],
                    azure_endpoint=model_config['api_base'],
                    chunk_size=16, request_timeout=60, max_retries=2
                )
                if 'dimensions' in model_config:
                    emb_kwargs['dimensions'] = model_config['dimensions']
                return AzureOpenAIEmbeddings(**emb_kwargs)
            except Exception as e:
                self.logger.error(f"Failed to instantiate AzureOpenAIEmbeddings: {e}")
                return None
        elif provider == 'google-genai':
            kwargs = {
                'google_api_key': model_config['api_key'],
                'model_name': model_config['deployment_name']  # Map deployment_name to model_name
            }
            if 'temperature' in model_config:
                kwargs['temperature'] = model_config['temperature']
            if 'max_tokens' in model_config:
                kwargs['max_tokens'] = model_config['max_tokens']
            return GeminiChatModel(**kwargs)
        elif provider == 'vertex-ai':
            deployment_name = model_config['deployment_name']
            
            # Handle the 'model_name@location' format for deployment_name
            model_name_for_gemini = deployment_name.split('@')[0] if '@' in deployment_name else deployment_name

            kwargs = {
                'use_vertex_ai': True,
                'model_name': model_name_for_gemini,
                'project_id': model_config['project_id'],
                'location': model_config['location'],
            }
            if 'service_account_file' in model_config:
                kwargs['service_account_file'] = model_config['service_account_file']
            if 'temperature' in model_config:
                kwargs['temperature'] = model_config['temperature']
            if 'max_tokens' in model_config:
                kwargs['max_tokens'] = model_config['max_tokens']
            return GeminiChatModel(**kwargs)
        else:
            self.logger.error(f"Unsupported provider: {provider}")
            raise ValueError(f"Unsupported provider: {provider}")

    def _initialize_state(self):
        self.active_models = []
        self.usage_counter = defaultdict(int)
        self.current_indices = {}

    def _random_selection(self, candidates: list) -> Dict:
        """Selects a model randomly from a list of candidates."""
        model = random.choice(candidates)
        self.usage_counter[model['id']] += 1
        return model

    def _round_robin_selection(self, candidates: list) -> Dict:
        if id(candidates) not in self.current_indices:
            self.current_indices[id(candidates)] = 0
        idx = self.current_indices[id(candidates)]
        model = candidates[idx]
        self.current_indices[id(candidates)] = (idx + 1) % len(candidates)
        self.usage_counter[model['id']] += 1

        return model

    def _least_used_selection(self, candidates: list) -> Dict:
        min_usage = min(self.usage_counter[m['id']] for m in candidates)
        least_used = [m for m in candidates if self.usage_counter[m['id']] == min_usage]
        model = random.choice(least_used)
        self.usage_counter[model['id']] += 1
        return model
