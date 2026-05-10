from utils.bot_app import create_application
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    application = create_application()
    print("🤖 Bot Running (Polling) ...")
    application.run_polling()
