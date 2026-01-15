import sys
import os
import asyncio
import json

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telethon import TelegramClient
from src import config

# HiAI group with Schedule topic
GROUP_ID = -1002804503194
TOPIC_ID = 5

async def fetch_sample_messages(client, limit=200):
    """Fetch first N messages from the Schedule topic."""
    print(f"Fetching {limit} messages from Schedule topic...")

    messages = []

    async for message in client.iter_messages(GROUP_ID, reply_to=TOPIC_ID, limit=limit):
        # Get sender info
        sender = await message.get_sender()
        sender_name = None
        if sender:
            if hasattr(sender, 'first_name'):
                sender_name = sender.first_name
                if sender.last_name:
                    sender_name += f" {sender.last_name}"
            elif hasattr(sender, 'title'):
                sender_name = sender.title

        msg_data = {
            "id": message.id,
            "date": message.date.isoformat() if message.date else None,
            "sender_id": message.sender_id,
            "sender_name": sender_name,
            "text": message.text if message.text else "[No text - possibly media]"
        }
        messages.append(msg_data)

    return messages

def main():
    if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
        print("Error: TELEGRAM_API_ID or TELEGRAM_API_HASH not set.")
        return

    print("Initializing Telegram Client...")
    client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)

    async def run():
        messages = await fetch_sample_messages(client, limit=200)

        # Create data structure with metadata
        data = {
            "group_id": GROUP_ID,
            "topic_id": TOPIC_ID,
            "fetched_at": asyncio.get_event_loop().time(),
            "total_messages": len(messages),
            "messages": messages
        }

        # Save to file first
        output_path = os.path.join(os.path.dirname(__file__), '..', 'data_raw', 'schedule_sample.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(messages)} messages to {output_path}")
        print(f"Group ID: {GROUP_ID}, Topic ID: {TOPIC_ID}")

    client.start()
    client.loop.run_until_complete(run())

if __name__ == "__main__":
    main()
