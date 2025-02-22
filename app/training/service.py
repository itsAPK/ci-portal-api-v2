from beanie import PydanticObjectId
from fastapi import BackgroundTasks, HTTPException, status
import pandas as pd
from app.core.databases import parse_json
from app.employee.models import Employee
from app.schemas.api import Response, ResponseStatus
from app.training.models import CumulativeTraining, Training, TrainingModel, TrainingRequest, TrainingUpdate,CumulativeTrainingRequest,CumulativeTrainingUpdate


class TrainingService:
    def __init__(self):
        pass

    async def create_training(self, data: TrainingRequest):
        values = data.model_dump()

        # employee = await Employee.find_one(
        #     Employee.employee_id == values["employee_id"]
        # )

        # if not employee:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail={
        #             "message": "employee not found",
        #             "success": False,
        #             "status": ResponseStatus.NOT_FOUND.value,
        #             "data": None,
        #         },
        #     )

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
        try:
            # Find the training by ID
            training = await Training.get(id)
            
            if not training:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "message": "Training not found",
                        "success": False,
                        "status": ResponseStatus().NOT_FOUND,
                        "data": None,
                    },
                )

            # Perform the deletion
            await training.delete()

            return {"message": "Training successfully deleted", "data": training}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": f"Error deleting training: {str(e)}",
                    "success": False,
                    "status": "Error",
                    "data": None,
                },
            )
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
                try:
                    training_data = TrainingModel(
                        employee_id=str(row["Employee No."]),
                        name=row["Name"],
                        department=row["Department"],
                        grade=row["Grade"],
                        working_location=row["Working Location"],
                        bussiness_unit=row["Bussiness Unit"],
                        plant=row["Plant"],
                        company=row["Company"],
                        batch=row["Batch"],
                        year=row["Year"],
                        trainer=row["Trainer"],
                        category=row["Category"],
                    )
                

                    await self.create_training(training_data)
                except Exception as e:
                    print('error-training-upload', e)
                    continue

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
        
        
    async def delete_all_trainings(self):
        return await Training.get_motor_collection().drop()

class CumulativeTrainingService:
    def __init__(self):
        pass
    
    
    async def create(self,data : CumulativeTraining):
        values = data.model_dump()
        
        cumulative_training = CumulativeTraining(**values)
        await cumulative_training.insert()
        return cumulative_training

    async def update(self,data : CumulativeTrainingUpdate,id : PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        cumulative_training = await CumulativeTraining.get(id)
        if not cumulative_training:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "cumulative training not found",
                    "success": False,
                    "status": ResponseStatus.NOT_FOUND.value,
                    "data": None,
                },
            )
        for key, value in values.items():
            if value is not None and hasattr(cumulative_training, key):
                setattr(cumulative_training, key, value)

        await cumulative_training.save()
        return cumulative_training

    async def delete(self,id : PydanticObjectId):
        try:
            # Find the training by ID
            cumulative_training = await CumulativeTraining.get(id)
            
            if not cumulative_training:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "message": "Cumulative Training not found",
                        "success": False,
                        "status": ResponseStatus().NOT_FOUND,
                        "data": None,
                    },
                )

            # Perform the deletion
            await cumulative_training.delete()

            return {"message": "Cumulative Training successfully deleted", "data": cumulative_training}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": f"Error deleting cumulative training: {str(e)}",
                    "success": False,
                    "status": "Error",
                    "data": None,
                },
            )
    async def count(self):
        return await CumulativeTraining.find().count()

    async def query_count(self,  filter: list[dict]):
        results = await CumulativeTraining.aggregate(filter).to_list()
        return len(results)

    async def query(self, filter: list[dict], page: int, page_size: int):
        skip = (page - 1) * page_size
        query = [] + filter
        total_items = await self.query_count(query)
        results = await CumulativeTraining.aggregate(
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

    async def export_query(self, filter: list[dict]):

        query = [] + filter
        total_items = await self.query_count(query)
        results = await CumulativeTraining.aggregate(query).to_list()

        return {
            "total_items": total_items,
            "data":  parse_json(results),
        }

    async def get(self, id: PydanticObjectId):
        cumulative_training = await CumulativeTraining.find_one(CumulativeTraining.id == id)
        if not cumulative_training:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "cumulative training not found",
                    "success": False,
                    "status": ResponseStatus.NOT_FOUND.value,
                    "data": None,
                },
            )
        return cumulative_training

    async def get_all():
        results = await CumulativeTraining.find().to_list()
        return {
            "message": "Cumulative Training Retrieved Successfully",
            "success": True,
            "status": ResponseStatus.RETRIEVED,
            "data": results,
        }
        