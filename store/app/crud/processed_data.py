from sqlalchemy.sql import select
from app.models.database import SessionLocal
from app.models.db_models import processed_agent_data
from app.models.schemas import ProcessedAgentData

def create_data(item: ProcessedAgentData):
    db = SessionLocal()
    try:
        new_row = {
            "road_state": item.road_state,
            "user_id": item.agent_data.user_id,
            "x": item.agent_data.accelerometer.x,
            "y": item.agent_data.accelerometer.y,
            "z": item.agent_data.accelerometer.z,
            "latitude": item.agent_data.gps.latitude,
            "longitude": item.agent_data.gps.longitude,
            "timestamp": item.agent_data.timestamp,
        }
        result = db.execute(processed_agent_data.insert().values(**new_row))
        db.commit()
        new_row["id"] = result.inserted_primary_key[0]
        return new_row
    finally:
        db.close()

def get_data_by_id(data_id: int):
    db = SessionLocal()
    try:
        query = select(processed_agent_data).where(processed_agent_data.c.id == data_id)
        result = db.execute(query).mappings().fetchone()
        return result
    finally:
        db.close()


def list_data():
    db = SessionLocal()
    try:
        results = db.execute(select(processed_agent_data)).mappings().all()
        return results
    finally:
        db.close()


def update_data(data_id: int, item: ProcessedAgentData):
    db = SessionLocal()
    try:
        update_stmt = (
            processed_agent_data.update()
            .where(processed_agent_data.c.id == data_id)
            .values(
                road_state=item.road_state,
                user_id=item.agent_data.user_id,
                x=item.agent_data.accelerometer.x,
                y=item.agent_data.accelerometer.y,
                z=item.agent_data.accelerometer.z,
                latitude=item.agent_data.gps.latitude,
                longitude=item.agent_data.gps.longitude,
                timestamp=item.agent_data.timestamp,
            )
            .returning(processed_agent_data)
        )
        result = db.execute(update_stmt).mappings().fetchone()
        db.commit()
        return result
    finally:
        db.close()


def delete_data(data_id: int):
    db = SessionLocal()
    try:
        delete_stmt = (
            processed_agent_data.delete()
            .where(processed_agent_data.c.id == data_id)
            .returning(processed_agent_data)
        )
        result = db.execute(delete_stmt).mappings().fetchone()
        db.commit()
        return result
    finally:
        db.close()

