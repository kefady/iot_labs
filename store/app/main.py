from fastapi import FastAPI, WebSocket
from app.routers import processed_data
from app.services.websocket_manager import websocket_endpoint
from app.models.database import metadata, engine

app = FastAPI(
    title="Road Vision Store API",
)

# Create tables if not exists
metadata.create_all(bind=engine)

# Include API routes
app.include_router(processed_data.router, prefix="/processed_agent_data", tags=["processed_agent_data"])

@app.websocket("/ws/{user_id}")
async def websocket(user_id: int, websocket: WebSocket):
    await websocket_endpoint(websocket, user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
