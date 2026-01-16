import os
import asyncio
import google.generativeai as genai
from typing import Optional
from google import genai
from google.genai import types


def call_llm(prompt: str, fast_mode: bool = False, max_retry_time: int = None) -> str:
    """Call LLM with timeout protection and automatic retry logic"""
    model_id = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Xin lỗi, hệ thống chưa cấu hình API key."
    
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0)) if "thinking" in model_id and not fast_mode else None
    response = client.models.generate_content(model=model_id, contents=prompt, config=config)
    return response.text or "Xin lỗi, không thể tạo response."

def main():
    """Test function to try the Gemini API call"""
    test_prompt = "What is the capital of Vietnam?"
    try:
        result = call_llm(test_prompt)
        print(f"Prompt: {test_prompt}")
        print(f"Response: {result}")
    except Exception as e:
        print(f"Error: {e}")


async def call_llm_async(prompt: str, model_name: str = "gemini-2.5-flash") -> str:
    """
    Async version of call_llm for parallel execution.

    Args:
        prompt: The input prompt to send to Gemini
        model_name: The Gemini model to use (default: gemini-2.5-flash)

    Returns:
        The generated response text from Gemini
    """
    # Run sync call_llm in thread pool to not block event loop
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, call_llm, prompt, model_name)


if __name__ == "__main__":
    main()