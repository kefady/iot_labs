from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import ProcessedAgentData, ProcessedAgentDataInDB
from app.crud import processed_data as crud
from app.services.websocket_manager import send_data_to_subscribers
from collections import defaultdict

router = APIRouter(tags=["Processed Agent Data"])

@router.post(
    "/",
    response_model=List[ProcessedAgentDataInDB],
    summary="Create processed agent data",
    description="""
    Accepts a list of processed agent data entries and stores them in the database.
    Also pushes the new data to subscribed WebSocket clients in real time.
    """
)
async def create_data(data: List[ProcessedAgentData]):
    created = crud.create_data_batch(data)

    user_data_map = defaultdict(list)
    for item in created:
        user_data_map[item["user_id"]].append(item)

    for user_id, items in user_data_map.items():
        await send_data_to_subscribers(user_id, items)

    return created

@router.get(
    "/",
    response_model=List[ProcessedAgentDataInDB],
    summary="Get all processed agent data",
    description="Returns a list of all processed agent data entries stored in the database."
)
def list_data():
    return crud.list_data()

@router.get(
    "/{data_id}",
    response_model=ProcessedAgentDataInDB,
    summary="Get processed agent data by ID",
    description="Returns a single processed agent data entry by its ID."
)
def get_data(data_id: int):
    result = crud.get_data_by_id(data_id)
    if not result:
        raise HTTPException(status_code=404, detail="Data not found")
    return result

@router.put(
    "/{data_id}",
    response_model=ProcessedAgentDataInDB,
    summary="Update processed agent data by ID",
    description="Updates an existing processed agent data entry by its ID."
)
def update_data(data_id: int, item: ProcessedAgentData):
    result = crud.update_data(data_id, item)
    if not result:
        raise HTTPException(status_code=404, detail="Data not found")
    return result

@router.delete(
    "/{data_id}",
    response_model=ProcessedAgentDataInDB,
    summary="Delete processed agent data by ID",
    description="Deletes a processed agent data entry by its ID."
)
def delete_data(data_id: int):
    result = crud.delete_data(data_id)
    if not result:
        raise HTTPException(status_code=404, detail="Data not found")
    return result
