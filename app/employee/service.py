from beanie import PydanticObjectId
from fastapi import BackgroundTasks, HTTPException, status
import pandas as pd
from datetime import datetime

from app.core.databases import parse_json
from app.employee.models import (
   
    EmployeeModel,
    EmployeeUpdate,
    Employee,
    PlantChange,
    PlantChangeRequest,
    PlantChangeStatus,
)
from app.plant.models import Plant
from app.schemas.api import Response, ResponseStatus
from app.core.security import get_password_hash
from dateutil import parser

from app.utils import process_role


class EmployeeService:
    def __init__(self):
        pass

    async def create(self, data: EmployeeModel):
        values = data.model_dump()

        employee = await Employee.find_one(
            Employee.employee_id == values["employee_id"]
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
        p = values["password"] if values["password"] else "amararaja"
        password = get_password_hash(p)
        values.pop("password")
        employee = Employee(**values, password=password)
        await employee.insert()
        return employee

    async def update(self, data: EmployeeUpdate, id: PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        employee = await Employee.get(id)
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
        employee = await Employee.get(id)
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
        return await Employee.find().count()

    async def query_count(self, filter):
        results = await Employee.aggregate(filter).to_list()
        return len(results)

    async def query(self, filter: list[dict], page: int, page_size: int):
        skip = (page - 1) * page_size
        query = [] + filter
        total_items = await self.query_count(query)
        print(query)
        results = await Employee.aggregate(
            query + [{"$skip": skip}, {"$limit": page_size}]
        ).to_list()
        total_pages = (total_items + page_size - 1) // page_size
        remaining_items = max(0, total_items - (skip + len(results)))
        print(results)
        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
            "remaining_items": remaining_items,
            "data": parse_json(results),
        }

    async def export_query(self, filter: list[dict]):
        print(filter)
        query = [] + filter
        total_items = await self.query_count(query)
        results = await Employee.aggregate(query).to_list()
        print(results)
        return {
            "total_items": total_items,
            "data": parse_json(results),
        }

    async def get(self, id: PydanticObjectId):
        employee = await Employee.find_one(Employee.id == id)
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
        employee = await Employee.find_one(Employee.employee_id == employee_id)
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

    async def get_by_email(self, email: str):
        employee = await Employee.find_one(Employee.email == email)
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
                try:
                    employee_data = EmployeeModel(
                        name=row["Name"],
                        employee_id=str(row["Employee No."]),
                        plant=row["Plant"],
                        company=row["Company"],
                        department=row["Department"],
                        email=str(row["E-Mail"]),
                        date_of_birth=(
                            row["Date of Birth"].to_pydatetime()
                            if hasattr(row["Date of Birth"], "to_pydatetime")
                            else parser.parse(str(row["Date of Birth"]))
                        ),
                        date_of_joining=(
                            row["Date of Joining"].to_pydatetime()
                            if hasattr(row["Date of Joining"], "to_pydatetime")
                            else (
                                parser.parse(str(row["Date of Joining"]))
                                if row["Date of Joining"]
                                else None
                            )
                        ),
                        grade=row["Grade"],
                        role=process_role(row["Role"]),
                        designation=row["Designation"],
                        working_location=row["Working Location"],
                        bussiness_unit=row["Business Unit"],
                    )
                    employee = await Employee.find_one(
                        Employee.employee_id == employee_data.employee_id
                    )
                    if employee:
                        await employee.set(
                            {
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
                            }
                        )
                    else:
                        await self.create(employee_data)
                except Exception as e:
                    print(e)
                    continue

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
                    "message": str(e),
                    "success": False,
                    "status": ResponseStatus.FAILED.value,
                    "data": None,
                },
            )

    async def upload_excel_in_background(
        self, background_tasks: BackgroundTasks, file: bytes
    ):
        background_tasks.add_task(self.upload_excel, file)
        return Response(
            message="Excel file upload is in progress.",
            success=True,
            status=ResponseStatus.ACCEPTED,
            data=None,
        )

    async def create_plant_change(self, data: PlantChangeRequest):
        if not data.employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee_id is required",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        employee = await Employee.get(data.employee_id)

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        requested_plant = await Plant.get(data.requested_plant_id)
        if not requested_plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "requested_plant not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        current_plant = await Plant.find_one(Plant.name == employee.plant)
        if not current_plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "current plant not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        if employee.plant == requested_plant.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Requested Plant is same as current plant",
                    "success": False,
                    "status": ResponseStatus.SERVICE_UNAVAILABLE.value,
                    "data": None,
                },
            )

        plant_change = PlantChange(
            **data.model_dump(),
            employee=employee,
            current_plant=current_plant,
            requested_plant=requested_plant,
        )
        await plant_change.insert()
        return plant_change

    async def get_plant_changes(self, employee_id: str):
        employee = await Employee.find_one(Employee.employee_id == employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        plant_changes = await PlantChange.find(
            PlantChange.employee == employee
        ).to_list()
        return plant_changes

    async def palnt_change_query_count(self, filter: list[dict]):
        results = await Employee.aggregate(filter).to_list()
        return len(results)

    async def plant_change_query(self, filter: list[dict], page: int, page_size: int):
        skip = (page - 1) * page_size
        query = [] + filter
        total_items = await self.palnt_change_query_count(query)
        results = await PlantChange.aggregate(
            query + [{"$skip": skip}, {"$limit": page_size}]
        ).to_list()
        total_pages = (total_items + page_size - 1) // page_size
        remaining_items = max(0, total_items - (skip + len(results)))

        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size,
            "remaining_items": remaining_items,
            "data": parse_json(results),
        }

    async def approve_plant_change(self, id: PydanticObjectId):
        plant_change = await PlantChange.find_one(PlantChange.id == id)
        if not plant_change:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        if plant_change.status != PlantChangeStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": f"Requested status is already {plant_change.status}",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await plant_change.set({"status": PlantChangeStatus.approved})
        employee = await Employee.find_one(
            Employee.employee_id == plant_change.employee.employee_id
        )
        employee.set({"plant": plant_change.requested_plant.name})
        await employee.save()
        return plant_change

    async def reject_plant_change(self, id: PydanticObjectId):
        plant_change = await PlantChange.find_one(PlantChange.id == id)
        if not plant_change:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "employee not found",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )
        if plant_change.status != PlantChangeStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": f"Requested status is already {plant_change.status}",
                    "success": False,
                    "status": ResponseStatus.DATA_NOT_FOUND.value,
                    "data": None,
                },
            )

        await plant_change.set({"status": PlantChangeStatus.rejected})
        return plant_change
    
