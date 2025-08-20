from pymilvus import DataType, MilvusClient
import json
import logging
from typing import Any

class MilvusSchemaManager:
    """
    Manages Milvus/Milvus collection schemas.

    This class provides functionalities to create and validate collection schemas
    and index parameters based on a JSON definition. It interacts with a
    MilvusClient instance to perform these operations.
    """
    def __init__(self, client: MilvusClient, logger=None):
        """
        Initializes the MilvusSchemaManager.

        Args:
            client (MilvusClient): An instance of the Milvus client.
            logger (logging.Logger, optional): A logger instance. If not provided,
                                               a default logger will be created.
                                               Defaults to None.
        """
        self.client = client
        self.logger = logger or logging.getLogger(__name__)

    def bind_client(self, client: MilvusClient):
        """
        Binds a new MilvusClient instance to the manager.

        Args:
            client (MilvusClient): The Milvus client instance to use.
        """
        self.client = client

    def _add_array_field(self, schema, field_name, field_info):
        """
        Adds an ARRAY field to the schema based on field information.

        This is a helper method to handle the specific logic for creating ARRAY fields.

        Args:
            schema: The Milvus schema object to add the field to.
            field_name (str): The name of the field.
            field_info (dict): A dictionary containing information about the field,
                               such as element type and max capacity.

        Raises:
            ValueError: If required information like 'element' or 'max_capacity'
                        is missing from field_info, or if an unsupported element
                        type is specified.
        """
        element_type_str = field_info.get("element")
        if not element_type_str:
            raise ValueError(f"Array field '{field_name}' must have 'element' type specified.")

        element_type = None
        if element_type_str in ["STRING", "VARCHAR", "TEXT"]:
            element_type = DataType.VARCHAR
        elif element_type_str == "INT64":
            element_type = DataType.INT64
        else:
            raise ValueError(f"Unsupported element type '{element_type_str}' for ARRAY field '{field_name}'.")

        max_capacity = field_info.get("max_capacity")
        if max_capacity is None:
            raise ValueError(f"Array field '{field_name}' must have 'max_capacity' specified.")

        nullable = field_info.get('nullable', True)

        field_args = {
            "field_name": field_name,
            "datatype": DataType.ARRAY,
            "element_type": element_type,
            "max_capacity": int(max_capacity),
            "nullable": nullable,
        }

        if element_type == DataType.VARCHAR:
            max_length = field_info.get('max_length', 65535)
            field_args["max_length"] = int(max_length)
        
        schema.add_field(**field_args)

    def create_collection_schema(self, json_schema: str):
        """
        Creates a Milvus collection schema from a JSON string.

        Args:
            json_schema (str): A JSON string defining the schema.

        Returns:
            A Milvus schema object.

        Raises:
            ValueError: If an unknown field type is encountered in the schema.
        """
        schema_data = json.loads(json_schema)
        fields = schema_data['node_types']['Document']['properties']

        schema = self.client.create_schema(auto_id=False, enable_dynamic_fields=True)
        for field_name, field_info in fields.items():
            field_type = field_info['type']
            if field_type == "STRING" or field_type == "VARCHAR" or field_type == "TEXT":
                max_length = field_info.get('max_length', 256)  # Default max_length if not provided
                nullable = field_info.get('nullable', False)    # Default nullable if not provided
                schema.add_field(field_name=field_name, datatype=DataType.VARCHAR, max_length=max_length, nullable=nullable)
            elif field_type == "JSON":
                nullable = field_info.get('nullable', True)
                schema.add_field(field_name=field_name, datatype=DataType.JSON, nullable=nullable)
            elif field_type == "INT64":
                is_primary = field_info.get('is_primary', False)
                auto_id = field_info.get('auto_id', False)
                nullable = field_info.get('nullable', False)
                schema.add_field(field_name=field_name, datatype=DataType.INT64, is_primary=is_primary, auto_id=auto_id, nullable=nullable)
            elif field_type == "FLOAT":
                nullable = field_info.get('nullable', True)
                schema.add_field(field_name=field_name, datatype=DataType.FLOAT, nullable=nullable)
            elif field_type == "ARRAY":
                self._add_array_field(schema, field_name, field_info)
            elif field_type == "FLOAT_VECTOR":
                dim = field_info.get('dim', 1536)  # Default dimension if not provided
                schema.add_field(field_name=field_name, datatype=DataType.FLOAT_VECTOR, dim=dim)
            else:
                raise ValueError(f"Unknown field type: {field_type}")

        return schema

    def create_index_params(self, json_schema: str):
        """
        Creates index parameters from a JSON schema string.

        This method defines indexes based on the 'indexes' section of the schema
        and automatically creates an 'AUTOINDEX' for any FLOAT_VECTOR fields.

        Args:
            json_schema (str): A JSON string defining the schema and indexes.

        Returns:
            Milvus index parameters object.
        """
        schema_data = json.loads(json_schema)
        fields = schema_data['node_types']['Document']['properties']
        
        index_params = self.client.prepare_index_params()

        # Check if 'indexes' key exists
        if 'indexes' in schema_data['node_types']['Document']:
            indexes = schema_data['node_types']['Document']['indexes']
            for index_name, index_details in indexes.items():
                field_name = index_details['fieldname']
                index_type = index_details['type']
                params = index_details['params']
                index_params.add_index(
                    field_name=field_name,
                    index_type=index_type,
                    index_name=index_name,
                    params=params
                )

        # Automatic indexing for FLOAT_VECTOR fields
        for field_name, field_info in fields.items():
            if field_info['type'] == "FLOAT_VECTOR":
                index_params.add_index(
                    field_name=field_name,
                    index_name="vector",
                    index_type="AUTOINDEX",
                    metric_type="L2"
                )

        return index_params

    def create_collection(self, collection_name: str, json_schema: str):
        """
        Creates a new collection in Milvus.

        This method orchestrates the creation of the schema and index parameters
        before creating the collection itself.

        Args:
            collection_name (str): The name for the new collection.
            json_schema (str): The JSON string defining the collection's schema
                               and indexes.
        """
        schema = self.create_collection_schema(json_schema)
        index_params = self.create_index_params(json_schema)

        self.client.create_collection(
            collection_name=collection_name,
            schema=schema,
            index_params=index_params,
            enable_dynamic_fields=True   # we need to enable dynamic fields for schema updates
        )

    def validate_schema(self, json_schema: str) -> bool:
        """
        Validates the given schema by attempting to create a collection schema and index params.

        Args:
            json_schema (str): The schema JSON string to validate.

        Returns:
            bool: True if the schema is valid, False if any exceptions are caught.
        """
        try:
            self.create_collection_schema(json_schema)
            self.create_index_params(json_schema)
            return True
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
            return False


class ZillizSchemaManager(MilvusSchemaManager):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        import warnings

        warnings.warn(
            "The ZillizSchemaManager class will be deprecated in the future. "
            "Please use the MilvusSchemaManager class instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)    