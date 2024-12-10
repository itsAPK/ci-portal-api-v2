from beanie import PydanticObjectId
from fastapi import BackgroundTasks, HTTPException, status
import pandas as pd
from app.core.databases import parse_json
from app.employee.models import Employee
from app.schemas.api import Response, ResponseStatus
from app.training.models import Training, TrainingModel, TrainingRequest, TrainingUpdate


class TrainingService:
    def __init__(self):
        pass

    async def create_training(self, data: TrainingRequest):
        values = data.model_dump()

        employee = await Employee.find_one(
            Employee.employee_id == values["employee_id"]
        )

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

        training = Training(**values)
        await training.insert()
        return training

    async def update_training(self, data: TrainingUpdate, id: PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        training = await Training.get(id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "training not found",
                    "success": False,
                    "status": ResponseStatus.NOT_FOUND.value,
                    "data": None,
                },
            )
        for key, value in values.items():
            if value is not None and hasattr(training, key):
                setattr(training, key, value)

        await training.save()
        return training

    async def delete_training(self, id: PydanticObjectId):
        training = await Training.get(id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "training not found",
                    "success": False,
                    "status": ResponseStatus.NOT_FOUND.value,
                    "data": None,
                },
            )
        training.is_active = False
        await training.save()
        return training

    async def count_training(self):
        return await Training.find().count()

    async def query_count_training(self, filter):
        results = await Training.aggregate(filter).to_list()
        return len(results)

    async def query_training(self, filter: list[dict], page: int, page_size: int):
        skip = (page - 1) * page_size
        query = [] + filter
        total_items = await self.query_count_training(query)
        results = await Training.aggregate(
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

    async def export_query_training(self, filter: list[dict]):

        query = [] + filter
        total_items = await self.query_count_training(query)
        results = await Training.aggregate(query).to_list()

        return {
            "total_items": total_items,
            "data":  parse_json(results),
        }

    async def get_training(self, id: PydanticObjectId):
        training = await Training.find_one(Training.id == id)
        if not training:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "training not found",
                    "success": False,
                    "status": ResponseStatus.NOT_FOUND.value,
                    "data": None,
                },
            )
        return training

    async def get_all_training(self, page: int, page_size: int):
        skip = (page - 1) * page_size
        total_items = await self.count_training()
        results = await Training.find().skip(skip).limit(page_size).to_list()
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

    async def upload_training(self, file: bytes):
        try:
            df = pd.read_excel(file)

            for _, row in df.iterrows():
                training_data = TrainingModel(
                    employee_id=str(row["Employee No."]),
                    name=row["Name"],
                    department=row["Department"],
                    grade=row["Grade"],
                    working_location=row["Working Location"],
                    bussiness_unit=row["Business Unit"],
                    plant=row["Plant"],
                    company=row["Company"],
                    batch=row["Batch"],
                    year=row["Year"],
                    trainer=row["Trainer"],
                    category=row["Category"],
                )

                await self.create_training(training_data)

            return Response(
                message="training imported from Excel file successfully",
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

    async def upload_training_in_background(
        self, background_tasks: BackgroundTasks, file: bytes
    ):
        background_tasks.add_task(self.upload_training, file)
        return Response(
            message="Excel file upload is in progress.",
            success=True,
            status=ResponseStatus.ACCEPTED,
            data=None,
        )
