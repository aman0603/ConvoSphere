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
        Analyzes the current session context and returns a tactical analysis.
        """
        # Extract data from the payload
        short_context = session_payload.get("short_context", [])
        customer_name = session_payload.get("customer", {}).get("name", "there")
        goal = session_payload.get("goal", "achieve a positive outcome")
        
        # Construct a detailed prompt for the tactical analysis
        prompt = f"""
You are a Tactical Analyst for a sales conversation. Your task is to analyze the provided conversation context and output a structured JSON object.

**Conversation Details:**
- Customer Name: {customer_name}
- Sales Goal: {goal}
- Recent Conversation History (short_context):
{json.dumps(short_context, indent=2)}

**Your Task:**
Based on the conversation history, provide the following analysis in a single JSON object. Do not include any text or formatting outside of the JSON object.

1.  **global_summary**: A concise, one-sentence summary of the entire conversation so far.
2.  **latest_interaction_summary**: A summary of the very last message or exchange.
3.  **current_sentiment**: Classify the customer's current sentiment. Choose one from: "Positive", "Neutral", "Skeptical", "Negative", "Curious".
4.  **conversation_state_tag**: Categorize the current state of the conversation. Choose one from: "Rapport_Building", "Needs_Discovery", "Solution_Pitching", "Price_Negotiation", "Objection_Handling", "Closing", "Stalled".

**Output Format (JSON only):**
{{
  "global_summary": "<Your one-sentence summary>",
  "latest_interaction_summary": "<Your summary of the last interaction>",
  "current_sentiment": "<Your sentiment analysis>",
  "conversation_state_tag": "<Your conversation state tag>"
}}
"""
        
        try:
            raw_llm_output = await llm_model_client.generate(prompt)
            
            # Clean the output to extract only the JSON
            # LLMs sometimes add markdown formatting (```json ... ```) or other text
            if "```json" in raw_llm_output:
                json_part = raw_llm_output.split("```json")[1].split("```")[0]
            else:
                json_part = raw_llm_output
            
            # Parse the JSON and return it
            analysis_json = json.loads(json_part)

            # Safeguard: Ensure latest_interaction_summary is a string
            if isinstance(analysis_json.get("latest_interaction_summary"), dict):
                analysis_json["latest_interaction_summary"] = json.dumps(analysis_json["latest_interaction_summary"])

            analysis_json["last_analysis_at"] = datetime.utcnow()
            return analysis_json

        except json.JSONDecodeError as e:
            print(f"--- Local LLM analysis failed: Could not decode JSON from LLM response. Error: {e} ---")
            return {
                "last_analysis_at": datetime.utcnow(),
                "error": f"JSONDecodeError: {e}. Raw output: {raw_llm_output}"
            }
        except Exception as e:
            print(f"--- Local LLM analysis failed with an unexpected error: {e} ---")
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