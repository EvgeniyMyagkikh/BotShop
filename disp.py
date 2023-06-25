import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

dotenv.load_dotenv(".env")

url = os.environ.get("URL")
pay_token = os.environ.get("PAY_TOKEN")
web_app = types.WebAppInfo(url=url)
sheet_id = os.environ.get("SHEET_ID")
cred_file = "creds.json"

bot = Bot(token=os.environ.get("API_KEY"))
dp = Dispatcher(bot, storage=MemoryStorage())
