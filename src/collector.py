import json
import os
from datetime import datetime, timezone
from telethon import TelegramClient
from src import config

def get_start_of_month():
    """Returns the timezone-aware datetime for the start of the current month (UTC)."""
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

async def fetch_messages(client):
    """
    Fetches messages from the configured group/topic since the start of the month.
    Filters:
    - Not empty
    - At least 4 words
    """
    start_date = get_start_of_month()
    print(f"Fetching messages since: {start_date}")

    entity = config.TARGET_GROUP_ID
    topic_id = config.TARGET_TOPIC_ID

    if not entity:
        print("Error: TARGET_GROUP_ID is not set.")
        return []

    messages = []

    # Iterate over messages
    # Note: Telethon iter_messages goes from newest to oldest by default.
    # We stop when we reach a message older than start_date.

    # Handle Topic ID if present
    kwargs = {}
    if topic_id:
        kwargs['reply_to'] = topic_id

    try:
        async for message in client.iter_messages(entity, **kwargs):
            # Check date
            if message.date < start_date:
                break

            # Filter logic
            text = message.text
            if not text:
                continue

            # Remove extra whitespace for word counting
            words = text.strip().split()
            if len(words) < 4:
                continue

            # Collect data
            msg_data = {
                "id": message.id,
                "date": message.date.isoformat(),
                "sender_id": message.sender_id,
                "text": text
            }
            messages.append(msg_data)
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

    print(f"Collected {len(messages)} messages.")
    return messages

def save_to_json(data, filepath):
    """Saves the list of dictionaries to a JSON file."""
    # Ensure directory exists
    dir_path = os.path.dirname(filepath)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Saved data to {filepath}")
