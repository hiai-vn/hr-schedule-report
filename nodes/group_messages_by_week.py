from pocketflow import Node
import yaml
from datetime import timedelta


class GroupMessagesByWeekNode(Node):
    """Node to group messages by week in YAML format"""
    # Output format:
    # week_range: "2026-01-12 → 2026-01-18"
    # messages:
    #   - message_id: 12345
    #     name: "Thu Nguyen"
    #     date: "2026-01-13"
    #     message: "Dạ em xin phép làm remote hôm nay (14/1) do em bị sốt ạ"
    #   - message_id: 12346
    #     name: "Nguyễn Duy Thắng"
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
                'message_id': msg['message_id'],
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