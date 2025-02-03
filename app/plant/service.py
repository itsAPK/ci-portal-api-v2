from beanie import PydanticObjectId
import pandas as pd
from fastapi import HTTPException, status,BackgroundTasks
from app.employee.models import Employee
from app.plant.models import AssignCIHeadUser, Plant, PlantModel, PlantUpdate
from app.schemas.api import Response
from app.schemas.api import ResponseStatus


class PlantService:
    def __init__(self):
        pass

    async def create(self, data: PlantModel):

        values = data.model_dump()
        

        plant = await Plant.find_one(Plant.name == values.get("name"))
        if plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Plant already exists',
                    "success":False,
                    "status":ResponseStatus.ALREADY_EXIST.value,
                    "data":plant,
                },
            )

        plant = Plant(**values)
        await plant.insert()
        return plant

    async def update(self, data: PlantUpdate,id : PydanticObjectId):
        values = data.model_dump(exclude_none=True)
        
        plant = await Plant.find_one(Plant.id == id)
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Plant not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )   
        if values.get("name"):
            plant.name = values.get("name")

        if values.get("plant_code"): 
            plant.plant_code = values.get("plant_code")

        await plant.save()
        return plant

    async def delete(self, id: PydanticObjectId):
        plant = await Plant.find_one(Plant.id == id)
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                 detail={
                    "message":'Plant not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )
        await plant.delete()
        return plant

    async def get(self, plant_id: PydanticObjectId):
        plant = await Plant.find_one(Plant.id == plant_id)
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Plant not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )
        return plant

    async def get_all(self):
        plants = await Plant.find_all().to_list()
        return plants

    async def upload_excel(self, file: bytes):
        try:
            df = pd.read_excel(file)

            for _, row in df.iterrows():
                plant_data = PlantModel(
                    name=row["Plant Name"],
                    plant_code=str(row["Plant Code"])
                )
                plant = await Plant.find_one(Plant.name == plant_data.name)
                print(plant)
                if plant:
                    plant.name = plant_data.name
                    plant.plant_code = plant_data.plant_code
                    await plant.save()
                else:
                    await self.create(plant_data)

            return Response(
                message="plants imported from Excel file successfully",
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
    
    async def upload_excel_in_background(self, background_tasks: BackgroundTasks, file: bytes):
        background_tasks.add_task(self.upload_excel, file)
        print("Excel file upload started in the background.")
        return Response(
            message="Excel file upload is in progress.",
            success=True,
            status=ResponseStatus.ACCEPTED,
            data=None,
        )
            
            
    async def assign_ci_head(self, data : AssignCIHeadUser):
        values = data.model_dump(exclude_none=True)
        print(data)
        plant = await Plant.get(values.get("plant_id"))
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message":'Plant not found',
                    "success":False,
                    "status":ResponseStatus.DATA_NOT_FOUND.value,
                    "data":None,
                },
            )
        if data.ci_head:
            ci_head = await Employee.get(data.ci_head)
            if not ci_head:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message":'CI Head not found',
                        "success":False,
                        "status":ResponseStatus.DATA_NOT_FOUND.value,
                        "data":None,
                    },
                )
            plant.ci_head = ci_head
        if data.ci_team:
            ci_team = await Employee.get(data.ci_team)
            if not ci_team:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message":'CI Team not found',
                        "success":False,
                        "status":ResponseStatus.DATA_NOT_FOUND.value,
                        "data":None,
                    },
                )
            plant.ci_team = ci_team
        if data.cs_head:
            cs_head = await Employee.get(data.cs_head)
            if not cs_head:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message":'CI Team not found',
                        "success":False,
                        "status":ResponseStatus.DATA_NOT_FOUND.value,
                        "data":None,
                    },
                )
            plant.cs_head = cs_head
        if data.lof:
            lof = await Employee.get(data.lof)
            if not lof:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message":'LOF not found',
                        "success":False,
                        "status":ResponseStatus.DATA_NOT_FOUND.value,
                        "data":None,
                    },
                )
            print(lof)
            plant.lof = lof
            
        if data.hod:
            hod = await Employee.get(data.hod)
            if not hod:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message":'CI Team not found',
                        "success":False,
                        "status":ResponseStatus.DATA_NOT_FOUND.value,
                        "data":None,
                    },
                )
            plant.hod = hod
            
        await plant.save()
        return plant
    
    async def delete_all_plants(self):
        return await Plant.get_motor_collection().drop()