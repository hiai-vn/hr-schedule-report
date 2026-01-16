from pocketflow import Node
import sys
import os
import asyncio
import json
import csv
import yaml
from datetime import datetime, timezone, timedelta

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from telethon import TelegramClient
from src import config

# below are example 



class FetchTelegramMessagesNode(Node):
    """Node to fetch messages from Telegram schedule topics for current month"""
    
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
            
            return all_messages
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
                offset_id = message.id

            if not messages_batch:
                break

            all_messages.extend(messages_batch)

            # Sleep between requests to avoid rate limiting
            if len(all_messages) < TOTAL_MESSAGES_LIMIT and messages_batch:
                await asyncio.sleep(SLEEP_BETWEEN_REQUESTS)

        return all_messages
    
    def post(self, shared, prep_res, exec_res):
        shared["telegram_messages"] = exec_res
        return "default"


class ProcessTelegramMessagesNode(Node):
    """Node to process telegram messages into the required format"""
    
    def prep(self, shared):
        return shared["telegram_messages"]
    
    def exec(self, messages):
        # Parse dates and convert to required format
        processed_messages = []
        
        for msg in messages:
            if msg['date'] and msg['text'].strip():  # Only include messages with date and text
                # Parse the date
                date_obj = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))
                
                processed_msg = {
                    'name': msg['sender_name'] or f"User {msg['sender_id']}",
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'message': msg['text'].strip(),
                    'datetime_obj': date_obj  # Keep for sorting/grouping
                }
                processed_messages.append(processed_msg)
        
        # Sort by date
        processed_messages.sort(key=lambda x: x['datetime_obj'])
        
        return processed_messages
    
    def post(self, shared, prep_res, exec_res):
        shared["processed_messages"] = exec_res
        return "default"


class GroupMessagesByWeekNode(Node):
    """Node to group messages by week in YAML format"""
# Output format:
# week_range: "2026-01-12 → 2026-01-18"
# messages:
#   - name: "Thu Nguyen"
#     date: "2026-01-13"
#     message: "Dạ em xin phép làm remote hôm nay (14/1) do em bị sốt ạ"
#   - name: "Nguyễn Duy Thắng"
#     date: "2026-01-13"
#     message: "Dạ em xin phép thầy và anh chị cho em lên trễ tầm 10h ạ, do có việc cá nhân ạ"
    def prep(self, shared):
        return shared["processed_messages"]
    
    def exec(self, messages):
        # Group messages by week
        weeks = {}
        
        for msg in messages:
            date_obj = msg['datetime_obj']
            
            # Find the start of the week (Monday)
            days_since_monday = date_obj.weekday()
            week_start = date_obj.date() - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in weeks:
                weeks[week_key] = {
                    'week_range': f"{week_start.strftime('%Y-%m-%d')} → {week_end.strftime('%Y-%m-%d')}",
                    'messages': []
                }
            
            # Add message without datetime_obj
            clean_msg = {
                'name': msg['name'],
                'date': msg['date'],
                'message': msg['message']
            }
            weeks[week_key]['messages'].append(clean_msg)
        
        # Convert to YAML format for each week
        yaml_outputs = []
        for week_key in sorted(weeks.keys()):
            week_data = weeks[week_key]
            yaml_str = yaml.dump(week_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
            yaml_outputs.append(yaml_str)
        
        return yaml_outputs
    
    def post(self, shared, prep_res, exec_res):
        shared["weekly_messages_yaml"] = exec_res
        return "default"

