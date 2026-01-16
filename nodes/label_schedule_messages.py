"""
Node to label schedule messages using LLM (Gemini) into categories:
- nghi: xin nghỉ cả ngày hoặc nhiều ngày
- tre: xin lên trễ
- nua_buoi: xin nghỉ nửa buổi (sáng / chiều)
- remote: xin làm remote / làm online

Uses AsyncParallelBatchNode to process multiple weeks in parallel.
Input: List of weekly CSV data from GroupMessagesByWeekNode
Output: Merged labeled messages from all weeks
"""
from pocketflow import AsyncParallelBatchNode
import yaml
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.call_llm import call_llm_async


class LabelScheduleMessagesNode(AsyncParallelBatchNode):
    """Node to classify schedule messages using Gemini LLM in parallel.

    Input: List of weekly data dicts with csv_string for each week
    Output: Merged labeled messages with categories: nghi, tre, nua_buoi, remote

    Uses AsyncParallelBatchNode to call LLM for each week in parallel.
    """

    SYSTEM_PROMPT = """Bạn là một trợ lý phân loại tin nhắn xin phép lịch làm việc.

Phân loại các tin nhắn vào các nhãn sau:
- nghi: xin nghỉ cả ngày hoặc nhiều ngày (nghỉ phép, nghỉ làm, off)
- tre: xin lên trễ, đi trễ, vào muộn
- nua_buoi: xin nghỉ nửa buổi (nghỉ sáng, nghỉ chiều)
- remote: xin làm remote, làm online, work from home

Bỏ qua các tin nhắn không thuộc loại nào trên.

Ví dụ:
Input (CSV):
message_id,name,date,message
1047,Tín Lữ,2026-01-13 23:11,Em xin phép làm remote hôm nay (14/1) do em bị sốt ạ
1042,Nguyễn Duy Thắng,2026-01-13 00:41,Dạ em xin phép thầy và anh chị cho em lên trễ tầm 10h ạ

Output (YAML):
nghi: []
tre:
  - message_id: 1042
    name: Nguyễn Duy Thắng
    dates:
      - "2026-01-13"
    info: "Lên trễ đến 10h"
nua_buoi: []
remote:
  - message_id: 1047
    name: Tín Lữ
    dates:
      - "2026-01-14"
    info: "Làm remote do bị sốt"

Lưu ý:
- Chỉ trả về YAML, không có text khác
- dates phải là danh sách các ngày theo format YYYY-MM-DD
- Nếu tin nhắn đề cập ngày theo format d/m (ví dụ: 14/1), convert sang YYYY-MM-DD dựa vào năm của ngày gửi tin nhắn
- Nếu không đề cập ngày cụ thể, dùng ngày gửi tin nhắn
- info nên ngắn gọn, tối đa 50 ký tự
- Nếu không có tin nhắn nào thuộc một category thì để mảng rỗng []"""

    async def prep_async(self, shared):
        """Get list of weekly data from shared store."""
        return shared.get("weekly_messages", [])

    async def exec_async(self, week_data):
        """Classify messages for a single week using LLM.

        Args:
            week_data: Dict with keys: week_key, week_range, csv_string

        Returns:
            Dict with week info and labeled results
        """
        csv_string = week_data.get('csv_string', '')
        if not csv_string:
            return {
                'week_key': week_data.get('week_key'),
                'week_range': week_data.get('week_range'),
                'labels': self._empty_result()
            }

        prompt = f"""{self.SYSTEM_PROMPT}

Input (CSV):
{csv_string}

Output (YAML):"""

        response_text = await call_llm_async(prompt)
        response_text = response_text.strip()

        # Clean up response - remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()

        result = yaml.safe_load(response_text)

        return {
            'week_key': week_data.get('week_key'),
            'week_range': week_data.get('week_range'),
            'labels': self._normalize_result(result)
        }

    def _normalize_result(self, result):
        """Ensure result has all required categories."""
        normalized = self._empty_result()

        if not isinstance(result, dict):
            return normalized

        for category in ['nghi', 'tre', 'nua_buoi', 'remote']:
            if category in result and isinstance(result[category], list):
                normalized[category] = result[category]

        return normalized

    def _empty_result(self):
        """Return empty result structure."""
        return {
            'nghi': [],
            'tre': [],
            'nua_buoi': [],
            'remote': [],
        }

    async def post_async(self, shared, prep_res, exec_res):
        """Merge results from all weeks and store in shared store."""
        # Merge all weekly results
        merged = self._empty_result()

        weekly_results = []
        for week_result in (exec_res or []):
            if not week_result:
                continue

            # Store per-week result
            weekly_results.append({
                'week_key': week_result.get('week_key'),
                'week_range': week_result.get('week_range'),
                'labels': week_result.get('labels', self._empty_result())
            })

            # Merge into total
            labels = week_result.get('labels', {})
            for category in ['nghi', 'tre', 'nua_buoi', 'remote']:
                if category in labels:
                    merged[category].extend(labels[category])

        # Sort weekly results by week_key
        weekly_results.sort(key=lambda x: x.get('week_key', ''))

        # Store results
        shared["labeled_messages"] = merged
        shared["weekly_labeled_messages"] = weekly_results
        shared["labeled_messages_yaml"] = yaml.dump(
            merged,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )

        return "default"