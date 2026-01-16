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

    SYSTEM_PROMPT = """Bạn là một trợ lý phân loại tin nhắn xin phép lịch làm việc. Chỉ trả về YAML, không có text khác.

Phân loại các tin nhắn vào các nhãn sau:
- nghi: xin nghỉ cả ngày hoặc nhiều ngày (nghỉ phép, nghỉ làm, off)
- tre: xin lên trễ, đi trễ, vào muộn
- nua_buoi: xin nghỉ nửa buổi (nghỉ sáng, nghỉ chiều)
- remote: xin làm remote, làm online, work from home

---
Ví dụ 1:
Input (CSV):
message_id,name,date,message
1047,Tín Lữ,2026-01-13 23:11,Em xin phép làm remote hôm nay (14/1) do em bị sốt ạ

Output (YAML):
nghi: []
tre: []
nua_buoi: []
remote:
  - message_id: 1047
    name: Tín Lữ
    dates:
      - "2026-01-14"
    info: Làm remote do bị sốt

---
Ví dụ 2:
Input (CSV):
message_id,name,date,message
1042,Nguyễn Duy Thắng,2026-01-13 00:41,Dạ em xin phép thầy và anh chị cho em lên trễ tầm 10h ạ

Output (YAML):
nghi: []
tre:
  - message_id: 1042
    name: Nguyễn Duy Thắng
    dates:
      - "2026-01-13"
    info: Lên trễ đến 10h
nua_buoi: []
remote: []

---
Ví dụ 3:
Input (CSV):
message_id,name,date,message
1050,Minh Trần,2026-01-15 08:00,Em xin nghỉ phép ngày 16/1 và 17/1 ạ
1051,Hoa Nguyễn,2026-01-15 09:30,Em xin nghỉ buổi chiều hôm nay ạ

Output (YAML):
nghi:
  - message_id: 1050
    name: Minh Trần
    dates:
      - "2026-01-16"
      - "2026-01-17"
    info: Nghỉ phép 2 ngày
tre: []
nua_buoi:
  - message_id: 1051
    name: Hoa Nguyễn
    dates:
      - "2026-01-15"
    info: Nghỉ buổi chiều
remote: []

---
Lưu ý:
- CHỈ trả về YAML thuần, KHÔNG có markdown, KHÔNG có ```yaml
- dates là danh sách ngày theo format YYYY-MM-DD
- Nếu tin nhắn đề cập ngày d/m, convert sang YYYY-MM-DD dựa vào năm của ngày gửi
- Nếu không đề cập ngày cụ thể, dùng ngày gửi tin nhắn
- info ngắn gọn, tối đa 50 ký tự
- Category không có tin nhắn thì để mảng rỗng []
- Bỏ qua tin nhắn không thuộc loại nào"""

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
        print(prompt)  # Debug: print the prompt being sent
        response_text = await call_llm_async(prompt)
        response_text = response_text.strip()

        # Clean up response - remove markdown code blocks if present
        response_text = self._clean_llm_response(response_text)

        result = yaml.safe_load(response_text)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}: {response_text[:200]}"

        return {
            'week_key': week_data.get('week_key'),
            'week_range': week_data.get('week_range'),
            'labels': self._normalize_result(result)
        }

    def _clean_llm_response(self, text):
        """Clean LLM response to extract valid YAML."""
        import re
        text = text.strip()

        # Remove markdown code blocks (```yaml, ```yml, ``` etc.)
        match = re.search(r'^```(?:yaml|yml)?\s*\n(.*?)```\s*$', text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Fallback: strip ``` from start and end
        if text.startswith('```'):
            lines = text.split('\n')
            if lines[0].strip().startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            return '\n'.join(lines).strip()

        return text

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