from typing import List, Optional
import logging
import json
import asyncio

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
                # If it's a JSON object field (e.g., plant_metadata)
                # Check if the existing value is a string, and if so, try to parse it as a dictionary
                if key in existing_metadata and isinstance(existing_metadata[key], str):
                    try:
                        existing_metadata[key] = json.loads(existing_metadata[key])
                    except json.JSONDecodeError:
                        # If the parsing fails, it may not be a valid JSON string, treat it as a regular string
                        self.logger.warning(f"Field '{key}' could not be parsed as JSON. Overwriting as a new dict.")
                        existing_metadata[key] = {}

                if key not in existing_metadata:
                    # If the field does not exist, add it
                    existing_metadata[key] = value
                elif isinstance(existing_metadata[key], dict):
                    # If the field exists and is a dictionary, recursively update the sub-fields
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, dict):
                            # If the sub-field is also a dictionary, recursively process it
                            if sub_key not in existing_metadata[key]:
                                existing_metadata[key][sub_key] = sub_value
                            else:
                                existing_metadata[key][sub_key].update(sub_value)
                        else:
                            # If the sub-field is a regular value, update it
                            existing_metadata[key][sub_key] = sub_value
                else:
                    # If the field exists but is not a dictionary (e.g., a number or string), overwrite with the new dictionary
                    existing_metadata[key] = value
            else:
                # If it's a regular field, update the value
                existing_metadata[key] = value

        # Update the document's metadata
        doc.metadata = existing_metadata

        return doc

    def _process_document_update(self, doc: Document, metadata_dict: dict, action: Action) -> Document:
        """
        Applies the specified update operation to a single document.
        
        Args:
            doc: The Document object to be updated.
            metadata_dict: A dictionary containing the new data.
            action: The type of operation to perform (UPSERT, DELETE, UPDATE, INSERT).

        Returns:
            The updated Document object.
        """
        pk_value = doc.metadata.get(self.primary_field)
        text_value = doc.metadata.get(self.text_field)

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

        if pk_value is not None:
            doc.metadata[self.primary_field] = pk_value
        if text_value is not None:
            doc.metadata[self.text_field] = text_value
        
        return doc

    def update_documents_metadata(self, expr: str, metadata: str, action: Action = Action.UPSERT) -> List[Document]:
        """
        Updates the metadata of documents in the Milvus vector store based on the provided expression.
        This method uses a direct client upsert to avoid re-embedding vectors.

        Args:
            expr: Expression to filter the target documents.
            metadata: New metadata to update the documents with.
            action: The action to perform on the document metadata.

        Returns:
            List of updated documents.
        """
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string for metadata")
        
        fields = self.get_fields()
        if not fields:
            fields = []

        if isinstance(self._vector_field, list):
            fields.extend(self._vector_field)
        else:
            fields.append(self._vector_field)

        documents = self.search_by_metadata(expr, fields=fields, limit=5000)
        
        updated_documents = [self._process_document_update(doc, metadata_dict, action) for doc in documents]

        if updated_documents:
            self.logger.debug(f"Upserting {len(updated_documents)} documents using direct client upsert.")
            upsert_data = [doc.metadata for doc in updated_documents]
            self.client.upsert(
                collection_name=self.collection_name,
                data=upsert_data
            )
        
        return updated_documents

    async def aupdate_documents_metadata(self, expr: str, metadata: str, action: Action = Action.UPSERT) -> List[Document]:
        """
        Asynchronously updates the metadata of documents in the Milvus vector store.
        This method uses a direct client upsert to avoid re-embedding vectors.

        Args:
            expr: Expression to filter the target documents.
            metadata: New metadata to update the documents with.
            action: The action to perform on the document metadata.

        Returns:
            List of updated documents.
        """
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string for metadata")
        
        fields = self.get_fields()
        if not fields:
            fields = []

        if isinstance(self._vector_field, list):
            fields.extend(self._vector_field)
        else:
            fields.append(self._vector_field)

        documents = self.search_by_metadata(expr, fields=fields, limit=5000)
        
        updated_documents = [self._process_document_update(doc, metadata_dict, action) for doc in documents]

        if updated_documents:
            self.logger.debug(f"Upserting {len(updated_documents)} documents using direct client upsert.")
            upsert_data = [doc.metadata for doc in updated_documents]
            
            await asyncio.to_thread(
                self.client.upsert,
                collection_name=self.collection_name,
                data=upsert_data
            )
        
        return updated_documents

    def update_documents_metadata_by_iterator(self, expr: str, metadata: str, action:Action=Action.UPSERT) -> List[Document]:
        """
        【官方推荐版】
        使用 pymilvus.Collection.query_iterator 官方推荐的迭代方式更新元数据。
        本方法的业务逻辑（UPSERT/DELETE等）与 update_documents_metadata 方法完全一致，
        仅数据获取方式遵循官方标准迭代器模式。
        """
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string for metadata")

        fields = self.get_fields() or []
        # 确保主键和文本字段在输出字段中
        if 'pk' not in fields:
            fields.append('pk')
        text_field = getattr(self, "_text_field", "text")
        if text_field not in fields:
            fields.append(text_field)
        
        # 【关键修正】: 确保在查询时也获取向量字段。
        # self.client.upsert 操作要求提供所有非 nullable 字段，包括 vector。
        # 因此，我们必须在迭代查询时获取它，以便在更新时能够一并传回。
        vector_fields_to_add = self._vector_field if isinstance(self._vector_field, list) else [self._vector_field]
        for vf in vector_fields_to_add:
            if vf not in fields:
                fields.append(vf)
            
        total_updated_documents = []
        batch_size = 1000 # 您可以根据需要调整批次大小

        self.logger.info(f"Starting metadata update using 'collection.query_iterator' with batch size {batch_size}.")

        # # 1. 【关键保险】: 在查询前，显式地确保集合已被加载。
        # logger.info(f"Ensuring collection '{self.collection_name}' is loaded before querying.")
        # self.col.load()

        # 2. 【官方用法】: 创建官方推荐的迭代器
        iterator = self.col.query_iterator(
            batch_size=batch_size,
            expr=expr,
            output_fields=fields
        )

        batch_i = 0
        try:
            while True:
                # 3. 【官方用法】: 获取下一批次
                batch_results = iterator.next()
                if not batch_results:
                    break # 迭代完成，正常退出

                batch_i += 1
                self.logger.info(f"Processing batch {batch_i} of {len(batch_results)} documents.")

                # 4. 将 Milvus 返回的 dict 列表转换为 Langchain Document 对象
                documents = [
                    Document(page_content=result.get(text_field, ""), metadata=result)
                    for result in batch_results
                ]

                # 5. 【核心业务逻辑】: 使用公共方法处理批次中的每个文档
                updated_documents_in_batch = [self._process_document_update(doc, metadata_dict, action) for doc in documents]
                
                # 6. 【Upsert逻辑】: 
                if updated_documents_in_batch:
                    self.logger.debug(f"Upserting batch of {len(updated_documents_in_batch)} documents using direct client upsert.")
                    # 从更新后的 Document 对象中提取元数据字典列表
                    upsert_data = [doc.metadata for doc in updated_documents_in_batch]
                    self.client.upsert(
                        collection_name=self.collection_name,
                        data=upsert_data
                    )
                    total_updated_documents.extend(updated_documents_in_batch)

        finally:
            # 7. 【官方用法】: 确保迭代器被关闭
            self.logger.info("Closing iterator.")
            iterator.close()
            
        self.logger.info(f"Iterator processing complete. Total batches processed: {batch_i}.")
        return total_updated_documents


    def update_documents_metadata_folder_path(self, old_expr: str, metadata: str, action:Action=Action.UPSERT) -> List[Document]:
        """
        专门用于更新 version_metadata.folder_path 字段的方法。

        它执行一个“目录移动”逻辑：
        1. 使用 old_expr 找出所有路径匹配的文档。
        2. 从 metadata 中获取新的基础路径。
        3. 将文档中 folder_path 的 old_expr 前缀替换为新的基础路径，并保留后续的子路径。
        """
        # 1. 根据 old_expr 构造一个 "starts with" 查询
        # Milvus JSON 'like' 操作符需要转义内部的双引号
        # 但由于我们这里是变量，直接用 f-string 插入是安全的
        expr = f"version_metadata[\"folder_path\"] like \"{old_expr}%\""

        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string for metadata")

        fields = self.get_fields() or []
        # 确保关键字段都被查询出来
        required_fields = ['pk', getattr(self, "_text_field", "text")]
        vector_fields = self._vector_field if isinstance(self._vector_field, list) else [self._vector_field]
        required_fields.extend(vector_fields)
        
        for f in required_fields:
            if f not in fields:
                fields.append(f)

        total_updated_documents = []
        batch_size = 1000

        self.logger.info(f"Starting folder path update using 'collection.query_iterator' with expr: {expr}")

        # self.col.load() # 确保集合已加载

        iterator = self.col.query_iterator(
            batch_size=batch_size,
            expr=expr,
            output_fields=fields
        )

        batch_i = 0
        try:
            while True:
                batch_results = iterator.next()
                if not batch_results:
                    break

                batch_i += 1
                self.logger.info(f"Processing batch {batch_i} of {len(batch_results)} documents for folder path update.")

                documents = [
                    Document(page_content=result.get(getattr(self, "_text_field", "text"), ""), metadata=result)
                    for result in batch_results
                ]

                updated_documents_in_batch = []
                for doc in documents:
                    # 沿用标准的 UPSERT 逻辑，但在处理 folder_path 时应用特殊规则
                    if action == Action.UPSERT:
                        existing_metadata = doc.metadata
                        for key, value in metadata_dict.items():
                            # ... (此处省略了标准的深层合并逻辑，与您已有的 update_documents_metadata 方法一致)
                            # 仅展示与 folder_path 相关的特殊处理部分
                            if isinstance(value, dict):
                                # ... (处理从数据库读出的可能是字符串的JSON)
                                if key in existing_metadata and isinstance(existing_metadata[key], str):
                                    try:
                                        existing_metadata[key] = json.loads(existing_metadata[key])
                                    except json.JSONDecodeError:
                                        existing_metadata[key] = {}
                                
                                if key not in existing_metadata or not isinstance(existing_metadata[key], dict):
                                    existing_metadata[key] = value
                                else:
                                    # 递归更新，在这里注入我们的特殊逻辑
                                    for sub_key, sub_value in value.items():
                                        # 【核心特殊逻辑】
                                        if key == 'version_metadata' and sub_key == 'folder_path':
                                            new_folder_path_base = sub_value
                                            current_folder_path = existing_metadata.get(key, {}).get(sub_key)

                                            if current_folder_path and current_folder_path.startswith(old_expr):
                                                # 移除旧前缀，保留子路径
                                                sub_path = current_folder_path[len(old_expr):]
                                                # 拼接新路径（确保斜杠正确）
                                                new_full_path = f"{new_folder_path_base.rstrip('/')}/{sub_path.lstrip('/')}"
                                                existing_metadata[key][sub_key] = new_full_path
                                                self.logger.debug(f"Rewrote folder path from '{current_folder_path}' to '{new_full_path}'")
                                            else:
                                                # 如果不匹配，则按普通逻辑直接覆盖
                                                existing_metadata[key][sub_key] = new_folder_path_base
                                        
                                        # 其他所有字段按原逻辑递归更新
                                        elif isinstance(sub_value, dict):
                                            if sub_key not in existing_metadata[key]:
                                                existing_metadata[key][sub_key] = sub_value
                                            else:
                                                existing_metadata[key][sub_key].update(sub_value)
                                        else:
                                            existing_metadata[key][sub_key] = sub_value
                            else:
                                existing_metadata[key] = value
                        doc.metadata = existing_metadata

                    # (此处可以添加对 DELETE, UPDATE, INSERT 的处理，如果需要的话)
                    
                    updated_documents_in_batch.append(doc)

                if updated_documents_in_batch:
                    self.logger.debug(f"Upserting batch of {len(updated_documents_in_batch)} documents with updated folder paths.")
                    upsert_data = [d.metadata for d in updated_documents_in_batch]
                    self.client.upsert(
                        collection_name=self.collection_name,
                        data=upsert_data
                    )
                    total_updated_documents.extend(updated_documents_in_batch)
        finally:
            self.logger.info("Closing folder path update iterator.")
            iterator.close()

        self.logger.info(f"Folder path update complete. Total batches processed: {batch_i}.")
        return total_updated_documents
