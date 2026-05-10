from collections import deque
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.config import GEMINI_API_KEY, GEMINI_MODEL_NAME, AI_GENERATION_CONFIG, CHOOSING_MODE, AI_MODE

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_ai_keyboard():
    return ReplyKeyboardMarkup([["🔙 Back to Main Menu"]], resize_keyboard=True)

async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles interaction with Google Gemini.
    """
    user_text = update.message.text

    # 1. Handle Back Button
    if user_text == "🔙 Back to Main Menu":
        # Import here to avoid circular dependency
        from modules.tourism_info import get_start_keyboard
        await update.message.reply_text(
            "🔙 Returning to Main Menu...", 
            reply_markup=get_start_keyboard()
        )
        return CHOOSING_MODE

    # 2. UI Feedback
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # 3. History Management
    if 'history' not in context.chat_data:
        context.chat_data['history'] = deque(maxlen=10)
    
    history_buffer = context.chat_data['history']
    
    # 4. Prepare API Request
    system_prompt = """You are a helpful and knowledgeable **Ethiopian Information Assistant 🇪🇹** that provides **accurate, concise, and engaging information only about Ethiopia**, including tourism 🗺️, weather 🌦️, culture 🏛️, history 📜, food 🍲, and local travel tips 🚗. Always keep responses short, friendly, and easy to understand, using relevant emojis to enhance clarity and engagement ✨. Maintain a polite and welcoming tone, avoid speculation, and **do not provide any information beyond the Ethiopian context**—if a question is unrelated to Ethiopia, politely state that you can only assist with Ethiopia-related information.
"""
    
    gemini_history = list(history_buffer)
    gemini_history.append({'role': 'user', 'parts': [user_text]})

    try:
        # Check if key is missing before trying
        if not GEMINI_API_KEY:
            raise ValueError("API Key is missing in .env file")

        # FIX: Changed 'MODEL_NAME=' to 'model_name=' (Python arguments are case sensitive)
        model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME, system_instruction=system_prompt)
        
        response = await model.generate_content_async(gemini_history, generation_config=AI_GENERATION_CONFIG)
        ai_reply = response.text

        # 5. Update History
        history_buffer.append({'role': 'user', 'parts': [user_text]})
        history_buffer.append({'role': 'model', 'parts': [ai_reply]})

        await update.message.reply_text(ai_reply, parse_mode="Markdown")

    except Exception as e:
        # --- IMPORTANT: PRINT THE REAL ERROR TO CONSOLE ---
        print(f"\n❌ GEMINI API ERROR: {e}\n") 
        
        # Show a summary to the user
        await update.message.reply_text(f"⚠️ Error: {e}")

    return AI_MODE