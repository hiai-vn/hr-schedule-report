"""
Node to group messages by week and output CSV for each week.

Input: telegram_messages_csv from FetchTelegramMessagesNode
Output: List of weekly CSV strings for LLM classification
"""
from pocketflow import Node
import csv
from io import StringIO
from datetime import datetime, timedelta


class GroupMessagesByWeekNode(Node):
    """Node to group messages by week.

    Input: CSV string with columns: message_id, name, date, message
    Output: List of dicts with week_range and csv_string for each week
    """

    def prep(self, shared):
        """Get CSV string from shared store."""
        return shared.get("telegram_messages_csv", "")

    def exec(self, csv_string):
        """Group messages by week and return list of weekly CSVs."""
        if not csv_string:
            return []

        # Parse CSV
        messages = self._parse_csv(csv_string)

        if not messages:
            return []

        # Group by week
        weeks = {}
        for msg in messages:
            week_key, week_range = self._get_week_info(msg['date'])

            if week_key not in weeks:
                weeks[week_key] = {
                    'week_range': week_range,
                    'messages': []
                }

            weeks[week_key]['messages'].append(msg)

        # Convert each week to CSV string
        weekly_data = []
        for week_key in sorted(weeks.keys()):
            week = weeks[week_key]
            # Sort messages by date
            week['messages'].sort(key=lambda x: x['date'])

            csv_str = self._messages_to_csv(week['messages'])
            weekly_data.append({
                'week_key': week_key,
                'week_range': week['week_range'],
                'csv_string': csv_str
            })

        return weekly_data

    def _parse_csv(self, csv_string):
        """Parse CSV string to list of dicts."""
        reader = csv.DictReader(StringIO(csv_string))
        messages = []
        for row in reader:
            messages.append({
                'message_id': row['message_id'],
                'name': row['name'],
                'date': row['date'],
                'message': row['message'],
            })
        return messages

    def _get_week_info(self, date_str):
        """Get week key and range from date string.

        Args:
            date_str: Date string in format "YYYY-MM-DD HH:MM"

        Returns:
            tuple: (week_key, week_range)
                - week_key: "YYYY-MM-DD" of Monday
                - week_range: "YYYY-MM-DD -> YYYY-MM-DD" (Mon -> Sun)
        """
        # Parse date (format: "2026-01-13 23:11")
        date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')

        # Find Monday of this week
        days_since_monday = date_obj.weekday()
        week_start = date_obj - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)

        week_key = week_start.strftime('%Y-%m-%d')
        week_range = f"{week_start.strftime('%Y-%m-%d')} -> {week_end.strftime('%Y-%m-%d')}"

        return week_key, week_range

    def _messages_to_csv(self, messages):
        """Convert list of messages to CSV string."""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['message_id', 'name', 'date', 'message'])
        writer.writeheader()
        writer.writerows(messages)
        return output.getvalue()

    def post(self, shared, prep_res, exec_res):
        """Store weekly data in shared store."""
        shared["weekly_messages"] = exec_res
        return "default"