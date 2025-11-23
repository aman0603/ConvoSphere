import os
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class TelegramRouter:
    """
    Handles sending outbound messages via Telegram.
    Webhook receiver logic will be handled as a separate FastAPI endpoint.
    """
    def __init__(self):
        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")
        self.client = None
        self.session_file = str(Path(__file__).parent.parent / 'tg_user_session')

        if not self.api_id or not self.api_hash:
            print("WARNING: TELEGRAM_API_ID or TELEGRAM_API_HASH not set. Telegram functionality will be mocked.")
            self.mock_mode = True
        else:
            self.api_id = int(self.api_id)
            self.mock_mode = False

    async def connect(self):
        if self.mock_mode:
            return
        if self.client is None:
            self.client = TelegramClient(self.session_file, self.api_id, self.api_hash)
        
        if not self.client.is_connected():
            await self.client.connect()
            if not await self.client.is_user_authorized():
                print("Telegram client not authorized. Manual authentication might be needed.")
                print("Please run `python telegram_talker.py` once to authenticate if needed.")

    async def send_message(self, phone_number: str, message_text: str):
        if self.mock_mode:
            print(f"[MOCK TELEGRAM] Sending message to {phone_number}: {message_text}")
            return {"status": "mock_sent", "phone": phone_number, "message": message_text}
        
        if not self.client or not self.client.is_connected():
            # This should not happen if the startup event is working correctly
            await self.connect()

        try:
            # Resolve the contact by phone number
            entity = await self.client.get_entity(phone_number)
            if not entity:
                return {"status": "error", "detail": f"Could not resolve Telegram entity for {phone_number}"}

            sent_message = await self.client.send_message(entity, message_text)
            return {"status": "sent", "message_id": sent_message.id, "phone": phone_number}
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return {"status": "error", "detail": str(e)}

    async def disconnect(self):
        if not self.mock_mode and self.client.is_connected():
            await self.client.disconnect()

# Example usage
async def main():
    router = TelegramRouter()
    await router.connect()
    
    # Replace with a real phone number you want to send a message to
    target_phone = os.getenv("TELEGRAM_TEST_PHONE", "+1234567890") 
    test_message = "Hello from ConvoSphere Telegram Router!"

    result = await router.send_message(target_phone, test_message)
    print(f"Telegram send result: {result}")

    await router.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
