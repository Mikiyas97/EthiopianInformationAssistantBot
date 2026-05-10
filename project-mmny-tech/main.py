from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, 
    ConversationHandler, CallbackQueryHandler
)
from telegram.request import HTTPXRequest 

# Imports
from utils.config import (
    BOT_TOKEN, CHOOSING_MODE, AI_MODE, SELECT_SITE, ORIGINAL_MENU, TOURISM_INFO, TICKET_INFO, WAITING_FEEDBACK
)
from modules.ai_chatbot import handle_ai_chat, get_ai_keyboard
from modules.tourism_info import (
    handle_site_selection, handle_original_menu, handle_tourism_info, handle_ticket_info, 
    get_start_keyboard, get_original_menu_keyboard
)
from modules.feedback import start_feedback, handle_feedback_message, cancel_feedback, handle_admin_decision
from modules.help_system import help_command
from modules.mapping import get_google_maps_link
from modules.explore_images import refresh_callback

# --- START ---
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
        # --- UPDATED MESSAGE HERE ---
        await update.message.reply_text(
            "🤖 Hey! There 👋\n"
            "I’m the Ethiopian Information AI 🇪🇹🧠\n"
            "How can I help you today?", 
            reply_markup=get_ai_keyboard()
        )
        return AI_MODE
    else: return CHOOSING_MODE

# --- NEW: HANDLE USER SHARING LOCATION FOR DIRECTIONS ---
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
            reply_markup=get_original_menu_keyboard() # Return to menu
        )
    else:
        await update.message.reply_text("⚠️ Could not calculate directions.", reply_markup=get_original_menu_keyboard())
    
    return ORIGINAL_MENU

async def cancel_directions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔙 Directions cancelled.", reply_markup=get_original_menu_keyboard())
    return ORIGINAL_MENU

# --- MAIN ---
if __name__ == '__main__':
    # Increase connection pool and timeouts for slower networks
    t_request = HTTPXRequest(connection_pool_size=8, connect_timeout=60, read_timeout=60)
    application = ApplicationBuilder().token(BOT_TOKEN).request(t_request).build()

    feedback_conv = ConversationHandler(
        entry_points=[CommandHandler("feedback", start_feedback)],
        states={WAITING_FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback_message)]},
        fallbacks=[CommandHandler("cancel", cancel_feedback)]
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mode_choice)],
            AI_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_chat)],
            SELECT_SITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_site_selection)],
            ORIGINAL_MENU: [
                MessageHandler(filters.LOCATION, handle_user_location), # Handle Location Sharing
                MessageHandler(filters.Regex("^🔙 Cancel Directions$"), cancel_directions),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_original_menu)
            ],
            TOURISM_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tourism_info)],
            TICKET_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ticket_info)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    # Register Handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(feedback_conv)
    
    # Inline Button Handlers
    application.add_handler(CallbackQueryHandler(handle_admin_decision, pattern="^feedback_"))
    application.add_handler(CallbackQueryHandler(refresh_callback, pattern="^refresh_images"))
    
    application.add_handler(conv_handler)
    
    print("🤖 Bot Running ...")
    application.run_polling()