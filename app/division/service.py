from beanie import PydanticObjectId
import pandas as pd
from fastapi import HTTPException, status
from app.division.models import Division, DivisionModel, DivisionUpdate
from app.schemas.api import Response, ResponseStatus


class DivisionService:
    def __init__(self):
        pass

    async def create(self, data: DivisionModel):

        values = data.model_dump()

        division = await Division.find_one(Division.name == values.get("name"))
        if division:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":"division already exists",
                    "success":False,
                    "status":ResponseStatus.ALREADY_EXIST.value,
                    "data":None,
                },
            )

        division = Division(**values)
        await division.insert()
        return division

    async def update(self, data: DivisionUpdate,id : PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        
        division = await Division.find_one(Division.id == id)
        if not division:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":"division not found",
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                }
            )

        if values.get("name"):
            division.name = values.get("name")

        if values.get("division_code"): 
            division.division_code = values.get("division_code")

        await division.save()
        return division

    async def delete(self, id: PydanticObjectId):
            division = await Division.find_one(Division.id == id)
        
            if division:
                    await division.delete()
                    return division
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=Response(
                        message="division not found",
                        success=False,
                        status=ResponseStatus.DATA_NOT_FOUND.value,
                        data=None,
                    ),
                )
           
       

    async def get(self, division_id: PydanticObjectId):
        division = await Division.find_one(Division.id == division_id)
        if not division:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    message="division not found",
                    success=False,
                    status=ResponseStatus.DATA_NOT_FOUND.value,
                    data=None,
                ),
            )
        return division

    async def get_all(self):
        division = await Division.find_all().to_list()
        return division

    async def upload_excel(self, file: bytes):
        try:
            df = pd.read_excel(file)

            for _, row in df.iterrows():
                division_data = DivisionModel(
                    name=row["Division Name"],
                    division_code=str(row["Division Code"])
                )
                division = await Division.find_one(Division.name == division_data.name)
                print(division)
                if division:
                    await division.set({Division.name:division_data.name,Division.division_code:division_data.division_code})
                else:
                    await self.create(division_data)

            return Response(
                message="division imported from Excel file successfully",
                success=True,
                status=ResponseStatus.CREATED,
                data=None,
            )
        except Exception as e:
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":str(e),
                    "success":False,
                    "status":ResponseStatus.FAILED.value,
                    "data":None,
                },
            )

