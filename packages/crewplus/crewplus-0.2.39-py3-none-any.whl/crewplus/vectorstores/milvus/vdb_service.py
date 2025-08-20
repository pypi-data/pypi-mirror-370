# -*- coding: utf-8 -*-
# @Author: Cursor
# @Date: 2025-02-12
# @Last Modified by: Gemini
# @Last Modified time: 2025-07-04

import logging
from typing import List, Dict, Union, Optional
from langchain_milvus import Milvus
from langchain_core.embeddings import Embeddings
from langchain_openai import AzureOpenAIEmbeddings
from pymilvus import MilvusClient
import time

from ...services.init_services import get_model_balancer
from .schema_milvus import SchemaMilvus, DEFAULT_SCHEMA

class VDBService(object):
    """
    A service to manage connections to Milvus/Zilliz vector databases and embedding models.

    This service centralizes the configuration and instantiation of the Milvus client
    and provides helper methods to get embedding functions and vector store instances.

    Args:
        settings (dict, optional): A dictionary containing configuration for the vector store
                         and embedding models.
        endpoint (str, optional): The URI for the Zilliz cluster. Can be used for simple
                                  initialization instead of `settings`.
        token (str, optional): The token for authenticating with Zilliz. Must be provided
                               with `endpoint`.
        schema (str, optional): The schema definition for a collection. Defaults to None.
        logger (logging.Logger, optional): An optional logger instance. Defaults to None.

    Raises:
        ValueError: If required configurations are missing.
        NotImplementedError: If an unsupported provider is specified.
        RuntimeError: If the MilvusClient fails to initialize after a retry.

    Example:
        >>> # Initialize with a full settings dictionary
        >>> settings = {
        ...     "embedder": {
        ...         "provider": "azure-openai",
        ...         "config": {
        ...             "model": "text-embedding-3-small",
        ...             "api_version": "2023-05-15",
        ...             "api_key": "YOUR_AZURE_OPENAI_KEY",
        ...             "openai_base_url": "YOUR_AZURE_OPENAI_ENDPOINT",
        ...             "embedding_dims": 1536
        ...         }
        ...     },
        ...     "vector_store": {
        ...         "provider": "milvus",
        ...         "config": {
        ...             "host": "localhost",
        ...             "port": 19530,
        ...             "user": "root",
        ...             "password": "password",
        ...             "db_name": "default"
        ...         }
        ...     },
        ...     "index_params": {
        ...         "metric_type": "IP",
        ...         "index_type": "HNSW",
        ...         "params": {}
        ...     }
        ... }
        >>> vdb_service = VDBService(settings=settings)
        >>>
        >>> # Alternatively, initialize with an endpoint and token for Zilliz
        >>> # vdb_service_zilliz = VDBService(endpoint="YOUR_ZILLIZ_ENDPOINT", token="YOUR_ZILLIZ_TOKEN")
        >>>
        >>> # Get the raw Milvus client
        >>> client = vdb_service.get_vector_client()
        >>> print(client.list_collections())
        >>> # Get an embedding function
        >>> embeddings = vdb_service.get_embeddings()
        >>> print(embeddings)
        >>> # Get a LangChain vector store instance (will be cached)
        >>> vector_store = vdb_service.get_vector_store(collection_name="my_collection")
        >>> print(vector_store)
        >>> same_vector_store = vdb_service.get_vector_store(collection_name="my_collection")
        >>> assert vector_store is same_vector_store
    """
    _client: MilvusClient
    _instances: Dict[str, Milvus] = {}

    schema: str
    embedding_function: Embeddings
    index_params: dict
    connection_args: dict
    settings: dict
    
    def __init__(self, settings: dict = None, endpoint: str = None, token: str = None, schema: str = None, logger: logging.Logger = None):
        """
        Initializes the VDBService. 

        Can be initialized in two ways:
        1. By providing a full `settings` dictionary for complex configurations.
        2. By providing `endpoint` and `token` for a direct Zilliz connection.
           Note: When using this method, an `embedder` configuration is not created.
           You must either use the `ModelLoadBalancer` or pass an `Embeddings` object
           directly to methods like `get_vector_store`.
        
        Args:
            settings (dict, optional): Configuration dictionary for the service. Defaults to None.
            endpoint (str, optional): The URI for the Zilliz cluster. Used if `settings` is not provided.
            token (str, optional): The token for authenticating with the Zilliz cluster.
            schema (str, optional): Default schema for new collections. Defaults to None.
            logger (logging.Logger, optional): Logger instance. Defaults to None.
        """
        self.logger = logger or logging.getLogger(__name__)

        if settings:
            self.settings = settings
        elif endpoint and token:
            self.logger.info("Initializing VDBService with endpoint and token for a Zilliz connection.")
            self.settings = {
                "vector_store": {
                    "provider": "zilliz",
                    "config": {
                        "uri": endpoint,
                        "token": token
                    }
                }
            }
        else:
            raise ValueError("VDBService must be initialized with either a 'settings' dictionary or both 'endpoint' and 'token'.")

        vector_store_settings = self.settings.get("vector_store")
        if not vector_store_settings:
            msg = "'vector_store' not found in settings"
            self.logger.error(msg)
            raise ValueError(msg)

        provider = vector_store_settings.get("provider")
        self.connection_args = vector_store_settings.get("config")

        if not provider or not self.connection_args:
            msg = "'provider' or 'config' not found in 'vector_store' settings"
            self.logger.error(msg)
            raise ValueError(msg)

        self._client = self._initialize_milvus_client(provider)

        self.schema = schema
        self.index_params = self.settings.get("index_params")
        
        self.logger.info("VDBService initialized successfully")

    def _initialize_milvus_client(self, provider: str) -> MilvusClient:
        """
        Initializes and returns a MilvusClient with a retry mechanism.
        """
        client_args = {}
        if provider == "milvus":
            host = self.connection_args.get("host", "localhost")
            port = self.connection_args.get("port", 19530)
            
            # Use https for remote hosts, and http for local connections.
            scheme = "https" if host not in ["localhost", "127.0.0.1"] else "http"
            uri = f"{scheme}://{host}:{port}"
            
            client_args = {
                "uri": uri,
                "user": self.connection_args.get("user"),
                "password": self.connection_args.get("password"),
                "db_name": self.connection_args.get("db_name")
            }
            # Filter out None values to use client defaults
            client_args = {k: v for k, v in client_args.items() if v is not None}

        elif provider == "zilliz":
            client_args = self.connection_args
        else:
            self.logger.error(f"Unsupported vector store provider: {provider}")
            raise NotImplementedError(f"Vector store provider '{provider}' is not supported.")

        try:
            # First attempt to connect
            return MilvusClient(**client_args)
        except Exception as e:
            self.logger.error(f"Failed to initialize MilvusClient, trying again. Error: {e}")
            # Second attempt after failure
            try:
                return MilvusClient(**client_args)
            except Exception as e_retry:
                self.logger.error(f"Failed to initialize MilvusClient on retry. Final error: {e_retry}")
                raise RuntimeError(f"Could not initialize MilvusClient after retry: {e_retry}")

    def get_vector_client(self) -> MilvusClient:
        """
        Returns the active MilvusClient instance.

        Returns:
            MilvusClient: The initialized client for interacting with the vector database.
        """
        return self._client

    def get_embeddings(self, from_model_balancer: bool = False, provider: Optional[str] = "azure-openai", model_type: Optional[str] = "embedding-large") -> Embeddings:
        """
        Gets an embedding function, either from the model balancer or directly from settings.

        Args:
            from_model_balancer (bool): If True, uses the central model balancer service.
                                        If False, creates a new instance based on 'embedder' settings.
            model_type (str, optional): The type of model to get from the balancer. Defaults to "embedding-large".

        Returns:
            Embeddings: An instance of a LangChain embedding model.
        """
        if from_model_balancer:
            model_balancer = get_model_balancer()
            return model_balancer.get_model(provider=provider, model_type=model_type)

        embedder_config = self.settings.get("embedder")
        if not embedder_config:
            self.logger.error("'embedder' configuration not found in settings.")
            raise ValueError("'embedder' configuration not found in settings.")

        provider = embedder_config.get("provider")
        config = embedder_config.get("config")

        if not provider or not config:
            self.logger.error("Embedder 'provider' or 'config' not found in settings.")
            raise ValueError("Embedder 'provider' or 'config' not found in settings.")

        if provider == "azure-openai":
            # Map the settings config to AzureOpenAIEmbeddings parameters.
            azure_config = {
                "azure_deployment": config.get("model"),
                "openai_api_version": config.get("api_version"),
                "api_key": config.get("api_key"),
                "azure_endpoint": config.get("openai_base_url"),
                "dimensions": config.get("embedding_dims"),
                "chunk_size": config.get("chunk_size", 16),
                "request_timeout": config.get("request_timeout", 60),
                "max_retries": config.get("max_retries", 2)
            }
            # Filter out None values to use client defaults.
            azure_config = {k: v for k, v in azure_config.items() if v is not None}
            
            return AzureOpenAIEmbeddings(**azure_config)
        else:
            self.logger.error(f"Unsupported embedding provider: {provider}")
            raise NotImplementedError(f"Embedding provider '{provider}' is not supported yet.")
        
    def _ensure_collection_exists(self, collection_name: str, embeddings: Embeddings, check_existence: bool = True):
        """
        Checks if a collection exists and creates it if it doesn't.
        This operation is wrapped in a try-except block to handle potential failures
        during collection creation.
        """
        try:
            client = self.get_vector_client()
            if check_existence and not client.has_collection(collection_name):
                self.logger.info(f"Collection '{collection_name}' does not exist. Creating it.")
                
                schema_milvus = SchemaMilvus(
                    embedding_function=embeddings,
                    collection_name=collection_name,
                    connection_args=self.connection_args,
                    index_params=self.index_params
                )

                schema_to_use = self.schema or DEFAULT_SCHEMA
                if not self.schema:
                    self.logger.warning(f"No schema provided for VDBService. Using DEFAULT_SCHEMA for collection '{collection_name}'.")
                
                schema_milvus.set_schema(schema_to_use)
                
                if not schema_milvus.create_collection():
                    raise RuntimeError(f"SchemaMilvus failed to create collection '{collection_name}'.")
        except Exception as e:
            self.logger.error(f"An error occurred while ensuring collection '{collection_name}' : {e}")
            raise RuntimeError(f"Failed to ensure collection '{collection_name}' .") from e

    def _is_good_connection(self, vdb_instance: Milvus, collection_name: str) -> tuple[bool, bool | None]:
        """
        Checks if the Milvus instance has a good connection by verifying collection existence.
        
        Args:
            vdb_instance (Milvus): The cached vector store instance.
            collection_name (str): The name of the collection to check.

        Returns:
            tuple[bool, bool | None]: A tuple of (is_connected, collection_exists).
                                     collection_exists is None if the connection failed.
        """
        try:
            # Use has_collection as a lightweight way to verify the connection and collection status.
            # If the server is unreachable, this will raise an exception.
            collection_exists = vdb_instance.client.has_collection(collection_name)
            if collection_exists:
                self.logger.debug(f"Connection for cached instance of '{collection_name}' is alive.")
            else:
                self.logger.warning(f"Collection '{collection_name}' not found for cached instance. It may have been dropped.")
            return True, collection_exists
        except Exception as e:
            self.logger.warning(f"Connection check failed for cached instance of '{collection_name}': {e}")
            return False, None

    def get_vector_store(self, collection_name: str, embeddings: Embeddings = None, metric_type: str = "IP") -> Milvus:
        """
        Gets a vector store instance, creating it if it doesn't exist for the collection.
        This method validates both the embedding function and the vector store connection
        before caching the instance to prevent faulty instances from being reused.

        Args:
            collection_name (str): The name of the collection in the vector database.
            embeddings (Embeddings, optional): An embedding model instance. If None, one is created.
            metric_type (str): The distance metric for the index. Defaults to "IP".

        Returns:
            Milvus: LangChain Milvus instance, which is compatible with both Zilliz and Milvus.
        """
        if not collection_name:
            self.logger.error("get_vector_store called with no collection_name.")
            raise ValueError("collection_name must be provided.")

        check_existence = True
        # Check for a cached instance and validate its connection before returning.
        if collection_name in self._instances:
            instance = self._instances[collection_name]
            is_connected, collection_exists = self._is_good_connection(instance, collection_name)
            
            if is_connected and collection_exists:
                self.logger.info(f"Returning existing vector store instance for collection: {collection_name}")
                return instance
            
            self.logger.warning(f"Cached instance for '{collection_name}' is invalid. Removing it from cache.")
            del self._instances[collection_name]
            
            if is_connected and not collection_exists:
                # We know the collection doesn't exist, so no need to check again.
                check_existence = False

        self.logger.info(f"Creating new vector store instance for collection: {collection_name}")
        if embeddings is None:
            embeddings = self.get_embeddings()

        # Ensure the collection exists before proceeding.
        self._ensure_collection_exists(collection_name, embeddings, check_existence=check_existence)

        # 1. Validate the embedding function before proceeding.
        try:
            self.logger.debug(f"Testing embedding function for collection '{collection_name}'...")
            embeddings.embed_query("validation_test_string")
            self.logger.debug("Embedding function is valid.")
        except Exception as e:
            self.logger.error(
                f"The provided embedding function is invalid and failed with error: {e}. "
                f"Cannot create a vector store for collection '{collection_name}'."
            )
            raise RuntimeError(f"Invalid embedding function provided.") from e

        # If embeddings are valid, proceed to create the Milvus instance.
        index_params = self.index_params or {
            "metric_type": metric_type,
            "index_type": "AUTOINDEX",
            "params": {}
        }
        
        vdb = self._create_milvus_instance_with_retry(
            collection_name=collection_name,
            embeddings=embeddings,
            index_params=index_params
        )

        # Cache the newly created instance.
        self._instances[collection_name] = vdb

        return vdb

    def _create_milvus_instance_with_retry(self, collection_name: str, embeddings: Embeddings, index_params: dict) -> Milvus:
        """
        Creates a Milvus instance with a retry mechanism for connection failures.
        """
        retries = 2
        for attempt in range(retries + 1):
            try:
                vdb = Milvus(
                    embedding_function=embeddings,
                    collection_name=collection_name,
                    connection_args=self.connection_args,
                    index_params=index_params
                )
                self.logger.info(f"Successfully connected to Milvus for collection '{collection_name}' on attempt {attempt + 1}.")
                return vdb  # Return on success
            except Exception as e:
                self.logger.warning(
                    f"Attempt {attempt + 1}/{retries + 1} to connect to Milvus for collection '{collection_name}' failed: {e}"
                )
                if attempt < retries:
                    self.logger.info("Retrying in 3 seconds...")
                    time.sleep(3)
                else:
                    self.logger.error(f"Failed to connect to Milvus for collection '{collection_name}' after {retries + 1} attempts.")
                    raise RuntimeError(f"Could not connect to Milvus after {retries + 1} attempts.") from e

    def drop_collection(self, collection_name: str) -> None:
        """
        Deletes a collection from the vector database and removes it from the cache.

        Args:
            collection_name (str): The name of the collection to drop.

        Raises:
            ValueError: If collection_name is not provided.
            RuntimeError: If the operation fails on the database side.
        """
        if not collection_name:
            self.logger.error("drop_collection called without a collection_name.")
            raise ValueError("collection_name must be provided.")

        self.logger.info(f"Attempting to drop collection: {collection_name}")

        try:
            client = self.get_vector_client()
            client.drop_collection(collection_name=collection_name)
            self.logger.info(f"Successfully dropped collection: {collection_name}")
        except Exception as e:
            self.logger.error(f"Failed to drop collection '{collection_name}': {e}")
            raise RuntimeError(f"An error occurred while dropping collection '{collection_name}'.") from e
        finally:
            # Whether successful or not, remove the stale instance from the cache.
            if collection_name in self._instances:
                del self._instances[collection_name]
                self.logger.info(f"Removed '{collection_name}' from instance cache.")

    def delete_data_by_filter(self, collection_name: str = None, filter: str = None) -> None:
        """ Delete data by filter

        Args:
            collection_name (str): collection_name
            filter (str): filter
        """
        self.logger.info(f"Delete data by filter:{filter}")

        try:
            client=self.get_vector_client()
            if collection_name is None or client is None or filter is None:
                return RuntimeError(f"collection_name must be not null or check out your client to link milvus")
            client.delete(collection_name=collection_name, filter=filter)
        except Exception as e:
            raise RuntimeError(f"delete collection data failed: {str(e)}")

    @staticmethod
    def delete_old_indexes(url: str = None, vdb: Milvus = None) -> (bool | None):
        """ Delete old indexes of the same source_url

        Args:
            url (str): source url
            vdb (Milvus): Milvus/Zilliz instance
        """
        # Logging is not performed in static method
        if url is None or vdb is None:
            return None

        # Delete indexes of the same source_url
        expr = f'source_url == "{url}" or source == "{url}"'
        pks = vdb.get_pks(expr)

        # Delete entities by pks
        if pks is not None and len(pks) > 0 :
            res = vdb.delete(pks)
            return res

    @staticmethod
    def delete_old_indexes_by_id(source_id: str = None, vdb: Milvus = None) -> (bool | None):
        """ Delete old indexes of the same source_id

        Args:
            source_id (str): source id
        """
        # Logging is not performed in static method
        if source_id is None or vdb is None:
            return None

        # Delete indexes of the same source_id
        expr = f'source_id == "{source_id}"'
        pks = vdb.get_pks(expr)

        # Delete entities by pks
        if pks is not None and len(pks) > 0 :
            res = vdb.delete(pks)
            return res
        