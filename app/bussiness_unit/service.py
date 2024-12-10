from beanie import PydanticObjectId
from fastapi import HTTPException, status
import pandas as pd

from app.bussiness_unit.models import (
    BussinessUnit,
    BussinessUnitModel,
    BussinessUnitRequest,
)
from app.schemas.api import Response, ResponseStatus


class BussinessUnitService:
    def __init__(self):
        pass

    async def create(self, data: BussinessUnitRequest):

        values = data.model_dump()

        bussiness_unit = await BussinessUnit.find_one(BussinessUnit.name == values.get("name"))
        if bussiness_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    message="Bussiness Unit already exists",
                    success=False,
                    status=ResponseStatus.ALREADY_EXIST,
                    data=None,
                ),
            )

        company = BussinessUnit(**values)
        await company.insert()
        return company

    async def update(self, data: BussinessUnitRequest, id: PydanticObjectId):

        values = data.model_dump(exclude_none=True)
        bussiness_unit = await BussinessUnit.find_one(BussinessUnit.id == id)

        if not bussiness_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    message="Company not found",
                    success=False,
                    status=ResponseStatus.DATA_NOT_FOUND,
                    data=None,
                ),
            )

        if values["name"]:
            bussiness_unit.name = values["name"]

        await bussiness_unit.save()
        return bussiness_unit

    async def delete(self, id: str):
        bussiness_unit = await BussinessUnit.find_one(BussinessUnit.name == id)
        if not bussiness_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    message="BussinessUnit not found",
                    success=False,
                    status=ResponseStatus.DATA_NOT_FOUND,
                    data=None,
                ),
            )
        await bussiness_unit.delete()
        return bussiness_unit

    async def get(self, bussiness_unit_id: PydanticObjectId):
        bussiness_unit = await BussinessUnit.find_one(
            BussinessUnit.id == bussiness_unit_id
        )
        if not bussiness_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    message="Bussiness Unit not found",
                    success=False,
                    status=ResponseStatus.DATA_NOT_FOUND,
                    data=None,
                ),
            )
        return bussiness_unit

    async def get_all(self):
        bussiness_unit = await BussinessUnit.find_all().to_list()
        return bussiness_unit

    async def upload_excel(self, file: bytes):
        try:
            df = pd.read_excel(file)

            for _, row in df.iterrows():
                bussiness_unit_data = BussinessUnitModel(
                    name=row["Name"],
                )
                bussiness_unit = await BussinessUnit.find_one(
                    BussinessUnit.name == bussiness_unit_data.name
                )
                if bussiness_unit:
                    await bussiness_unit.set(bussiness_unit_data.model_dump())
                else:
                    await self.create(bussiness_unit_data)

            return Response(
                message="Bussiness Unit imported from Excel file successfully",
                success=True,
                status=ResponseStatus.CREATED,
                data=None,
            )
        except Exception as e:
            print(e)
