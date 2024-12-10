from beanie import PydanticObjectId
from fastapi import HTTPException, status
from app.archive.models import Archive, ArchiveRequest
from app.core.databases import parse_json
from app.employee.models import Employee
from app.schemas.api import ResponseStatus


class ArchiveService:
    def __init__(self):
        pass

    async def create(self, data: ArchiveRequest):
        employee = await Employee.get(data.uploaded_by)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data.uploaded_by = employee
        archive = Archive(**data.model_dump())
        await archive.insert()
        return archive
    
    
    async def get(self, archive_id: PydanticObjectId):
        archive = await Archive.find_one(Archive.id == archive_id,fetch_links=True)
        if not archive:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Archive not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )
        return archive
    
    async def get_all(self, page: int, page_size: int):
        skip = (page - 1) * page_size
        total_items = await self.count()
        results = await Archive.find(fetch_links=True).skip(skip).limit(page_size).to_list()
        total_pages = (total_items + page_size - 1) // page_size
        remaining_items = max(0, total_items - (skip + len(results)))
        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
            "data": results,
            "remaining_items": remaining_items,
        }

    async def count(self):
        return await Archive.find().count()
    
    async def query(self, filter: list[dict], page: int, page_size: int):
        skip = (page - 1) * page_size
        query = [] + filter
        total_items = await self.query_count(query)
        results = await Archive.find(fetch_links=True).aggregate(
            query + [{"$skip": skip}, {"$limit": page_size}]
        ).to_list()
        total_pages = (total_items + page_size - 1) // page_size
        remaining_items = max(0, total_items - (skip + len(results)))

        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
            "data": parse_json(results),
            "remaining_items": remaining_items,
        }
    
    async def query_count(self, filter):
        results = await Archive.aggregate(filter).to_list()
        return len(results)
    
    async def delete(self, id: PydanticObjectId):
        archive = await Archive.find_one(Archive.id == id)
        if not archive:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Archive not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )
        await archive.delete()
        return archive
