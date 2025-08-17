from bson import ObjectId
from typing import Generic, TypeVar, List, Type
from math import ceil
from contextlib import suppress

from pydantic.v1 import BaseModel
from pymongo import MongoClient, ReturnDocument

from sharedkernel.objects.user_info import current_user_info
from sharedkernel.string_extentions import camel_to_snake
from sharedkernel.objects.base_document import BaseAuditDocument
from sharedkernel.database.mongo_generic_audit_repository import MongoGenericAuditRepository
from sharedkernel.database.audit_model import (
    AuditLog,
    AuditOperation
)
from sharedkernel.diff_utils import generate_clean_diff
from sharedkernel.database.pagination_response_dto import PaginationResponseDto

T = TypeVar("T", bound=BaseModel)

class MongoGenericRepository(Generic[T]):
    def __init__(self, database: MongoClient, model: Type[T], audit_collection_name: str | None = None):
        self.database = database
        self.__collection_name = camel_to_snake(model.__name__)
        self.collection = self.database[self.__collection_name]
        self.model = model
        self.audit_collection = MongoGenericAuditRepository(
            database=database,
            audit_collection_name=audit_collection_name
        )

    def _map_to_model(self, document: dict) -> T:
        document["id"] = str(document.pop("_id"))
        return self.model.model_validate(document)

    def find_one(self, id: str) -> T:
        query = {"_id": ObjectId(id), "is_deleted": False}
        result = self.collection.find_one(query)
        return self._map_to_model(result) if result else None   

    def insert_one(self, data: T) -> str:
        delattr(data, "id")
        result = self.collection.insert_one(data.model_dump())
        
        # For Audit log
        with suppress(Exception):
            if isinstance(data, BaseAuditDocument):
                document = AuditLog(
                    user_id=current_user_info.get().nameid,
                    collection_name=self.__collection_name,
                    document_id=str(result.inserted_id),
                    operation=AuditOperation.CREATE,
                    original=None,
                    modified=data.model_dump(),
                )
                self.audit_collection.insert_one(document)

        return str(result.inserted_id)

    def insert_many(self, data: List[T]) -> List[str]:
        data_list = [delattr(d.model_dump(), "id") for d in data]
        result = self.collection.insert_many(data_list)

        # For Audit log
        with suppress(Exception):
            if len(result.inserted_ids) > 0:
                if isinstance(data[0], BaseAuditDocument):
                    documents = []
                    for i, d in enumerate(data):
                        document = AuditLog(
                            user_id=current_user_info.get().nameid,
                            collection_name=self.__collection_name,
                            document_id=str(result.inserted_ids[i]),
                            operation=AuditOperation.CREATE,
                            original=None,
                            modified=d.model_dump(),
                        )
                        documents.append(document)
                    
                    self.audit_collection.insert_many(documents)

        return [str(id_) for id_ in result.inserted_ids]

    def update_one(self, id: str, data: T, is_audit = True) -> int:
        delattr(data, "id")

        query = {"_id": ObjectId(id)}
        before_dict = self.collection.find_one_and_update(
            query,
            {"$set": data.model_dump()},
            return_document=ReturnDocument.BEFORE
        )

        # For Audit log
        if isinstance(data, BaseAuditDocument) and is_audit:
            with suppress(Exception):
                before_model = self.model(**before_dict)
                
                diff_data = generate_clean_diff(before_model, data)
                old_data, new_data = diff_data["original"], diff_data["modified"]

                if new_data:
                    document = AuditLog(
                        user_id=current_user_info.get().nameid,
                        collection_name=self.__collection_name,
                        document_id=id,
                        operation=AuditOperation.UPDATE,
                        original=old_data,
                        modified=new_data,
                    )
                    
                    self.audit_collection.insert_one(document)

        return 1

    def delete_one(self, id: str) -> int:
        query = {"_id": ObjectId(id)}
        result = self.collection.delete_one(query)
        return result.deleted_count

    def get_all(self, page_number=1, page_size=10) -> List[T]:
        skip_count = (page_number - 1) * page_size
        query = {"is_deleted": False}
        result = self.collection.find(query).skip(skip_count).limit(page_size)
        return [self._map_to_model(doc) for doc in result]

    def paginate(
        self,
        query: dict,
        page_number: int,
        page_size: int,
        sort_field: str = "_id",
        sort_order: int = -1,
    ) -> PaginationResponseDto:
        
        skip_count = (page_number - 1) * page_size
        total_items = self.collection.count_documents(query)

        cursor = (
            self.collection.find(query)
            .sort(sort_field, sort_order)
            .skip(skip_count)
            .limit(page_size)
        )

        return PaginationResponseDto(
            data=[self._map_to_model(doc) for doc in cursor],
            total_items=total_items,
            page_size=page_size,
            current_page=page_number,
            total_pages=ceil(total_items / page_size) if page_size else 1,
            has_next=(page_number * page_size) < total_items,
            has_prev=page_number > 1,
        )