from beanie import PydanticObjectId
from fastapi import HTTPException, status
from app.archive.models import Archive, ArchiveCumulative, ArchiveCumulativeRequest, ArchiveRequest
from app.core.databases import parse_json
from app.employee.models import Employee
from app.schemas.api import ResponseStatus


class ArchiveService:
    def __init__(self):
        pass

    async def create(self, data: ArchiveRequest):
        print(data)
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
        print(employee)
        project_leader = await Employee.get(data.project_leader)
      
        if not project_leader:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Project Leader not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        data.uploaded_by = employee
        data.project_leader = project_leader
        print(project_leader)
        try:
            archive = Archive(
                **data.model_dump()
            )
            await archive.insert()
        except Exception as e:
            print(e)
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


    async def delete_all(self):
        return await Archive.get_motor_collection().drop()
    
    
    
class ArchiveCumulativeService:
    def __init__(self):
        pass

    async def create(self, data: ArchiveCumulativeRequest):
        print(data)
        values = data.model_dump()
      
        archive = ArchiveCumulative(
                **values
            )
        await archive.insert()
        
        return archive
    
    
    async def get_all():
        return await ArchiveCumulative.find(fetch_links=True).to_list()

    async def get(self, id: PydanticObjectId):
        archive = await ArchiveCumulative.find_one(ArchiveCumulative.id == id,fetch_links=True)
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
    
    async def query(self, filter: list[dict], page: int, page_size: int):
        skip = (page - 1) * page_size
        query = [] + filter
        total_items = await self.query_count(query)
        results = await ArchiveCumulative.find(fetch_links=True).aggregate(
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
        
    async def export(self, filter: list[dict]):
        results = await ArchiveCumulative.aggregate(filter).to_list()
        return {
            "data": parse_json(results),
            "success": True,
            "status": ResponseStatus.SUCCESS.value,
            "message": "Successfully exported data",
        }
    
    async def query_count(self, filter):
        results = await ArchiveCumulative.aggregate(filter).to_list()
        return len(results)
    
    async def delete(self, id: PydanticObjectId):
        archive = await ArchiveCumulative.find_one(Archive.id == id)
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

    async def delete_all(self):
        return await ArchiveCumulative.get_motor_collection().drop()