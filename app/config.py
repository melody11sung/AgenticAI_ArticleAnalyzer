import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

def verify_api_key():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return True

def get_openai_client():
    verify_api_key()
    return AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY')) 