from beanie import PydanticObjectId
import pandas as pd
from fastapi import HTTPException, status
from app.department.models import Department, DepartmentModel, DepartmentUpdate
from app.schemas.api import Response,ResponseStatus

class DepartmentService:    
    def __init__(self):
        pass

    async def create(self, data: DepartmentModel):
        values = data.model_dump()
        department = await Department.find_one(Department.name == values.get("name"))
        if department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Department already exists',
                    "success":False,
                    "status":ResponseStatus.ALREADY_EXIST.value,
                    "data":department,
                },
            )
        department = Department(**values)
        await department.insert()
        return department

    async def update(self, data: DepartmentUpdate,id : PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        
        department = await Department.find_one(Department.id == id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Department not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )   
        if values.get("name"):
            department.name = values.get("name")

        if values.get("department_code"): 
            department.department_code = values.get("department_code")

        await department.save()
        return department

    async def delete(self, id: PydanticObjectId):
        department = await Department.find_one(Department.id == id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                 detail={
                    "message":'Department not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )
        await department.delete()
        return department

    async def get(self, department_id: PydanticObjectId):
        department = await Department.find_one(Department.id == department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Department not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )
        return department

    async def get_all(self):
        departments = await Department.find_all().to_list()
        return departments

    async def upload_excel(self, file: bytes):
        try:
            df = pd.read_excel(file)

            for _, row in df.iterrows():
                department_data = DepartmentModel(
                    name=row["Department Name"],
                    department_code=str(row["Department Code"])
                )
                department = await Department.find_one(Department.name == department_data.name)
                print(department)
                if department:
                    await department.set({Department.name:department_data.name,Department.department_code:department_data.department_code})
                else:
                    await self.create(department_data)

            return Response(
                message="departments imported from Excel file successfully",
                success=True,
                status=ResponseStatus.CREATED,
                data=None,
            )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":str(e),
                    "success":False,
                    "status":ResponseStatus.FAILED.value,
                    "data":None,
                },
            )