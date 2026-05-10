from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from utils.config import (
    CHOOSING_MODE, AI_MODE, SELECT_SITE, ORIGINAL_MENU
)
from modules.ai_chatbot import get_ai_keyboard
from modules.tourism_info import (
    get_start_keyboard, get_original_menu_keyboard
)
from modules.mapping import get_google_maps_link

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    if 'history' not in context.chat_data: context.chat_data['history'] = []
    await update.message.reply_text(
        f"👋 Hello {user_name}!\n\n"
        f"👋 Welcome to the Ethiopia Information Assistant!\n\n"
        f"Your smart guide for exploring Ethiopia’s top destinations.\n\n"
        f"🌍 Tourism Info\n • History\n • Ticket prices & hours\n • Nearby hotels\n • Cultural notes\n • Safety tips & travel advice\n\n"
        f"⛅️ Weather Updates\n • Current site weather"
    )
    await update.message.reply_text(
        "🧑🏽‍🏫 Use /help to see a list of available commands and learn how to interact with the bot.",
        reply_markup=get_start_keyboard(),
        parse_mode="Markdown"
    )
    return CHOOSING_MODE

async def handle_mode_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "🏛️ Original Guide":
        await update.message.reply_text("🌍 Enter a Tourist Site:", reply_markup=ReplyKeyboardRemove())
        return SELECT_SITE
    elif choice == "🤖 AI Chatbot":
        context.chat_data['history'] = []
        await update.message.reply_text(
            "🤖 Hey! There 👋\n"
            "I’m the Ethiopian Information AI 🇪🇹🧠\n"
            "How can I help you today?", 
            reply_markup=get_ai_keyboard()
        )
        return AI_MODE
    else: return CHOOSING_MODE

async def handle_user_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_loc = update.message.location
    dest_coords = context.user_data.get('dest_coords')
    
    if user_loc and dest_coords:
        link = get_google_maps_link(
            user_loc.latitude, user_loc.longitude,
            dest_coords['lat'], dest_coords['lon']
        )
        await update.message.reply_text(
            f"🚗 **Directions Calculated!**\n\n[Click here to open Google Maps]({link})",
            parse_mode="Markdown",
            reply_markup=get_original_menu_keyboard()
        )
    else:
        await update.message.reply_text("⚠️ Could not calculate directions.", reply_markup=get_original_menu_keyboard())
    
    return ORIGINAL_MENU

async def cancel_directions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔙 Directions cancelled.", reply_markup=get_original_menu_keyboard())
    return ORIGINAL_MENU
