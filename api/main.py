from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="ConvoSphere API",
    description="API for the ConvoSphere OSINT-Powered Sales Intelligence System",
    version="0.1.0",
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to ConvoSphere API", "timestamp": datetime.now().isoformat()}

# Placeholder for future routes
# from api.routes import sessions
# app.include_router(sessions.router)
