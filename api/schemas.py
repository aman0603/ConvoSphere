from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

# Helper to generate UUIDs
def generate_uuid() -> str:
    return str(uuid.uuid4())

class Customer(BaseModel):
    name: str
    phone: str
    context: str
    goal: str

class OSINT(BaseModel):
    numverify: Optional[Dict[str, Any]] = None
    linkedin: Optional[Dict[str, Any]] = None
    github: Optional[Dict[str, Any]] = None
    serp: Optional[List[Dict[str, Any]]] = None
    firecrawl: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None

class Message(BaseModel):
    message_id: str = Field(default_factory=generate_uuid)
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender: str # "agent" | "customer" | "system"
    channel: str # "telegram" | "streamlit"
    text: str

class LocalLLMAnalysis(BaseModel):
    last_analysis_at: Optional[datetime] = None
    short_context: Optional[str] = None # Or List[str] if it's a list of messages
    long_summary: Optional[str] = None
    sentiment: Optional[str] = None
    emotion: Optional[str] = None
    buying_intent_score: Optional[int] = None
    intent_shift: Optional[bool] = None
    intent_shift_at: Optional[datetime] = None
    risks: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None

class GeminiAnalysis(BaseModel):
    last_call_at: Optional[datetime] = None
    payload_sent: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None

class Alert(BaseModel):
    alert_id: str = Field(default_factory=generate_uuid)
    type: str # "high_intent" | "risk" | "info"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message: str

class Session(BaseModel):
    session_id: str = Field(default_factory=generate_uuid, alias="_id") # Use _id for MongoDB
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    owner: str # sales_agent_id
    customer: Customer
    osint: OSINT = Field(default_factory=OSINT)
    messages: List[Message] = Field(default_factory=list)
    local_llm: LocalLLMAnalysis = Field(default_factory=LocalLLMAnalysis)
    gemini: GeminiAnalysis = Field(default_factory=GeminiAnalysis)
    alerts: List[Alert] = Field(default_factory=list)
    status: str = "initialized" # "initialized" | "active" | "closed"

# Request model for creating a new session
class CreateSessionRequest(BaseModel):
    name: str
    phone: str
    context: str
    goal: str
    owner_id: str
