from beanie import PydanticObjectId
from fastapi import HTTPException, status
import pandas as pd
from app.employee.models import EmployeeModel, EmployeeUpdate, Employee
from app.core.enums import ResponseStatus
from app.schemas.api import Response


class EmployeeService:
    def __init__(self):
        pass

    async def create(self, data: EmployeeModel):
        values = data.model_dump()
        employee = await Employee.find_one(
            EmployeeModel.employee_id == values.get("employee_id")
        )
        if employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee already exists",
                    "success": False,
                    "status": ResponseStatus.ALREADY_EXIST.value,
                    "data": None,
                },
            )
        employee = EmployeeModel(**values)
        await employee.insert()
        return employee

    async def update(self, data: EmployeeUpdate, id: PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        employee = await Employee.find_one(EmployeeModel.id == id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee not found",
                    "success": False,
                    "status": ResponseStatus.NOT_FOUND.value,
                    "data": None,
                },
            )
        for key, value in values.items():
            if value is not None and hasattr(employee, key):
                setattr(employee, key, value)

        await employee.save()
        return employee

    async def delete(self, id: PydanticObjectId):
        employee = await Employee.find_one(EmployeeModel.id == id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee not found",
                    "success": False,
                    "status": ResponseStatus.NOT_FOUND.value,
                    "data": None,
                },
            )
        employee.is_active = False
        await employee.save()
        return employee

    async def count(self):
        return await Employee.find()

    async def query_count(self, filter):
        results = await Employee.aggregate(filter).to_list()
        return len(results)

    async def query(self, filter: list[dict], page: int, page_size: int):
        skip = (page - 1) * page_size
        query = [] + filter
        total_items = await self.query_count(query)
        results = await Employee.aggregate(
            query + [{"$skip": skip}, {"$limit": page_size}]
        ).to_list()
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

    async def get(self, id: PydanticObjectId):
        employee = await Employee.find_one(EmployeeModel.id == id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee not found",
                    "success": False,
                    "status": ResponseStatus.NOT_FOUND.value,
                    "data": None,
                },
            )
        return employee

    async def get_by_employee_id(self, employee_id: str):
        employee = await Employee.find_one(EmployeeModel.employee_id == employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee not found",
                    "success": False,
                    "status": ResponseStatus.NOT_FOUND.value,
                    "data": None,
                },
            )
        return employee

    async def get_all(self, page: int, page_size: int):
        skip = (page - 1) * page_size
        total_items = await self.count()
        results = await Employee.find().skip(skip).limit(page_size).to_list()
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


    async def upload_excel(self, file: bytes):
        try:
            df = pd.read_excel(file)

            for _, row in df.iterrows():
                employee_data = EmployeeModel(
                    name=row["Name"],
                    employee_id=str(row["Employee No."]),
                    plant = row["Plant"],
                    company=row["Company"],
                    department=row["Department"],
                    email = row["Email"],
                    date_of_birth=row["Date of Birth"],
                    date_of_joining=row["Date of Joining"],
                    grade=row["Grade"],
                    role=row["Role"],
 
                )
                employee = await Employee.find_one(Employee.employee_id == employee_data.employee_id)
                print(employee)
                if employee:
                    await employee.set({
                        "name": employee_data.name,
                        "employee_id": employee_data.employee_id,
                        "plant": employee_data.plant,
                        "company": employee_data.company,
                        "department": employee_data.department,
                        "email": employee_data.email,
                        "date_of_birth": employee_data.date_of_birth,
                        "date_of_joining": employee_data.date_of_joining,
                        "grade": employee_data.grade,
                        "role": employee_data.role,
                        "designation": employee_data.designation,
                        "bussiness_unit": employee_data.bussiness_unit,
                        "working_location": employee_data.working_location,
                    })
                else:
                    await self.create(employee_data)

            return Response(
                message="employee imported from Excel file successfully",
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

