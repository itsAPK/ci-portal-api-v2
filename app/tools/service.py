from beanie import PydanticObjectId
from fastapi import HTTPException, status
from app.core.databases import parse_json
from app.schemas.api import ResponseStatus
from app.tools.models import Tools, ToolsModel, ToolsUpdate


class ToolsService:
    def __init__(self):
        pass

    async def create(self, data: ToolsModel):
        values = data.model_dump()
        tool = await Tools.find_one(Tools.name == values.get("name"))
        if tool:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Tool already exists",
                    "success": False,
                    "status": ResponseStatus.ALREADY_EXIST.value,
                    "data": None,
                },
            )
        tool = Tools(**values)
        await tool.insert()
        return tool

    async def update(self, data: ToolsUpdate, id: PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        status = True if values.get("status") == True else False
        tool = await Tools.get(id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Tool not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        print(values.get("status"))
        if values.get("name"):
            tool.name = values.get("name")
        if values.get("category"):
            tool.category = values.get("category")
        if values.get("status") == True:
            tool.status = True
        else:
            tool.status = False
        a = await tool.save()
        print(a)
        return tool

    async def delete(self, id: PydanticObjectId):
        tool = await Tools.find_one(Tools.id == id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Tool not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        await tool.delete()
        return tool

    async def get(self, tool_id: PydanticObjectId):
        tool = await Tools.find_one(Tools.id == tool_id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Tool not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        return tool

    async def get_all(self, page: int, page_size: int):
        skip = (page - 1) * page_size
        total_items = await self.count()
        results = await Tools.find().skip(skip).limit(page_size).to_list()
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
        return await Tools.find().count()

    async def query(self, filter: list[dict], page: int, page_size: int):
        print(filter)
        skip = (page - 1) * page_size
        query = [] + filter
        total_items = await self.query_count(query)
        results = await Tools.aggregate(
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

    async def query_export(self, filter: list[dict]):

        query = [] + filter
        results = await Tools.aggregate(query).to_list()
        print(results)
        return {
            "data": parse_json(results),
        }

    async def query_count(self, filter):
        results = await Tools.aggregate(filter).to_list()
        return len(results)
