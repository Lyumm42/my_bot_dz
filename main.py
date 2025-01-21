import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

bot_token=os.getenv("TOKEN")

bot = Bot(token=bot_token)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(f"Hello {message.from_user.first_name}!")


@dp.message(Command("help"))
async def help_(message: Message):
    await message.answer(f"Hello {message.from_user.first_name}! you asked help")


@dp.message()
async def reply_text(message: Message):
    await message.reply(f"You typed {message.text}")


async def main():
    print("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())