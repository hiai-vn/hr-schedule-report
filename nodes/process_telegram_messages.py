from pocketflow import Node
from datetime import datetime


class ProcessTelegramMessagesNode(Node):
    """Node to process telegram messages into the required format"""
    
    def prep(self, shared):
        return shared["telegram_messages"]
    
    def exec(self, messages):
        # Parse dates and convert to required format
        processed_messages = []
        
        for msg in messages:
            if msg['date'] and msg['text'].strip():  # Only include messages with date and text
                # Parse the date from ISO format string to datetime object
                # Example: "2026-01-15T14:30:25Z" -> "2026-01-15T14:30:25+00:00" -> datetime(2026, 1, 15, 14, 30, 25, tzinfo=timezone.utc)
                date_obj = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))
                
                # Create processed message data structure
                # date_obj is used for: 1) formatting display date string, 2) keeping original datetime for sorting/week grouping
                processed_msg = {
                    'message_id': msg['message_id'],
                    'name': msg['sender_name'] or f"User {msg['sender_id']}",
                    'date': date_obj.strftime('%Y-%m-%d %H:%M'),  # Format for display: "2026-01-15 14:30"
                    'message': msg['text'].strip(),
                    'datetime_obj': date_obj  # Keep original datetime object for sorting/grouping operations
                }
                processed_messages.append(processed_msg)
        
        # Sort by date
        processed_messages.sort(key=lambda x: x['datetime_obj'])
        
        return processed_messages
    
    def post(self, shared, prep_res, exec_res):
        shared["processed_messages"] = exec_res
        return "default"