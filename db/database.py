import os
from dotenv import load_dotenv
from pymongo import MongoClient
import redis
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "convosphere")

async def get_mongo_client():
    client = AsyncIOMotorClient(MONGO_URI)
    try:
        yield client[MONGO_DB_NAME]
    finally:
        client.close()

# Redis Connection
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

def get_redis_client():
    client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    return client

# Example usage (for testing connection)
if __name__ == "__main__":
    print("Testing MongoDB connection...")
    try:
        # Synchronous client for testing outside FastAPI context
        sync_client = MongoClient(MONGO_URI)
        db = sync_client[MONGO_DB_NAME]
        
        # The ismaster command is cheap and does not require auth.
        db.command('ismaster') 
        print(f"MongoDB connected successfully to DB: {MONGO_DB_NAME}")
        sync_client.close()
    except Exception as e:
        print(f"MongoDB connection error: {e}")

    print("\nTesting Redis connection...")
    try:
        r_client = get_redis_client()
        r_client.ping()
        print("Redis connected successfully.")
    except Exception as e:
        print(f"Redis connection error: {e}")
