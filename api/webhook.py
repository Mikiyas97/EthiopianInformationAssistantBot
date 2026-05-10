import os
import asyncio
import traceback
from flask import Flask, request
from telegram import Update
from utils.bot_app import create_application

app = Flask(__name__)

# Global variable to hold the bot application instance
bot_app = None

async def get_bot_app():
    global bot_app
    if bot_app is None:
        bot_app = create_application()
        await bot_app.initialize()
    return bot_app

@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        update_json = request.get_json(force=True)
        
        async def run_bot():
            application = await get_bot_app()
            update = Update.de_json(update_json, application.bot)
            await application.process_update(update)

        # Create a new event loop for this request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_bot())
        finally:
            loop.close()

        return "OK", 200
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"Error handling update: {error_msg}")
        return f"Error: {str(e)}", 500

@app.route('/')
def index():
    return "Ethiopian Information Assistant Bot is online!"

if __name__ == '__main__':
    app.run(port=5000)
