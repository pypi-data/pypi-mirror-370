from enum import Enum

class Action(Enum):
    UPSERT = "upsert"  # Update existing fields; if a match is found, it updates, otherwise, it inserts. Does not delete unmatched existing fields.
    DELETE = "delete"  # Clear data from fields in the schema.
    UPDATE = "update"  # Update only the matching original fields.
    INSERT = "insert"  # Insert data, clearing the original fields before inserting new values.