from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from utils.config import FEEDBACK_CHANNEL_ID, CHOOSING_MODE, WAITING_FEEDBACK

# Import this to return to main menu after feedback
from modules.tourism_info import get_start_keyboard

async def start_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Entry point: Asks user to type their comment.
    """
    await update.message.reply_text(
        "📝 **Feedback & Suggestions**\n\n"
        "Please type your comment, suggestion, or issue below.\n\n"
        "Type /cancel to stop.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return WAITING_FEEDBACK

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives the text, formats it, and sends it to the Admin Channel.
    """
    user = update.effective_user
    feedback_text = update.message.text
    
    # 1. Format the message for the Admin Channel
    admin_message = (
        f"📩 **New User Feedback**\n\n"
        f"👤 **User:** {user.first_name} {user.last_name or ''}\n"
        f"🔗 **Username:** @{user.username if user.username else 'N/A'}\n"
        f"🆔 **User ID:** `{user.id}`\n\n"
        f"💬 **Comment:**\n{feedback_text}"
    )

    # 2. Create Inline Buttons (Accept / Reject)
    keyboard = [
        [
            InlineKeyboardButton("✅ Accept", callback_data="feedback_accept"),
            InlineKeyboardButton("❌ Reject", callback_data="feedback_reject")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 3. Send to Channel
    if FEEDBACK_CHANNEL_ID:
        try:
            await context.bot.send_message(
                chat_id=FEEDBACK_CHANNEL_ID,
                text=admin_message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                "✅ Thank you! Your feedback has been sent to our team.",
                reply_markup=get_start_keyboard()
            )
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error sending feedback: {e}", reply_markup=get_start_keyboard())
    else:
        await update.message.reply_text("⚠️ Admin channel not configured.", reply_markup=get_start_keyboard())

    # Return to Main Menu state
    return CHOOSING_MODE

async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the feedback operation."""
    await update.message.reply_text("❌ Feedback cancelled.", reply_markup=get_start_keyboard())
    return CHOOSING_MODE

# --- CALLBACK HANDLER FOR ADMIN BUTTONS ---

async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the Accept/Reject buttons in the channel.
    """
    query = update.callback_query
    await query.answer() # Close the loading animation

    data = query.data

    if data == "feedback_reject":
        # Delete the message
        try:
            await query.message.delete()
        except Exception as e:
            await query.edit_message_text(f"❌ Could not delete: {e}")
    
    elif data == "feedback_accept":
        # Remove buttons and append "Accepted" tag
        original_text = query.message.text_markdown
        new_text = f"{original_text}\n\n✅ **STATUS: ACCEPTED**"
        
        await query.edit_message_text(
            text=new_text,
            parse_mode="Markdown"
        )