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
    #     date: "2026-01-13 09:30"
    #     message: "Dạ em xin phép làm remote hôm nay (14/1) do em bị sốt ạ"
    #   - message_id: 12346
    #     name: "Nguyễn Duy Thắng"
    #     date: "2026-01-13 08:45"
    #     message: "Dạ em xin phép thầy và anh chị cho em lên trễ tầm 10h ạ, do có việc cá nhân ạ"
    
    def prep(self, shared):
        return shared["processed_messages"]
    
    def exec(self, messages):
        # Group messages by week
        weeks = {}
        
        for msg in messages:
            date_obj = msg['datetime_obj']
            
            # Find the start of the week (Monday)
            # Example: if date_obj is Wednesday Jan 15, 2026, weekday() returns 2 (0=Mon, 1=Tue, 2=Wed)
            days_since_monday = date_obj.weekday()
            # Calculate the Monday of this week by subtracting days since Monday
            # Example: 2026-01-15 - 2 days = 2026-01-13 (Monday)
            week_start = date_obj.date() - timedelta(days=days_since_monday)
            # Calculate the Sunday of this week by adding 6 days to Monday
            # Example: 2026-01-13 + 6 days = 2026-01-19 (Sunday)
            week_end = week_start + timedelta(days=6)
            
            # Create a unique key for this week using Monday's date in YYYY-MM-DD format
            # Example: "2026-01-13"
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
        
        # Sort messages within each week by datetime before converting to YAML
        yaml_outputs = []
        for week_key in sorted(weeks.keys()):
            week_data = weeks[week_key]
            # Sort messages by datetime (earliest first)
            week_data['messages'].sort(key=lambda x: x['date'])
            yaml_str = yaml.dump(week_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
            yaml_outputs.append(yaml_str)
        
        return yaml_outputs
    
    def post(self, shared, prep_res, exec_res):
        shared["weekly_messages_yaml"] = exec_res
        return "default"