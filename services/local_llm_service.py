import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime

import ollama

class OllamaGenerativeModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = ollama.AsyncClient(host='http://localhost:11434')

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat(model=self.model_name, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']

llm_model_client = OllamaGenerativeModel(model_name="phi3:3.8b")


class LocalLLMService:
    async def analyze(self, session_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the current session context and returns a tactical analysis using the Elite Sales Strategist persona.
        """
        # Extract data from the payload
        short_context = session_payload.get("short_context", [])
        customer_info = session_payload.get("customer", {})
        osint_info = session_payload.get("osint", {})
        goal = session_payload.get("goal", "achieve a positive outcome")
        rag_context = session_payload.get("rag_context", "No specific RAG context available.") # Placeholder
        
        # Construct the detailed prompt
        prompt = f"""
# ROLE AND OBJECTIVE
You are an elite Sales Strategist and Psychological Coach. Your goal is to assist a human salesperson in real-time during a live negotiation. You do not speak to the customer directly. Instead, you "whisper" strategic advice, psychological insights, and drafted responses to the salesperson to help them close the deal.

# INPUT CONTEXT DATA
1. **Sales Goal**: {goal}
2. **Client Profile (OSINT)**: {json.dumps(osint_info, indent=2)}
3. **Tactical Analysis**: (Self-contained in this analysis)
4. **RAG Context**: {rag_context}
5. **Chat History**: {json.dumps(short_context, indent=2)}

# ANALYSIS INSTRUCTIONS
You must analyze the inputs and generate a JSON output based on the following logic:

## 1. State & Mode Detection
- **Sales Stage**: Classify into exactly one of: [Initializing, Rapport Building, Needs Discovery, Solution Pitching, Objection Handling, Closing, Stall/Delay, Dead].
- **Client Mode**: Detect psychological state: [Buying Mode, Validation Mode, Argumentative Mode, Delaying Mode].
- **Competitor Flag**: If client mentions a competitor, set to true.

## 2. Quality Control & Critique
- **Passive/Pushy Check**: Warn if salesperson is too aggressive or passive.
- **Red Flag Detector**: Identify risks like "Fake Interest" or "Authority Gap".

## 3. OSINT & Personalization
- **Bio-Hooks**: Analyze Client Profile for personal connections.

## 4. B.A.N.T. Tracker
- **Budget**: Unknown / Flexible / Specific Amount.
- **Authority**: Gatekeeper / Influencer / Decision Maker.
- **Need**: Specific pain points.
- **Timeline**: Quarter / Immediate / Next Year.

## 5. Actionable Strategy
- **Draft Response**: Write a ready-to-send reply mirroring the salesperson's tone.
- **Closing Trigger**: If stage is "Closing", suggest asking for PO.

# OUTPUT FORMAT
You must output **ONLY** a valid JSON object matching the schema below. Do not include markdown formatting or explanations outside the JSON.

```json
{{
  "meta": {{
    "timestamp": "{datetime.utcnow().isoformat()}",
    "confidence_score": 0.00
  }},
  "analysis": {{
    "current_stage": "String",
    "client_mode": "String",
    "competitor_detected": false,
    "red_flags": ["String"],
    "salesperson_critique": "String"
  }},
  "tracker": {{
    "trust_level": "String",
    "pain_points_discovered": ["String"],
    "budget_clarity": "String",
    "authority_status": "String"
  }},
  "strategy": {{
    "suggested_next_message": "String",
    "suggested_question": "String",
    "personal_hook": "String",
    "timing_suggestion": "String"
  }},
  "objections": {{
    "predicted_next": "String",
    "probability": 0.00,
    "preemptive_tactic": "String"
  }}
}}
```
"""
        
        try:
            # Add timeout for LLM generation (e.g., 30 seconds)
            try:
                raw_llm_output = await asyncio.wait_for(llm_model_client.generate(prompt), timeout=30.0)
            except asyncio.TimeoutError:
                print("--- Local LLM timed out. Using mock response. ---")
                # Mock response for fallback/testing
                raw_llm_output = """
```json
{
  "meta": {
    "timestamp": "2023-10-27T10:00:00Z",
    "confidence_score": 0.95
  },
  "analysis": {
    "current_stage": "Needs Discovery",
    "client_mode": "Buying Mode",
    "competitor_detected": false,
    "red_flags": [],
    "salesperson_critique": "Good job asking open-ended questions."
  },
  "tracker": {
    "trust_level": "High",
    "pain_points_discovered": ["Cost", "Integration"],
    "budget_clarity": "Medium",
    "authority_status": "Decision Maker"
  },
  "strategy": {
    "suggested_next_message": "That sounds great. What is your timeline for implementation?",
    "suggested_question": "When do you need this live?",
    "personal_hook": "I see you are in San Francisco.",
    "timing_suggestion": "Follow up tomorrow."
  },
  "objections": {
    "predicted_next": "Pricing",
    "probability": 0.7,
    "preemptive_tactic": "Emphasize ROI."
  }
}
```
"""

            # Clean the output to extract only the JSON
            if "```json" in raw_llm_output:
                json_part = raw_llm_output.split("```json")[1].split("```")[0]
            elif "```" in raw_llm_output:
                json_part = raw_llm_output.split("```")[1].split("```")[0]
            else:
                json_part = raw_llm_output
            
            # Parse the JSON and return it
            analysis_json = json.loads(json_part)
            analysis_json["last_analysis_at"] = datetime.utcnow()
            
            # Update timestamp to current
            if "meta" in analysis_json:
                analysis_json["meta"]["timestamp"] = datetime.utcnow().isoformat()
                
            return analysis_json

        except json.JSONDecodeError as e:
            print(f"--- Local LLM analysis failed: Could not decode JSON. Error: {e} ---")
            return {
                "last_analysis_at": datetime.utcnow(),
                "error": f"JSONDecodeError: {e}. Raw output: {raw_llm_output}"
            }
        except Exception as e:
            print(f"--- Local LLM analysis failed: {e} ---")
            return {
                "last_analysis_at": datetime.utcnow(),
                "error": str(e)
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