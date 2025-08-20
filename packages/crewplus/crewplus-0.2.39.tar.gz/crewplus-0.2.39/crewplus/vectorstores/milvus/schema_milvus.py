from typing import List, Optional
import logging
import json

from pymilvus import DataType
from langchain_milvus import Milvus
from langchain_core.documents import Document
from ...utils.schema_document_updater import SchemaDocumentUpdater
from ...utils.schema_action import Action
from .milvus_schema_manager import MilvusSchemaManager

DEFAULT_SCHEMA = """
{
    "node_types": {
        "Document": {
            "properties": {
                "pk": {
                    "type": "INT64",
                    "is_primary": true,
                    "auto_id": true
                },
                "vector": {
                    "type": "FLOAT_VECTOR",
                    "dim": 1536
                },
                "text": {
                    "type": "VARCHAR",
                    "max_length": 65535,
                    "description": "The core text of the memory. This could be a user query, a documented fact, a procedural step, or a log of an event."
                }
	        }
	    }
    }
}
"""

class SchemaMilvus(Milvus):
    """
    SchemaMilvus is a subclass of the Milvus class from langchain_milvus. This class is responsible for updating metadata of documents in a Milvus vector store.

    Attributes:
        embedding_function: Embedding function used by the Milvus vector store.
        collection_name: Name of the collection in the Milvus vector store.
        connection_args: Connection arguments for the Milvus vector store.
        index_params: Index parameters for the Milvus vector store.
        auto_id: Flag to specify if auto ID generation is enabled.
        primary_field: The primary field of the collection.
        vector_field: The vector field of the collection.
        consistency_level: The consistency level for the Milvus vector store.
        collection_schema: Schema JSON string associated with the Milvus existing collection name.
    """
    def __init__(
        self, 
        embedding_function, 
        collection_name, 
        connection_args, 
        index_params=None, 
        auto_id=True, 
        primary_field="pk", 
        text_field: str = "text",
        vector_field=["vector"], 
        consistency_level="Session",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initializes the SchemaMilvus class with the provided parameters.

        Args:
            embedding_function: Embedding function used by the Milvus vector store.
            collection_name: Name of the collection in the Milvus vector store.
            connection_args: Connection arguments for the Milvus vector store.
            index_params: Index parameters for the Milvus vector store.
            auto_id: Flag to specify if auto ID generation is enabled.
            primary_field: The primary field of the collection.
            text_field: The text field of the collection.
            vector_field: The vector field of the collection.
            consistency_level: The consistency level for the Milvus vector store.
            logger: Optional logger instance. If not provided, a default logger is created.
        """
        super().__init__(
            embedding_function=embedding_function,
            collection_name=collection_name,
            connection_args=connection_args,
            index_params=index_params,
            auto_id=auto_id,
            primary_field=primary_field,
            text_field=text_field,
            vector_field=vector_field,
            consistency_level=consistency_level
        )
        self.logger = logger or logging.getLogger(__name__)
        self.collection_schema = None
        self.schema_manager = MilvusSchemaManager(client=self.client)

    def set_schema(self, schema: str):
        """
        Sets the collection schema.

        Args:
            schema: The schema JSON string.
        """
        self.collection_schema = schema
    
    def get_fields(self, collection_name: Optional[str] = None) -> Optional[List[str]]:
        """
        Retrieves and returns the fields from the collection schema.

        Args:
            collection_name: The name of the collection to describe. If None, use self.collection_name.

        Returns:
            List[str] | None: The list of field names from the collection schema (excluding vector and text fields), or None if collection_name is not provided or an error occurs.
        """
        if collection_name is None:
            collection_name = self.collection_name
        if collection_name is None:
            return None

        try:
            schema = self.client.describe_collection(collection_name)
            fields = [field["name"] for field in schema["fields"] if field["type"] != DataType.FLOAT_VECTOR ]
            return fields
        except Exception as e:
            self.logger.warning(f"Failed to retrieve schema fields: {e}")
            return None
    
    def create_collection(self) -> bool:
        """
        Validates the schema and creates the collection using the MilvusSchemaManager.

        Returns:
            bool: True if the collection is successfully created, False otherwise.
        """
        if self.collection_schema is None:
            self.logger.error("Collection schema is not set. Please set a schema using set_schema().")
            return False
            
        self.schema_manager.bind_client(self.client)
        if not self.schema_manager.validate_schema(self.collection_schema):
            self.logger.error("Failed to validate schema")
            return False
        try:
            self.schema_manager.create_collection(self.collection_name, self.collection_schema)
            self.logger.info(f"Collection {self.collection_name} created successfully")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to create collection: {e}")
            return False

    def drop_collection(self, collection_name: Optional[str] = None) -> bool:
        """
        Drops the collection using the Milvus client.

        Returns:
            bool: True if the collection is successfully dropped, False otherwise.
        """
        if collection_name is None:
            collection_name = self.collection_name
            
        try:
            self.client.drop_collection(collection_name)
            self.logger.info(f"Collection {collection_name} dropped successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to drop collection {self.collection_name}: {e}")
            return False

    def _handle_upsert(self, doc: Document, metadata_dict: dict) -> Document:
        """
        Handles the UPSERT action for a single document by merging metadata.
        """
        existing_metadata = doc.metadata
        for key, value in metadata_dict.items():
            # Skip primary key and text fields to prevent modification.
            if key in [self.primary_field, self.text_field]:
                continue

            if isinstance(value, dict):
                # If the new value is a dictionary, handle nested updates.
                if key not in existing_metadata or not isinstance(existing_metadata.get(key), dict):
                    # If the key doesn't exist or its value is not a dict, replace it.
                    existing_metadata[key] = value
                else:
                    # If both are dictionaries, recursively update the nested fields.
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, dict) and sub_key in existing_metadata[key] and isinstance(existing_metadata[key].get(sub_key), dict):
                            existing_metadata[key][sub_key].update(sub_value)
                        else:
                            existing_metadata[key][sub_key] = sub_value
            else:
                # For non-dictionary values, simply update or add the field.
                existing_metadata[key] = value

        doc.metadata = existing_metadata
        return doc

    def _prepare_documents_for_update(self, expr: str, metadata: str, action: Action = Action.UPSERT) -> tuple[List[Document], List]:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string for metadata")

        # Retrieve documents that match the filter expression.
        fields = self.get_fields()
        documents = self.search_by_metadata(expr, fields=fields, limit=5000)

        updated_documents = []
        for doc in documents:
            # Preserve the original primary key and text values.
            pk_value = doc.metadata.get(self.primary_field) # default to pk
            text_value = doc.metadata.get(self.text_field)

            # Apply the specified action to update the document's metadata.
            if action == Action.UPSERT:
                doc = self._handle_upsert(doc, metadata_dict)
            elif action == Action.DELETE:
                keys_to_delete = metadata_dict.keys()
                doc = SchemaDocumentUpdater.delete_document_metadata(doc, list(keys_to_delete))
            elif action == Action.UPDATE:
                existing_metadata = doc.metadata
                update_dict = {}
                for key, value in metadata_dict.items():
                    if key in existing_metadata:
                        if isinstance(value, dict) and isinstance(existing_metadata.get(key), dict):
                            merged = existing_metadata[key].copy()
                            for sub_key, sub_value in value.items():
                                if sub_key in merged:
                                    merged[sub_key] = sub_value
                            update_dict[key] = merged
                        else:
                            update_dict[key] = value
                doc = SchemaDocumentUpdater.update_document_metadata(doc, update_dict)
            elif action == Action.INSERT:
                existing_metadata = doc.metadata
                for key, value in metadata_dict.items():
                    if key in ['pk', 'text']:
                        continue

                    if isinstance(value, dict) and key in existing_metadata and isinstance(existing_metadata.get(key), dict):
                        existing_metadata[key] = {}
                        existing_metadata[key] = value
                    else:
                        existing_metadata[key] = value
                doc.metadata = existing_metadata

            # Restore the primary key and text values to ensure they are not lost.
            if pk_value is not None:
                doc.metadata[self.primary_field] = pk_value
            if text_value is not None:
                doc.metadata[self.text_field] = text_value

            updated_documents.append(doc)

        if not updated_documents:
            return [], []

        # Extract the primary keys for the upsert operation.
        updated_ids = [doc.metadata[self.primary_field] for doc in updated_documents]

        # Remove primary key and text from metadata before upserting,
        # as they are handled separately by the vector store.
        for doc in updated_documents:
            doc.metadata.pop(self.primary_field, None)
            doc.metadata.pop(self.text_field, None)

        return updated_documents, updated_ids

    def update_documents_metadata(self, expr: str, metadata: str, action: Action = Action.UPSERT) -> List[Document]:
        """
        Updates the metadata of documents in the Milvus vector store based on the provided expression.

        Args:
            expr: Expression to filter the target documents.
            metadata: New metadata to update the documents with.

        Returns:
            List of updated documents.
        """
        documents_to_upsert, updated_ids = self._prepare_documents_for_update(expr, metadata, action)

        if not documents_to_upsert:
            return []

        # Perform the upsert operation to update the documents in the collection.
        self.upsert(ids=updated_ids, documents=documents_to_upsert)

        return documents_to_upsert

    async def aupdate_documents_metadata(self, expr: str, metadata: str, action: Action = Action.UPSERT) -> List[Document]:
        """
        Asynchronously updates the metadata of documents in the Milvus vector store.

        Args:
            expr: Expression to filter the target documents.
            metadata: New metadata to update the documents with.
            action: The action to perform on the document metadata.

        Returns:
            List of updated documents.
        """
        documents_to_upsert, updated_ids = self._prepare_documents_for_update(expr, metadata, action)

        if not documents_to_upsert:
            return []

        # Perform the asynchronous upsert operation.
        await self.aupsert(ids=updated_ids, documents=documents_to_upsert)

        return documents_to_upsert
