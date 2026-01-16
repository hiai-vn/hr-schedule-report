import os
import google.generativeai as genai
from typing import Optional


def call_llm(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Call Google Gemini API with a prompt and return the response.
    
    Args:
        prompt: The input prompt to send to Gemini
        model_name: The Gemini model to use (default: gemini-1.5-flash)
    
    Returns:
        The generated response text from Gemini
    
    Raises:
        ValueError: If API key is not set
        Exception: If API call fails
    """
    # Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    try:
        # Create the model
        model = genai.GenerativeModel(model_name)
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Return the response text
        return response.text
        
    except Exception as e:
        raise Exception(f"Failed to call Gemini API: {str(e)}")


def main():
    """Test function to try the Gemini API call"""
    test_prompt = "What is the capital of Vietnam?"
    try:
        result = call_llm(test_prompt)
        print(f"Prompt: {test_prompt}")
        print(f"Response: {result}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()