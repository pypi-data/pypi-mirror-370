from typing import List
from langchain_core.documents import Document
import random

class SchemaDocumentUpdater:
    """A utility class for updating and creating LangChain Documents with specific metadata schemas."""
    
    @staticmethod
    def update_document_metadata(document: Document, metadata: dict) -> Document:
        """
        Updates the metadata of a LangChain Document.

        Args:
            document (Document): The document to update.
            metadata (dict): A dictionary containing the metadata to add or update.

        Returns:
            Document: The updated document with the new metadata.
        """
        metadata_updates = document.metadata

        for key, value in metadata.items():
            metadata_updates[key] = value

        return Document(
            page_content=document.page_content,
            metadata=metadata_updates
        )

    @staticmethod
    def delete_document_metadata(document: Document, keys_to_delete: List[str]) -> Document:
        """
        Deletes specified keys from the metadata of a LangChain Document.

        Args:
            document (Document): The document to update.
            keys_to_delete (List[str]): A list of keys to delete from the metadata.

        Returns:
            Document: The updated document with the specified metadata keys removed.
        """
        metadata = document.metadata

        for key in keys_to_delete:
            if key in metadata:
                del metadata[key]

        return Document(
            page_content=document.page_content,
            metadata=metadata
        )

    @staticmethod
    def add_sample_metadata(document: Document, type: str) -> Document:
        """
        Adds sample metadata to a document based on a specified type.

        The metadata schema is tailored for either "Reg Wheel" or "Robot" types.

        Args:
            document (Document): The document to which sample metadata will be added.
            type (str): The type of sample metadata to add ("Reg Wheel" or "Robot").

        Returns:
            Document: The document with added sample metadata.
        """
        if type == "Reg Wheel":
            meta = {
                "keywords": "Reg Wheel",
                "plant_metadata": {
                    "entity_id": "EQUIP_123",
                    "entity_type": "Machine",
                    "hierarchy_path": "/EnterpriseA/SITE_A/LINE_003/",
                    "entity_tags": ["nickname_for_EQUIP_123", "PB3"],
                    "parent_entity": None,
                    "linked_entities": []
                },
                "version_metadata": {
                    "version_id": "V2.0",
                    "version_tags": ["global"],
                    "version_date": "2024/05/23"
                },
                "other_metadata": {}
            }
        else:  # Robot
            meta = {
                "keywords": "Robot",
                "plant_metadata": {
                    "entity_id": "EQUIP_124",
                    "entity_type": "Robot",
                    "hierarchy_path": "/EnterpriseA/SITE_A/LINE_002/",
                    "entity_tags": ["nickname_for_EQUIP_124", "RB2"],
                    "parent_entity": None,
                    "linked_entities": []
                },
                "version_metadata": {
                    "version_id": "R1.0",
                    "version_tags": ["prototype"],
                    "version_date": "2024/05/23"
                },
                "other_metadata": {}
            }

        updated_document = SchemaDocumentUpdater.update_document_metadata(document, meta)
        return updated_document

    @staticmethod
    def create_test_document(index: int, type: str) -> Document:
        """
        Creates a test document with sample content and metadata.

        The content and metadata are generated based on the specified type ("Reg Wheel" or "Robot").

        Args:
            index (int): An index number to make the document unique.
            type (str): The type of test document to create ("Reg Wheel" or "Robot").

        Returns:
            A new test document.
        """
        meta = {
            "title": f"{type} Maintenance Record {index}",
            "source_url": f"http://example.com/{type.lower()}_maintenance_{index}",
            "file_type": "xlsx",
            "page": index
        }

        if type == "Reg Wheel":
            page_content = ["| Date       | Maintenance Performed | Technician | Notes                      |",
                            "|------------|-----------------------|------------|----------------------------|"]
            for _ in range(random.randint(10, 20)):
                day = random.randint(1, 28)
                maintenance_performed = random.choice(["Oil Change", "Belt Replacement", "Alignment Check", "General Inspection"])
                technician = random.choice(["John Doe", "Jane Smith", "Jim Brown"])
                notes = random.choice(["Changed oil and filter", "Replaced worn-out belt", "Checked and adjusted align", "No issues found"])
                page_content.append(f"| 2023-05-{day:02} | {maintenance_performed} | {technician} | {notes} |")
            page_content = "\n".join(page_content)
        else:  # Robot
            technicians = ["Bob", "Tim", "Alice"]
            page_content = ["| Date       | Maintenance Performed | Technician | Notes                               |",
                            "|------------|-----------------------|------------|-------------------------------------|"]
            for _ in range(random.randint(10, 20)):
                day = random.randint(1, 28)
                maintenance_performed = random.choice(["Sensor Calibration", "Actuator Testing", "Software Update", "Battery Replacement"])
                technician = random.choice(technicians)
                notes = random.choice(["Calibrated all sensors", "Tested and replaced faulty actuators", "Updated robot software to v2.1", "Replaced old battery with new one"])
                page_content.append(f"| 2023-05-{day:02} | {maintenance_performed} | {technician} | {notes} |")
            page_content = "\n".join(page_content)

        document = Document(page_content=page_content, metadata=meta)
        return SchemaDocumentUpdater.add_sample_metadata(document, type)

    @staticmethod
    def create_test_documents(doc_num: int) -> List[Document]:
        """
        Creates a list of test documents.

        It generates a mix of "Reg Wheel" and "Robot" documents.

        Args:
            doc_num (int): The total number of documents to create.

        Returns:
            List[Document]: A list of created test documents.
        """

        reg_wheel_docs_num = doc_num * 2 // 3
        robot_docs_num = doc_num - reg_wheel_docs_num
        
        documents = [SchemaDocumentUpdater.create_test_document(i+1, "Reg Wheel") for i in range(reg_wheel_docs_num)]
        documents += [SchemaDocumentUpdater.create_test_document(i+1 + reg_wheel_docs_num, "Robot") for i in range(robot_docs_num)]
        
        return documents