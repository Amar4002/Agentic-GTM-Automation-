
import google.generativeai as genai
import os

class GeminiClient:
    def __init__(self, api_key: str = None):
        key = api_key or os.getenv("AIzaSyAQs2sILS1XQyK0kYlQilpiEWTL0MCKcUE")
        if not key:
            raise ValueError("GEMINI_API_KEY missing in environment")
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))

    def generate(self, prompt: str) -> str:
        
        # Generates a message using Gemini.
    
        resp = self.model.generate_content(prompt)
        return resp.text.strip()
