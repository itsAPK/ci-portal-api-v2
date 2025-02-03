from beanie import PydanticObjectId
import pandas as pd
from app.company.models import Company, CompanyModel, CompanyUpdate
from fastapi import HTTPException, status,BackgroundTasks

from app.schemas.api import Response, ResponseStatus


class CompanyService:
    def __init__(self):
        pass

    async def create(self, data: CompanyModel):

        values = data.model_dump()

        company = await Company.find_one(Company.name == values.get("name"))
        if company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    message="Company already exists",
                    success=False,
                    status=ResponseStatus.ALREADY_EXIST,
                    data=None,
                ),
            )

        company = Company(**values)
        await company.insert()
        return company

    async def update(self, data: CompanyUpdate, id: PydanticObjectId):

        values = data.model_dump(exclude_none=True)
        company = await Company.find_one(Company.id == id)

        if not company:
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
            company.name = values["name"]

        if values["company_code"]:
            company.company_code = values["company_code"]
        await company.save()
        return company

    async def delete(self, id: PydanticObjectId):
        company = await Company.get(id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    message="Company not found",
                    success=False,
                    status=ResponseStatus.DATA_NOT_FOUND,
                    data=None,
                ),
            )
        await company.delete()
        return company

    async def get(self, company_id: PydanticObjectId):
        company = await Company.find_one(Company.id == company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Response(
                    message="Company not found",
                    success=False,
                    status=ResponseStatus.DATA_NOT_FOUND,
                    data=None,
                ),
            )
        return company

    async def get_all(self):
        companies = await Company.find_all().to_list()
        return companies

    async def upload_excel(self, file: bytes):
        try:
            df = pd.read_excel(file)

            for _, row in df.iterrows():
                company_data = CompanyModel(
                    name=row["Company Name"],
                    company_code=row["Company Code"],
                )
                company = await Company.find_one(Company.name == company_data.name)
                if company:
                    await company.set(company_data.model_dump())
                    await company.save()
                else:
                    await self.create(company_data)

            return Response(
                message="Companies imported from Excel file successfully",
                success=True,
                status=ResponseStatus.CREATED,
                data=None,
            )
        except Exception as e:
            print(e)
            
    async def upload_excel_in_background(self, background_tasks: BackgroundTasks, file: bytes):
        background_tasks.add_task(self.upload_excel, file)
        print("Excel file upload started in the background.")
        return Response(
            message="Excel file upload is in progress.",
            success=True,
            status=ResponseStatus.ACCEPTED,
            data=None,
        )


    async def delete_all_companies(self):
        return await Company.get_motor_collection().drop()