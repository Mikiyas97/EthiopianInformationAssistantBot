from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Displays a help message listing all available commands and features.
    """
    help_text = (
        "💡 **Ethiopia Information Assistant - Help Guide**\n\n"
        
        "**🤖 Bot Modes:**\n"
        "1️⃣ **Original Guide:**\n"
        "   • Browse specific tourist sites.\n"
        "   • View 📸 Images, 📜 History, and 🎟️ Prices.\n"
        "   • Get 📍 Maps and 🚗 Driving Directions.\n"
        "   • Check real-time ⛅ Weather.\n\n"
        "2️⃣ **AI Chatbot:**\n"
        "   • Ask free-form questions (e.g., 'Best time to visit Lalibela?').\n"
        "   • Powered by Google Gemini.\n\n"
        
        "**🌍 How to Use:**\n"
        "• Type the name of a place (e.g., 'Axum') to start.\n"
        "• Use the buttons to navigate between menus.\n"
        "• If you share your location when asked, the bot calculates driving directions!\n\n"
        
        "**🛠️ Available Commands:**\n"
        "/start - Restart the bot\n"
        "/help - Show this guide\n"
        "/feedback - Send a suggestion or report a bug to Admins\n"
        "/cancel - Stop the current action\n\n"
        
        "ℹ️ *Tip: If the AI gets stuck, type 'Back' to return to the main menu.*"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")