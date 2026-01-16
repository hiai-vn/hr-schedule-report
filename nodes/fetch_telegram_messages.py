"""
phân tích dữ liệu lịch làm việc từ topic "Schedule" trong các nhóm Telegram và xuất báo cáo thống kê ngày công (đi làm, nghỉ, trễ, nửa buổi, remote) ra file Excel/Google Sheet hàng tháng.
"""
from pocketflow import Node
import sys
import os
import asyncio
import json
import csv
from io import StringIO
from datetime import datetime, timezone, timedelta

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telethon import TelegramClient
from src import config


class FetchTelegramMessagesNode(Node):
    """Node to fetch messages from Telegram schedule topics for current month.

    Output CSV format:
        message_id,name,date,message
    """

    def prep(self, shared):
        # Get current month parameters
        now = datetime.now(timezone.utc)
        return {
            "year": now.year,
            "month": now.month
        }

    def exec(self, params):
        # Run the telegram fetching logic
        return asyncio.run(self._fetch_messages_async(params))

    async def _fetch_messages_async(self, params):
        """Async function to fetch messages from Telegram"""
        # Validate config
        if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
            raise ValueError("TELEGRAM_API_ID or TELEGRAM_API_HASH not set")

        # Find dialog_info.json
        dialog_info_path = os.path.join('data_raw', 'dialog_info.json')
        if not os.path.exists(dialog_info_path):
            raise FileNotFoundError(f"dialog_info.json not found at {dialog_info_path}")

        # Find schedule topics
        schedule_topics = self._find_schedule_topics(dialog_info_path)
        if not schedule_topics:
            raise ValueError("No topics named 'schedule' found in dialog_info.json")

        # Initialize Telegram client
        client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
        await client.start()

        try:
            all_messages = []
            for topic_info in schedule_topics:
                messages = await self._fetch_messages_for_topic(
                    client,
                    topic_info['group_id'],
                    topic_info['topic_id'],
                    topic_info['group_name'],
                    topic_info['topic_name']
                )
                all_messages.extend(messages)

            # Convert to CSV format
            return self._convert_to_csv(all_messages)
        finally:
            await client.disconnect()

    def _find_schedule_topics(self, dialog_info_path):
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

    async def _fetch_messages_for_topic(self, client, group_id, topic_id, group_name, topic_name):
        """Fetch messages from a specific topic with pagination and rate limiting."""
        # Get start of current month
        now = datetime.now(timezone.utc)
        start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

        all_messages = []
        offset_id = 0
        MESSAGES_PER_REQUEST = 200
        TOTAL_MESSAGES_LIMIT = 1000
        SLEEP_BETWEEN_REQUESTS = 1

        while len(all_messages) < TOTAL_MESSAGES_LIMIT:
            remaining = TOTAL_MESSAGES_LIMIT - len(all_messages)
            limit = min(MESSAGES_PER_REQUEST, remaining)

            messages_batch = []
            async for message in client.iter_messages(
                group_id,
                reply_to=topic_id,
                limit=limit,
                offset_id=offset_id
            ):
                # Stop if message is older than start of month
                if message.date and message.date < start_of_month:
                    break

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
                    'message_id': message.id,
                    'name': sender_name or f"User {sender_id}",
                    'date': message.date.strftime('%Y-%m-%d %H:%M') if message.date else '',
                    'message': message.text.strip() if message.text else ''
                }
                messages_batch.append(msg_data)
                offset_id = message.id

            if not messages_batch:
                break

            all_messages.extend(messages_batch)

            # Sleep between requests to avoid rate limiting
            if len(all_messages) < TOTAL_MESSAGES_LIMIT and messages_batch:
                await asyncio.sleep(SLEEP_BETWEEN_REQUESTS)

        return all_messages

    def _convert_to_csv(self, messages):
        """Convert messages list to CSV string format.

        Output columns: message_id, name, date, message
        """
        # Sort messages by date
        messages.sort(key=lambda x: x['date'])

        # Filter out empty messages
        messages = [m for m in messages if m['message']]

        # Write to CSV string
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['message_id', 'name', 'date', 'message'])
        writer.writeheader()
        writer.writerows(messages)

        return output.getvalue()

    def post(self, shared, prep_res, exec_res):
        shared["telegram_messages_csv"] = exec_res
        return "default"