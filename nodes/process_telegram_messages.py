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
                # Parse the date
                date_obj = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))
                
                processed_msg = {
                    'message_id': msg['message_id'],
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