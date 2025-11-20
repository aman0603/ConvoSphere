from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
from datetime import datetime
from api.schemas import CreateSessionRequest, Session, Message, OSINT, LocalLLMAnalysis, GeminiAnalysis, Alert, NewMessageRequest
from db.database import get_mongo_client
from db.models import get_sessions_collection
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from typing import Optional, Dict, Any
import asyncio
import json # For json.dumps

# Import services
from services.telegram_router import TelegramRouter
from gemini_client import GeminiClient # Still using the old gemini_client.py
from services.local_llm_service import get_llm_service, LocalLLMService

app = FastAPI(
    title="ConvoSphere API",
    description="API for the ConvoSphere OSINT-Powered Sales Intelligence System",
    version="0.1.0",
)

# Initialize services globally
telegram_router = TelegramRouter()
gemini_client_instance = GeminiClient() # Rename to avoid conflict if gemini_client.py becomes a service
local_llm_service = get_llm_service() # Get instance of LocalLLMService


# --- Background Tasks / Workers ---

# Placeholder for Alert Dispatcher
async def run_alert_dispatcher(session_id: str, alert_data: Dict[str, Any], db_client: AsyncIOMotorClient):
    sessions_collection = db_client.get_collection("sessions")
    print(f"--- Dispatching alert for session {session_id}: {alert_data.get('message')} ---")
    
    new_alert = Alert(**alert_data)
    
    await sessions_collection.update_one(
        {"_id": session_id},
        {
            "$push": {"alerts": new_alert.dict(exclude_none=True)},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    print(f"--- Alert saved for session {session_id} ---")


# Placeholder for OSINT enrichment function
async def run_osint_enrichment(session_id: str, db_client: AsyncIOMotorClient):
    sessions_collection = db_client.get_collection("sessions")
    print(f"--- Starting OSINT enrichment for session: {session_id} ---")
    
    # Simulate work
    await asyncio.sleep(5) 
    
    # Update session status (example)
    await sessions_collection.update_one(
        {"_id": session_id},
        {"$set": {"osint.status": "completed", "updated_at": datetime.utcnow()}}
    )
    print(f"--- OSINT enrichment completed for session: {session_id} ---")


# Local LLM Analyze Worker
async def run_local_llm_analyze(session_id: str, db_client: AsyncIOMotorClient, background_tasks: BackgroundTasks):
    sessions_collection = db_client.get_collection("sessions")
    print(f"--- Starting Local LLM analysis for session: {session_id} ---")

    session_doc = await sessions_collection.find_one({"_id": session_id})
    if not session_doc:
        print(f"Local LLM analysis failed: Session {session_id} not found.")
        return

    session = Session(**session_doc)
    
    # Prepare payload for Local LLM Service
    llm_payload = {
        "session_id": session.session_id,
        "customer": session.customer.dict() if session.customer else {},
        "osint": session.osint.dict() if session.osint else {},
        "short_context": [msg.dict() for msg in session.messages], # Use all messages for short_context for now
        "long_context_summary": session.local_llm.long_summary if session.local_llm else None,
        "goal": session.customer.goal if session.customer else None,
        "task": "analyze_and_summarize"
    }

    try:
        analysis_result = await local_llm_service.analyze(llm_payload)
        
        # Convert datetime objects to ISO format if present in analysis_result
        if isinstance(analysis_result.get("last_analysis_at"), datetime):
            analysis_result["last_analysis_at"] = analysis_result["last_analysis_at"].isoformat()
        if isinstance(analysis_result.get("intent_shift_at"), datetime):
            analysis_result["intent_shift_at"] = analysis_result["intent_shift_at"].isoformat()

        # Update session with LLM analysis
        await sessions_collection.update_one(
            {"_id": session_id},
            {"$set": {"local_llm": analysis_result, "updated_at": datetime.utcnow()}}
        )
        print(f"--- Local LLM analysis completed and session updated for {session_id} ---")

        # Check for alerts based on analysis_result
        if analysis_result.get("intent_shift"):
            alert_message = f"Intent Shift detected for {session.customer.name} (Session: {session_id}). Buying intent score: {analysis_result.get('buying_intent_score')}"
            alert_data = {
                "type": "high_intent" if analysis_result.get('buying_intent_score', 0) > 70 else "info",
                "message": alert_message
            }
            background_tasks.add_task(run_alert_dispatcher, session_id, alert_data, db_client)
        
    except Exception as e:
        print(f"--- Local LLM analysis failed for session {session_id}: {e} ---")
        await sessions_collection.update_one(
            {"_id": session_id},
            {"$set": {"local_llm.error": str(e), "updated_at": datetime.utcnow()}}
        )


# Gemini call worker
async def run_gemini_call(session_id: str, task: str, db_client: AsyncIOMotorClient):
    sessions_collection = db_client.get_collection("sessions")
    print(f"--- Starting Gemini call for session: {session_id}, task: {task} ---")

    session_doc = await sessions_collection.find_one({"_id": session_id})
    if not session_doc:
        print(f"Gemini call failed: Session {session_id} not found.")
        return

    session = Session(**session_doc)

    # Construct Gemini payload (as per AGENT_ARCHITECTURE.md, section 8)
    gemini_payload = {
        "session_id": session.session_id,
        "customer": session.customer.dict(),
        "osint": session.osint.dict() if session.osint else {},
        "short_context": [msg.dict() for msg in session.messages[-20:]], # Last 20 messages
        "long_context_summary": session.local_llm.long_summary if session.local_llm else None,
        "local_llm_analysis": session.local_llm.dict() if session.local_llm else {},
        "task": task
    }

    # TODO: Implement PII sanitization before sending to Gemini if policy demands (section 8)

    try:
        # For now, we'll use a mock response. In a real scenario, you'd call gemini_client methods.
        # Example: response = await gemini_client_instance.some_gemini_method(prompt, model, formatted_payload)
        # For this placeholder, we'll just log and return a mock.
        
        # This is a mock interaction, actual gemini client methods like parse_initial_info are specific
        # We need a generic method to handle different tasks for gemini_call
        # Let's assume a generic `process_task` for now.
        
        # TODO: Replace with actual GeminiClient method call based on `task`
        mock_response = {
            "summary": f"Gemini mock summary for task '{task}' and session {session_id}",
            "recommendation": "Mocked recommendation: Follow up next week.",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        gemini_result = {
            "last_call_at": datetime.utcnow(),
            "payload_sent": gemini_payload,
            "response": mock_response
        }

        await sessions_collection.update_one(
            {"_id": session_id},
            {"$set": {"gemini": gemini_result, "updated_at": datetime.utcnow()}}
        )
        print(f"--- Gemini call completed for session: {session_id} ---")
    except Exception as e:
        print(f"--- Gemini call failed for session {session_id}: {e} ---")
        await sessions_collection.update_one(
            {"_id": session_id},
            {"$set": {"gemini.error": str(e), "updated_at": datetime.utcnow()}}
        )


# --- FastAPI Event Handlers ---

@app.on_event("startup")
async def startup_event():
    await telegram_router.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await telegram_router.disconnect()


# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to ConvoSphere API", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/sessions", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    background_tasks: BackgroundTasks,
    db_client: AsyncIOMotorClient = Depends(get_mongo_client),
    sessions_collection: pymongo.collection.Collection = Depends(get_sessions_collection)
):
    session_data = {
        "customer": request.dict(), # Use request.dict() for initial customer data
        "owner": request.owner_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "osint": OSINT().dict(), # Initialize with default empty OSINT
        "local_llm": LocalLLMAnalysis().dict(), # Initialize with default empty LocalLLMAnalysis
        "gemini": GeminiAnalysis().dict(), # Initialize with default empty GeminiAnalysis
        "messages": [],
        "alerts": [],
        "status": "initialized"
    }
    
    # Create a Session object to leverage Pydantic's default_factory for session_id
    new_session_obj = Session(**session_data)
    
    # Convert to dictionary, ensuring _id is correctly set from session_id
    session_to_insert = new_session_obj.dict(by_alias=True, exclude_none=True) # exclude_none to not store None values
    session_to_insert["_id"] = new_session_obj.session_id # Ensure _id is set for MongoDB
    
    try:
        result = await sessions_collection.insert_one(session_to_insert)
        
        # Fetch the created session to ensure it matches the response model
        created_session = await sessions_collection.find_one({"_id": result.inserted_id})
        if created_session:
            # Enqueue OSINT enrichment as a background task
            background_tasks.add_task(run_osint_enrichment, new_session_obj.session_id, db_client)
            return Session(**created_session)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve created session")
            
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@app.get("/api/sessions/{session_id}", response_model=Session)
async def get_session(
    session_id: str,
    db_client: AsyncIOMotorClient = Depends(get_mongo_client),
    sessions_collection: pymongo.collection.Collection = Depends(get_sessions_collection)
):
    try:
        session = await sessions_collection.find_one({"_id": session_id})
        if session:
            return Session(**session)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session with ID {session_id} not found")
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")


@app.post("/api/sessions/{session_id}/messages", response_model=Session)
async def add_message_to_session(
    session_id: str,
    message_request: NewMessageRequest,
    background_tasks: BackgroundTasks, # Add background_tasks here
    db_client: AsyncIOMotorClient = Depends(get_mongo_client),
    sessions_collection: pymongo.collection.Collection = Depends(get_sessions_collection)
):
    try:
        # Create a Message object
        new_message = Message(
            session_id=session_id,
            sender=message_request.sender,
            text=message_request.text,
            channel=message_request.channel,
            timestamp=datetime.utcnow()
        )
        
        update_result = await sessions_collection.update_one(
            {"_id": session_id},
            {
                "$push": {"messages": new_message.dict(exclude_none=True)},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if update_result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session with ID {session_id} not found")
        
        updated_session_doc = await sessions_collection.find_one({"_id": session_id})
        if updated_session_doc:
            updated_session = Session(**updated_session_doc)
            # Enqueue Local LLM analysis as a background task
            background_tasks.add_task(run_local_llm_analyze, updated_session.session_id, db_client, background_tasks)
            return updated_session
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve updated session")
            
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

class SendMessageRequest(BaseModel):
    text: str

@app.post("/api/sessions/{session_id}/send", response_model=Session)
async def send_outbound_message(
    session_id: str,
    send_request: SendMessageRequest,
    db_client: AsyncIOMotorClient = Depends(get_mongo_client),
    sessions_collection: pymongo.collection.Collection = Depends(get_sessions_collection)
):
    try:
        session = await sessions_collection.find_one({"_id": session_id})
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session with ID {session_id} not found")
        
        customer_phone = session.get("customer", {}).get("phone")
        if not customer_phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer phone not found in session")
        
        # Use the TelegramRouter to send the message
        telegram_send_result = await telegram_router.send_message(customer_phone, send_request.text)
        
        if telegram_send_result.get("status") == "error":
            # If sending fails, we might still want to record the attempt or raise an error
            print(f"Failed to send Telegram message: {telegram_send_result.get('detail')}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send message: {telegram_send_result.get('detail')}")

        # Create a Message object as if sent by the agent
        new_message = Message(
            session_id=session_id,
            sender="agent",
            text=send_request.text,
            channel="telegram", # Sent via Telegram
            timestamp=datetime.utcnow()
        )
        
        update_result = await sessions_collection.update_one(
            {"_id": session_id},
            {
                "$push": {"messages": new_message.dict(exclude_none=True)},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if update_result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session with ID {session_id} not found")
        
        updated_session = await sessions_collection.find_one({"_id": session_id})
        if updated_session:
            return Session(**updated_session)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve updated session")
            
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks, db_client: AsyncIOMotorClient):
    """
    Placeholder for Telegram webhook receiver.
    This endpoint will receive incoming messages from Telegram.
    """
    payload = await request.json()
    print(f"--- Received Telegram Webhook ---")
    print(f"Payload: {payload}")
    print(f"---------------------------------")

    # TODO: Parse payload, extract sender, text.
    # For now, let's assume we extract a phone number and message text
    mock_sender_phone = payload.get("message", {}).get("from", {}).get("phone_number", "+1234567890") # Mock
    mock_message_text = payload.get("message", {}).get("text", "Default webhook message") # Mock
    
    # Find session by phone number (requires a lookup across customer.phone field)
    # This is a simplification; a real system would map Telegram chat_id to session
    sessions_collection = db_client.get_collection("sessions")
    session_doc = await sessions_collection.find_one({"customer.phone": mock_sender_phone})

    if session_doc:
        session_id = str(session_doc["_id"])
        # Use add_message_to_session logic
        new_message_request = NewMessageRequest(
            sender="customer",
            text=mock_message_text,
            channel="telegram"
        )
        await add_message_to_session(session_id, new_message_request, background_tasks, db_client, sessions_collection)
        print(f"--- Processed incoming Telegram message for session {session_id} ---")
    else:
        print(f"--- No session found for phone number {mock_sender_phone}. Creating a stub session. ---")
        # For now, if no session, just print. In a real scenario, you might create a new session stub.
        # This requires more advanced logic for new conversations via webhook.

    # Return 200 OK to Telegram to acknowledge receipt
    return {"status": "success", "message": "Webhook received"}