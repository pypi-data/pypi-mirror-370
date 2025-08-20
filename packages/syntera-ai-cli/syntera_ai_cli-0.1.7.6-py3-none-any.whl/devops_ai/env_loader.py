import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env into os.environ

gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env file.")
print("GEMINI_API_KEY loaded successfully.")                    
    
