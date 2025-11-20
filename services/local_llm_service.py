import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Placeholder for a proper generative model client (e.g., Ollama)
# For now, we'll use a mock client.
class MockGenerativeModel:
    async def generate(self, prompt: str) -> str:
        # Simulate an async call
        await asyncio.sleep(0.1) 
        if "analyze" in prompt:
            return "This is a mock analysis of the conversation, noting a potential intent shift."
        elif "suggest" in prompt:
            return "This is a mock first message suggestion: 'Hi {name}, I noticed you're interested in {context}.'"
        return "Mock response."

# In a real implementation, you would use something like:
# from ollama import Client
# ollama_client = Client(host='http://localhost:11434')

# For now, we use the mock
llm_model_client = MockGenerativeModel()


class LocalLLMService:
    async def analyze(self, session_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the current session context and returns insights.
        This is a placeholder implementation.
        """
        short_context = session_payload.get("short_context", [])
        customer_name = session_payload.get("customer", {}).get("name", "there")
        prompt = f"Analyze the following conversation for {customer_name} and provide a summary, sentiment, and buying intent score.\n\nConversation:\n{json.dumps(short_context, indent=2)}\n\nTask: analyze_and_summarize"
        
        analysis_text = await llm_model_client.generate(prompt)

        # Simulate some dynamic values for alerts
        buying_intent_score = 60 + len(short_context) * 2 # Score increases with messages
        intent_shift = (buying_intent_score > 70) # Simulate a shift
        
        return {
            "last_analysis_at": datetime.utcnow().isoformat(),
            "short_context": json.dumps(short_context), # Store as string for simplicity
            "long_summary": analysis_text,
            "sentiment": "neutral-positive",
            "emotion": "curious",
            "buying_intent_score": min(95, buying_intent_score), # Cap score
            "intent_shift": intent_shift,
            "intent_shift_at": datetime.utcnow().isoformat() if intent_shift else None,
            "risks": ["price concern"] if buying_intent_score > 80 else [],
            "opportunities": ["trial module"]
        }

    async def suggest_first_message(self, session_payload: Dict[str, Any]) -> str:
        """
        Suggests an initial outbound message based on the person's info.
        This is a placeholder implementation.
        """
        customer_info = session_payload.get("customer", {})
        osint_info = session_payload.get("osint", {})
        goal = session_payload.get("goal", "")
        customer_name = customer_info.get("name", "there")
        customer_context = customer_info.get("context", "")

        prompt = f"Suggest a compelling first message for {customer_name}, with the goal of '{goal}', given their context: '{customer_context}'.\n\nPerson Info:\n{json.dumps(customer_info, indent=2)}\n\nOSINT Insights:\n{json.dumps(osint_info, indent=2)}\n\nTask: suggest_first_message"

        suggestion_text = await llm_model_client.generate(prompt)
        
        return suggestion_text.replace("{name}", customer_name).replace("{context}", customer_context) # Simple templating

def get_llm_service() -> LocalLLMService:
    return LocalLLMService()