from fastapi import UploadFile,APIRouter, Depends,status
from beanie import PydanticObjectId
from app.plant.models import PlantModel, PlantUpdate
from app.plant.service import PlantService
from app.utils.class_based_views import cbv
from app.schemas.api import ResponseStatus,Response

plant_router = APIRouter()


@cbv(plant_router)
class PlantRouter:
    # user: User = Depends(get_current_active_user)
    _service: PlantService = Depends(PlantService)

    @plant_router.post("/", status_code=status.HTTP_201_CREATED)
    async def create(self, plant: PlantModel):
        result = await self._service.create(plant)
        return Response(
            message="Plant Created Successfully",
            success=True,
            status=ResponseStatus.CREATED,
            data=result,
        )

    @plant_router.patch("/{id}", status_code=status.HTTP_200_OK)
    async def update(self, id: PydanticObjectId, plant: PlantUpdate):
        result = await self._service.update(plant, id)
        return Response(
            message="Plant Updated Successfully",
            success=True,
            status=ResponseStatus.UPDATED,
            data=result
        )

    @plant_router.delete("/{id}", status_code=status.HTTP_200_OK)
    async def delete(self, id: PydanticObjectId):
        result = await self._service.delete(id)
        return Response(
            message="Plant Deleted Successfully",
            success=True,
            status=ResponseStatus.DELETED,
            data=result,
        )

    @plant_router.get("/{id}", status_code=status.HTTP_200_OK)
    async def get(self, id: PydanticObjectId):
        result = await self._service.get(id)
        return Response(
            message="Plant Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @plant_router.get("/", status_code=status.HTTP_200_OK)
    async def get_all(self):
        result = await self._service.get_all()
        return Response(
            message="Plant Retrieved Successfully",
            success=True,
            status=ResponseStatus.SUCCESS,
            data=result,
        )

    @plant_router.post("/upload", status_code=status.HTTP_201_CREATED)
    async def upload_plants(self, file: UploadFile):
        return await self._service.upload_excel(await file.read())