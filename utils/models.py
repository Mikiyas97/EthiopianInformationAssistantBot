import google.generativeai as genai
from utils.config import GEMINI_API_KEY

def list_available_models():
    """Prints available Gemini models for the provided API key."""
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY is missing.")
        return

    genai.configure(api_key=GEMINI_API_KEY)
    
    print("🔍 Checking available Gemini models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"❌ Error connecting to Google AI: {e}")

if __name__ == "__main__":
    list_available_models()