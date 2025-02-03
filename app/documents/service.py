
from beanie import PydanticObjectId
from fastapi import HTTPException,status
from app.documents.models import Documents, DocumentsModel, DocumentsUpdate
from app.schemas.api import ResponseStatus


class DocumentsService:
    def __init__(self):
        pass
    
    async def create(self, data: Documents):
        values = data.model_dump()
        document = Documents(**values)
        await document.insert()
        return document
    
    async def get(self, document_id: PydanticObjectId):
        document = await Documents.get(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Document not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )
        return document
    
    async def get_all(self):
        documents = await Documents.find_all().to_list()
        return documents
    
    async def delete(self, id: PydanticObjectId):
        document = await Documents.get(id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Document not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )
        await document.delete()
        return document
    
    
    async def delete_all(self):
        return await Documents.get_motor_collection().drop()