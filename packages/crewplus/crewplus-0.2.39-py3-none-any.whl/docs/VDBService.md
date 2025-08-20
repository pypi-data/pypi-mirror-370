# VDBService Documentation

## 1. Introduction

The `VDBService` is a centralized service class designed to manage connections to vector databases (Milvus and Zilliz) and handle the instantiation of embedding models. It simplifies interactions with your vector store by reading all necessary configurations from a single `settings` object.

### Key Features:
- **Centralized Configuration**: Manages database connections and embedding model settings from a single Python dictionary.
- **Provider-Agnostic Client**: Supports both Milvus and Zilliz as vector store providers.
- **Resilient Connection**: Includes a built-in retry mechanism when first connecting to the vector database.
- **Instance Caching**: Caches `Zilliz` vector store instances by collection name to prevent re-instantiation and improve performance.
- **Flexible Embedding Models**: Can retrieve embedding models from either the global `ModelLoadBalancer` or directly from the configuration settings.

## 2. Initialization

To use the `VDBService`, you must first prepare a `settings` dictionary containing the configuration for your vector store and embedding provider. You then pass this dictionary to the service's constructor.

If you plan to use embedding models from the global `ModelLoadBalancer`, you must initialize it first.

```python
from crewplus.vectorstores.milvus.vdb_service import VDBService
from crewplus.services.init_services import init_load_balancer

# 1. (Optional) Initialize the global model load balancer if you plan to use it.
# This should be done once when your application starts.
init_load_balancer(config_path="path/to/your/models_config.json")

# 2. Define the configuration for the VDBService
settings = {
    "embedder": {
        "provider": "azure-openai",
        "config": {
            "model": "text-embedding-3-small",
            "api_version": "2023-05-15",
            "api_key": "YOUR_AZURE_OPENAI_KEY",
            "openai_base_url": "YOUR_AZURE_OPENAI_ENDPOINT",
            "embedding_dims": 1536
        }
    },
    "vector_store": {
        "provider": "milvus",
        "config": {
            "host": "localhost",
            "port": 19530,
            "user": "root",
            "password": "password",
            "db_name": "default"
        }
    },
    "index_params": {
        "metric_type": "L2",
        "index_type": "AUTOINDEX",
        "params": {}
    }
}

# 3. Initialize the VDBService with the settings
vdb_service = VDBService(settings=settings)

print("VDBService initialized successfully!")
```

**Alternative Initialization for Zilliz**

For a simpler Zilliz Cloud connection, you can initialize the service directly with your endpoint and token.

```python
# Initialize directly with Zilliz credentials
vdb_service_zilliz = VDBService(
    endpoint="YOUR_ZILLIZ_ENDPOINT", 
    token="YOUR_ZILLIZ_TOKEN"
)

print("VDBService for Zilliz initialized successfully!")
```

## 3. Usage Examples

### Basic Usage: Get Vector Store with Default Embeddings

This example shows how to get a vector store instance using the default embedding model specified in the `embedder` section of your settings.

```python
# Get a vector store instance for the "my_documents" collection
# This will use the "azure-openai" embedder from the settings by default.
vector_store = vdb_service.get_vector_store(collection_name="my_documents")

# You can now use the vector_store object to add or search for documents
# vector_store.add_texts(["some text to embed"])
print(f"Successfully retrieved vector store for collection: {vector_store.collection_name}")
```

### Advanced Usage: Using an Embedding Model from the Model Load Balancer

In some cases, you may want to use a specific embedding model managed by the central `ModelLoadBalancer`. This example demonstrates how to retrieve that model first and then pass it to `get_vector_store`.

This requires the `ModelLoadBalancer` to have been initialized, as shown in the Initialization section above.

```python
# 1. Get a specific embedding model from the ModelLoadBalancer
# The service will call get_model_balancer() internally to get the initialized instance.
embedding_model = vdb_service.get_embeddings(
    from_model_balancer=True,
    provider="azure-openai-embeddings", 
    model_type="embedding-large" # Specify the model type configured in the balancer
)

print(f"Retrieved embedding model from balancer: {embedding_model}")

# 2. Get a vector store instance using the specified embedding model
vector_store_from_balancer = vdb_service.get_vector_store(
    collection_name="balancer_collection",
    embeddings=embedding_model  # Pass the specific embedding model
)

print(f"Successfully retrieved vector store for collection: {vector_store_from_balancer.collection_name}")
```

### Getting the Raw Milvus Client

If you need to perform operations not exposed by the LangChain `Zilliz` wrapper, you can get direct access to the underlying `MilvusClient`.

```python
# Get the raw Milvus client to perform advanced operations
client = vdb_service.get_vector_client()

# For example, list all collections in the database
collections = client.list_collections()
print("Available collections:", collections)
```

### Adding and Deleting Documents by Source

This example shows a common workflow: adding documents with a specific `source` to a collection, and then using `delete_old_indexes` to remove them based on that source.

**Note:** The `delete_old_indexes` method in this example filters on the `source` metadata field. Ensure your implementation matches the field you intend to use for filtering.

```python
from langchain_core.documents import Document
import time

# 1. Get the vector store instance
collection_name = "test_collection_for_delete"
vector_store = vdb_service.get_vector_store(collection_name=collection_name)

# 2. Prepare documents with 'source' in their metadata.
# The delete function looks for this specific metadata field.
docs_to_add = [
    Document(
        page_content="This is a test document about CrewPlus AI.",
        metadata={"source": "http://example.com/crewplus-docs"}
    ),
    Document(
        page_content="This is another test document, about LangChain.",
        metadata={"source": "http://example.com/langchain-docs"} # Different source
    )
]

# 3. Add the documents to the collection
ids = vector_store.add_documents(docs_to_add)
print(f"Added {len(ids)} documents to collection '{collection_name}'.")

# In a real application, you might need a short delay for indexing to complete.
time.sleep(2) 

# 4. Verify the documents were added
results = vector_store.similarity_search("CrewPlus", k=2)
print(f"Found {len(results)} related documents before deletion.")
assert len(results) > 0

# 5. Delete the documents using the same source
source_to_delete = "http://example.com/crewplus-docs"
vdb_service.delete_old_indexes(url=source_to_delete, vdb=vector_store)
print(f"Called delete_old_indexes for source: {source_to_delete}")

# Allow time for the deletion to be processed.
time.sleep(2)

# 6. Verify the documents were deleted
results_after_delete = vector_store.similarity_search("CrewPlus", k=2)
print(f"Found {len(results_after_delete)} related documents after deletion.")
assert len(results_after_delete) == 0

# 7. Clean up by dropping the collection
vdb_service.drop_collection(collection_name=collection_name)
print(f"Dropped collection '{collection_name}'.")
```

### Adding and Deleting Documents by Source ID

This example shows how to add documents with a `source_id` and then use `delete_old_indexes_by_id` to remove them.

```python
from langchain_core.documents import Document
import time

# 1. Get the vector store instance
collection_name = "test_collection_for_id_delete"
vector_store_for_id = vdb_service.get_vector_store(collection_name=collection_name)

# 2. Prepare documents with 'source_id' in their metadata.
docs_with_id = [
    Document(
        page_content="Document for agent A.",
        metadata={"source_id": "agent-a-123"}
    ),
    Document(
        page_content="Another document for agent A.",
        metadata={"source_id": "agent-a-123"}
    )
]

# 3. Add the documents to the collection
ids = vector_store_for_id.add_documents(docs_with_id)
print(f"Added {len(ids)} documents to collection '{collection_name}'.")

time.sleep(2) 

# 4. Verify the documents were added
results = vector_store_for_id.similarity_search("agent A", k=2)
print(f"Found {len(results)} related documents before deletion.")
assert len(results) == 2

# 5. Delete the documents using the source_id
id_to_delete = "agent-a-123"
vdb_service.delete_old_indexes_by_id(source_id=id_to_delete, vdb=vector_store_for_id)
print(f"Called delete_old_indexes_by_id for source_id: {id_to_delete}")

time.sleep(2)

# 6. Verify the documents were deleted
results_after_delete = vector_store_for_id.similarity_search("agent A", k=2)
print(f"Found {len(results_after_delete)} related documents after deletion.")
assert len(results_after_delete) == 0

# 7. Clean up by dropping the collection
vdb_service.drop_collection(collection_name=collection_name)
print(f"Dropped collection '{collection_name}'.")