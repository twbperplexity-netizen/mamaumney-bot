import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

# Load environment variables from .env file
load_dotenv()

# Get Telegram token from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
