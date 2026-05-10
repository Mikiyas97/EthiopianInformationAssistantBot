import asyncio
from telegram.ext import (
    ApplicationBuilder, ConversationHandler, CommandHandler, 
    MessageHandler, CallbackQueryHandler, filters, PicklePersistence
)
from telegram.request import HTTPXRequest

# Imports from existing modules
from utils.config import (
    BOT_TOKEN, CHOOSING_MODE, AI_MODE, SELECT_SITE, ORIGINAL_MENU, TOURISM_INFO, TICKET_INFO, WAITING_FEEDBACK
)
from modules.ai_chatbot import handle_ai_chat
from modules.tourism_info import (
    handle_site_selection, handle_original_menu, handle_tourism_info, handle_ticket_info
)
from modules.feedback import start_feedback, handle_feedback_message, cancel_feedback, handle_admin_decision
from modules.help_system import help_command
from modules.explore_images import refresh_callback

# From main_handlers
from modules.main_handlers import start, handle_mode_choice, handle_user_location, cancel_directions

def create_application():
    persistence = PicklePersistence(filepath="/tmp/bot_state.pickle")
    
    t_request = HTTPXRequest(connection_pool_size=8, connect_timeout=60, read_timeout=60)
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(t_request)
        .persistence(persistence)
        .build()
    )

    # Merged Conversation Handler to prevent blocking
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("feedback", start_feedback)
        ],
        states={
            CHOOSING_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mode_choice)],
            AI_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_chat)],
            SELECT_SITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_site_selection)],
            ORIGINAL_MENU: [
                MessageHandler(filters.LOCATION, handle_user_location),
                MessageHandler(filters.Regex("^🔙 Cancel Directions$"), cancel_directions),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_original_menu)
            ],
            TOURISM_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tourism_info)],
            TICKET_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ticket_info)],
            WAITING_FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback_message)],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("cancel", cancel_feedback),
            CommandHandler("feedback", start_feedback)
        ],
        name="ethiopia_bot_conversation",
        persistent=True,
        allow_reentry=True
    )

    # Register Handlers
    application.add_handler(CommandHandler("help", help_command))
    
    # Inline Button Handlers
    application.add_handler(CallbackQueryHandler(handle_admin_decision, pattern="^feedback_"))
    application.add_handler(CallbackQueryHandler(refresh_callback, pattern="^refresh_images"))
    
    application.add_handler(conv_handler)
    
    return application
