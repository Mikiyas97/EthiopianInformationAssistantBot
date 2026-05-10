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
        from modules.tourism_info import get_start_keyboard
        await update.message.reply_text(
            "🔙 Returning to Main Menu...", 
            reply_markup=get_start_keyboard()
        )
        return CHOOSING_MODE

    # 2. UI Feedback
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing")

        # Prepare System Prompt
        system_prompt = (
            "You are a helpful and knowledgeable Ethiopian Information Assistant 🇪🇹. "
            "Provide accurate, concise information about Ethiopia only. "
            "Tourism, weather, culture, history, food, and local travel tips. "
            "Keep responses short, friendly, and use emojis. "
            "If asked about anything outside Ethiopia, politely decline."
        )

        # Initialize Model
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            system_instruction=system_prompt
        )

        # Retrieve history from context (stored as simple dicts for persistence safety)
        if 'chat_history' not in context.chat_data:
            context.chat_data['chat_history'] = []
        
        # Convert simple dicts back to Gemini format
        gemini_history = []
        for msg in context.chat_data['chat_history']:
            gemini_history.append({"role": msg["role"], "parts": [msg["content"]]})

        # Start a chat session with the history
        chat_session = model.start_chat(history=gemini_history)
        
        # Send message and get response
        response = await chat_session.send_message_async(user_text, generation_config=AI_GENERATION_CONFIG)
        ai_reply = response.text

        # Update persistent history (keep it simple for Pickle)
        context.chat_data['chat_history'].append({"role": "user", "content": user_text})
        context.chat_data['chat_history'].append({"role": "model", "content": ai_reply})
        
        # Limit history to last 10 exchanges
        if len(context.chat_data['chat_history']) > 20:
            context.chat_data['chat_history'] = context.chat_data['chat_history'][-20:]

        await update.message.reply_text(ai_reply, parse_mode="Markdown")

    except Exception as e:
        print(f"❌ GEMINI API ERROR: {e}") 
        await update.message.reply_text(f"⚠️ I'm having trouble connecting to my AI brain. Please try again in a moment.")

    return AI_MODE
