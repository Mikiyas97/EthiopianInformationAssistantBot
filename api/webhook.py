import os
import asyncio
import traceback
from flask import Flask, request
from telegram import Update
from utils.bot_app import create_application

app = Flask(__name__)

async def handle_update(update_json):
    """
    Creates and runs a fresh application instance for this specific request.
    This is the most reliable way to handle PTB on Vercel/Serverless.
    """
    application = create_application()
    
    # Initialize, process update, and shutdown correctly
    async with application:
        update = Update.de_json(update_json, application.bot)
        await application.process_update(update)

@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        if request.method == "POST":
            update_json = request.get_json(force=True)
            
            # Use asyncio.run to ensure a fresh, clean event loop for every request
            # This prevents the "Event loop is closed" errors
            asyncio.run(handle_update(update_json))
            
            return "OK", 200
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"❌ WEBHOOK ERROR: {error_msg}")
        return f"Error: {str(e)}", 500
    
    return "Method Not Allowed", 405

@app.route('/')
def index():
    return "Ethiopian Information Assistant Bot is online!"

if __name__ == '__main__':
    app.run(port=5000)
