from typing import Generic, TypeVar, List, Type
from bson import ObjectId
from pymongo import MongoClient
from pydantic.v1 import BaseModel

from sharedkernel.database.audit_model import AuditLog
from sharedkernel.enum.sort_order import SortOrder

T = TypeVar("T", bound=BaseModel)

AUDIT_COLLECTION_NAME = "audit_log"

class MongoGenericAuditRepository():
    def __init__(
            self,
            database: MongoClient,
            audit_collection_name: str | None = None
        ):
        self.database = database
        self.__collection_name = audit_collection_name or AUDIT_COLLECTION_NAME

        self.collection = self.database[self.__collection_name]

    def _map_to_model(self, document: dict) -> AuditLog:
        document["id"] = str(document.pop("_id"))
        return AuditLog(**document)

    def find_one(self, id: str) -> T:
        query = {"_id": ObjectId(id), "is_deleted": False}
        result = self.collection.find_one(query)
        return self._map_to_model(result) if result else None   

    def find(
        self,
        document_id: str | None = None,
        operation: str | None = None,
        collection_name: str | None  = None,
        field_name: str | None  = None,
        page_number=1,
        page_size=10,
        sort_order: SortOrder = SortOrder.Descending,
    ) -> List[AuditLog]:
        sort_order = -1 if sort_order == SortOrder.Descending else 1

        skip_count = (page_number - 1) * page_size

        query = {}

        if document_id:
            query["document_id"] = document_id
        if operation:
            query["operation"] = operation
        if collection_name:
            query["collection_name"] = collection_name

        if field_name:
            query["$or"] = [
                {f"original.{field_name}": {"$exists": True}},
                {f"modified.{field_name}": {"$exists": True}},
            ]

        results = self.collection.find(query).sort("_id", sort_order).skip(skip_count).limit(page_size)
        return [self._map_to_model(bot) for bot in results]
    
    def find_by_value(
        self,
        field_name: str,
        field_value: str,
        document_id: str | None = None,
        operation: str | None = None,
        collection_name: str | None = None,
        find_in_originals: bool | None = False,
        find_in_modifies: bool | None = False,
    ) -> list[AuditLog]:

        query = {}

        if document_id:
            query["document_id"] = document_id
        if operation:
            query["operation"] = operation
        if collection_name:
            query["collection_name"] = collection_name

        if find_in_originals and find_in_modifies:
            query["$or"] = [
                {f"original.{field_name}": field_value},
                {f"modified.{field_name}": field_value},
            ]
        elif find_in_originals:
            query[f"original.{field_name}"] = field_value
        elif find_in_modifies:
            query[f"modified.{field_name}"] = field_value

        results = self.collection.find(query)
        return [self._map_to_model(bot) for bot in results]
    
    def insert_one(self, data: AuditLog) -> str:
        delattr(data, "id")
        result = self.collection.insert_one(data.model_dump())
        return str(result.inserted_id)

    def insert_many(self, data: List[AuditLog]) -> List[str]:
        data_list = [delattr(d.model_dump(), "id") for d in data]
        result = self.collection.insert_many(data_list)
        return [str(id_) for id_ in result.inserted_ids]

    def delete_one(self, id: str) -> int:
        query = {"_id": ObjectId(id)}
        result = self.collection.delete_one(query)
        return result.deleted_count

