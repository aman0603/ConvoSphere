from db.database import get_mongo_client
from api.schemas import Session
from typing import AsyncGenerator
import motor.motor_asyncio

async def get_sessions_collection() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorCollection, None]:
    async for db in get_mongo_client():
        yield db.get_collection("sessions")

