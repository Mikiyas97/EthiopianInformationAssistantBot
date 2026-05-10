import os
import asyncio
import traceback
from flask import Flask, request
from telegram import Update
from utils.bot_app import create_application

app = Flask(__name__)

# Global variable to hold the bot application instance
bot_app = None

async def process_telegram_update(update_json):
    global bot_app
    if bot_app is None:
        bot_app = create_application()
        await bot_app.initialize()
    
    update = Update.de_json(update_json, bot_app.bot)
    await bot_app.process_update(update)

@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        update_json = request.get_json(force=True)
        
        # Using the existing loop or creating a new one if necessary
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # This shouldn't happen in a standard Vercel request but handle it just in case
            future = asyncio.run_coroutine_threadsafe(process_telegram_update(update_json), loop)
            future.result()
        else:
            loop.run_until_complete(process_telegram_update(update_json))

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
