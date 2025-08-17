from sharedkernel.objects.base_document import BaseDocument

from enum import Enum

class AuditOperation(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class AuditLog(BaseDocument):
    user_id: str
    collection_name: str
    document_id: str
    operation: AuditOperation
    original: dict | None = None
    modified: dict
    
