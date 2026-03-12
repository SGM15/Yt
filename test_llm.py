from app.core.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os

try:
    print(f"Testing model (settings): {settings.MODEL_NAME}")
    print(f"Testing model (env): {os.getenv('MODEL_NAME')}")
    print(f"Base URL: {settings.OPENAI_API_BASE}")
    key_start = settings.OPENAI_API_KEY[:8] if settings.OPENAI_API_KEY else "None"
    print(f"Key starts with: {key_start}...")
    print(f"Key length: {len(settings.OPENAI_API_KEY)}")
    print(f"Has whitespace: {' ' in settings.OPENAI_API_KEY}")
    
    llm = ChatOpenAI(
        model=settings.MODEL_NAME,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE,
        temperature=0
    )
    
    response = llm.invoke([HumanMessage(content="Hello")])
    print("Response:", response.content)
except Exception as e:
    print("Error:", e)
