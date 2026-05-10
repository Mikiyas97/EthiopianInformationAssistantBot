import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Keys
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
FEEDBACK_CHANNEL_ID = os.getenv("FEEDBACK_CHANNEL_ID")

# States
# Added EXPLORE_IMAGES at the end
# utils/config.py

# ... existing imports ...

# Add EXPLORE_IMAGES to the end of your states list
CHOOSING_MODE, AI_MODE, SELECT_SITE, ORIGINAL_MENU, TOURISM_INFO, TICKET_INFO, WAITING_FEEDBACK, EXPLORE_IMAGES = range(8)

# ... rest of file ...

# Gemini Config
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

AI_GENERATION_CONFIG = {
    "temperature": 0.7,
    "max_output_tokens": 500,
}

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Debugging
if not BOT_TOKEN:
    print("❌ CRITICAL ERROR: BOT_TOKEN is missing!")
if not GEMINI_API_KEY:
    print("❌ CRITICAL ERROR: GEMINI_API_KEY is missing!")