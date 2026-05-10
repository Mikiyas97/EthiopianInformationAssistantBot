import os
import asyncio
from flask import Flask, request
from telegram import Update
from utils.bot_app import create_application

app = Flask(__name__)

# Initialize the application globally
# Note: Vercel may reuse this instance between requests
bot_app = create_application()

async def handle_update(update_json):
    # Ensure the bot_app is initialized
    if not bot_app.running:
        await bot_app.initialize()
    
    update = Update.de_json(update_json, bot_app.bot)
    await bot_app.process_update(update)

@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        try:
            update_json = request.get_json(force=True)
            # Run the async handler
            asyncio.run(handle_update(update_json))
            return "OK", 200
        except Exception as e:
            print(f"Error handling update: {e}")
            return "Error", 500
    return "Method Not Allowed", 405

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(port=5000)
