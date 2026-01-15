import sys
import os
import asyncio
import json
import csv
from datetime import datetime

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telethon import TelegramClient
from src import config

# Constants
MESSAGES_PER_REQUEST = 200
TOTAL_MESSAGES_LIMIT = 1000
SLEEP_BETWEEN_REQUESTS = 1  # seconds


def find_schedule_topics(dialog_info_path):
    """Find all groups with topics named 'schedule' (case-insensitive)."""
    with open(dialog_info_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    schedule_topics = []
    for group in data.get('groups_and_channels', []):
        for topic in group.get('topics', []):
            if topic.get('title', '').lower() == 'schedule':
                schedule_topics.append({
                    'group_id': group['id'],
                    'group_name': group['name'],
                    'topic_id': topic['id'],
                    'topic_name': topic['title']
                })

    return schedule_topics


async def fetch_messages_for_topic(client, group_id, topic_id, group_name, topic_name):
    """Fetch messages from a specific topic with pagination and rate limiting."""
    print(f"\nFetching messages from '{group_name}' -> '{topic_name}'")
    print(f"  Group ID: {group_id}, Topic ID: {topic_id}")

    all_messages = []
    offset_id = 0
    request_count = 0

    while len(all_messages) < TOTAL_MESSAGES_LIMIT:
        remaining = TOTAL_MESSAGES_LIMIT - len(all_messages)
        limit = min(MESSAGES_PER_REQUEST, remaining)

        request_count += 1
        print(f"  Request {request_count}: Fetching {limit} messages (offset_id={offset_id})...")

        messages_batch = []
        async for message in client.iter_messages(
            group_id,
            reply_to=topic_id,
            limit=limit,
            offset_id=offset_id
        ):
            # Get sender info
            sender = await message.get_sender()
            sender_name = None
            sender_id = message.sender_id

            if sender:
                if hasattr(sender, 'first_name'):
                    sender_name = sender.first_name
                    if sender.last_name:
                        sender_name += f" {sender.last_name}"
                elif hasattr(sender, 'title'):
                    sender_name = sender.title

            msg_data = {
                'group_id': group_id,
                'topic_id': topic_id,
                'group_name': group_name,
                'topic_name': topic_name,
                'message_id': message.id,
                'date': message.date.isoformat() if message.date else None,
                'sender_id': sender_id,
                'sender_name': sender_name,
                'text': message.text if message.text else ''
            }
            messages_batch.append(msg_data)
            offset_id = message.id  # Update offset for next batch

        if not messages_batch:
            print(f"  No more messages available.")
            break

        all_messages.extend(messages_batch)
        print(f"  Fetched {len(messages_batch)} messages. Total: {len(all_messages)}")

        # Sleep between requests to avoid rate limiting
        if len(all_messages) < TOTAL_MESSAGES_LIMIT and messages_batch:
            print(f"  Sleeping {SLEEP_BETWEEN_REQUESTS} second(s)...")
            await asyncio.sleep(SLEEP_BETWEEN_REQUESTS)

    return all_messages


def save_to_csv(messages, output_path):
    """Save messages to CSV file."""
    if not messages:
        print("No messages to save.")
        return

    fieldnames = ['group_id', 'topic_id', 'group_name', 'topic_name', 'message_id', 'date', 'sender_id', 'sender_name', 'text']

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(messages)

    print(f"\nSaved {len(messages)} messages to {output_path}")


def main():
    if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
        print("Error: TELEGRAM_API_ID or TELEGRAM_API_HASH not set.")
        return

    # Find dialog_info.json
    dialog_info_path = os.path.join(os.path.dirname(__file__), '..', 'data_raw', 'dialog_info.json')
    if not os.path.exists(dialog_info_path):
        print(f"Error: dialog_info.json not found at {dialog_info_path}")
        return

    # Find all schedule topics
    schedule_topics = find_schedule_topics(dialog_info_path)
    if not schedule_topics:
        print("No topics named 'schedule' found in dialog_info.json")
        return

    print(f"Found {len(schedule_topics)} topic(s) named 'schedule':")
    for topic in schedule_topics:
        print(f"  - {topic['group_name']} -> {topic['topic_name']} (Group: {topic['group_id']}, Topic: {topic['topic_id']})")

    print("\nInitializing Telegram Client...")
    client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)

    async def run():
        all_messages = []

        for topic_info in schedule_topics:
            messages = await fetch_messages_for_topic(
                client,
                topic_info['group_id'],
                topic_info['topic_id'],
                topic_info['group_name'],
                topic_info['topic_name']
            )
            all_messages.extend(messages)

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(os.path.dirname(__file__), '..', 'data_raw', f'schedule_messages_{timestamp}.csv')

        save_to_csv(all_messages, output_path)

        print(f"\n=== Summary ===")
        print(f"Total messages fetched: {len(all_messages)}")
        print(f"Output file: {output_path}")

    client.start()
    client.loop.run_until_complete(run())


if __name__ == "__main__":
    main()
