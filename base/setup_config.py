import os
from dotenv import load_dotenv

load_dotenv()

google_gemini_config = None

def get_gemini_config():
    """Returns or initializes google_gemini_config gracefully."""
    global google_gemini_config
    if google_gemini_config is not None:
        return google_gemini_config

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("[WARNING] GEMINI_API_KEY is not set. Chatbot will run in fallback mode.")
        return None

    try:
        from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
        external_client = AsyncOpenAI(
            api_key=gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        model = OpenAIChatCompletionsModel(
            model="gemini-2.0-flash",
            openai_client=external_client
        )
        google_gemini_config = RunConfig(
            model=model,
            model_provider=external_client,
            tracing_disabled=True
        )
        return google_gemini_config
    except Exception as e:
        print(f"[ERROR] Failed to initialize Gemini config: {e}")
        return None

# Try initializing at import time if key is present
try:
    if os.getenv("GEMINI_API_KEY"):
        google_gemini_config = get_gemini_config()
except Exception:
    google_gemini_config = None
