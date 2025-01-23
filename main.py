import asyncio
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv

from states import Survey
from keyboards import reply_kb, inline_kb
load_dotenv()

bot_token=os.getenv("TOKEN")

bot = Bot(token=bot_token)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f"Hello {message.from_user.first_name}")


@router.message(Command(commands="help"))
async def cmd_help(message: Message):
    await message.answer(f"<i>Hello {message.from_user.first_name}! you asked help</i>", parse_mode="HTML")


@router.message(Command(commands='inet'))
async def cmd_inet(message: Message):
    await message.answer("Вот ссылки", reply_markup=inline_kb)


@router.message(Command(commands="survey"))
async def cmd_survey(message: Message, state: FSMContext):
    await message.answer("Как вас зовут?")
    await state.set_state(Survey.name)


@router.message(Survey.name, F.text)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько вам лет ?")
    await state.set_state(Survey.age)


@router.message(Survey.age, F.text)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Какой ваш любимый цвет ?")
    await state.set_state(Survey.color)


@router.message(Survey.color, F.text)
async def process_color(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    age = data.get("age")
    color = message.text
    answer_text = f"""
                    Отлично !!!\n Спасибо за пройденный опрос!!!
                    Ваш любимый цвет {color}\nВам {age} лет\nВас зовут {name}"""
    await message.answer(answer_text)
    await state.clear()


# @router.message(F.text == "Hello")
# async def reply_hello(message: Message):
#     await message.reply(f"HIII !!!")


@router.message(F.text)
async def reply_text(message: Message):
    if message.text == "Hi":
        await message.reply("И тебе привет")
    elif len(message.text) > 20:
        await message.reply("У тебя слишком длинный текст")
    elif message.text == "KB":
        await message.answer("Выберете опцию:", reply_markup=reply_kb)
    else:
        await message.reply(f"You typed {message.text}")


@router.message(F.photo)
async def reply_image(message: Message):
    await message.answer(f"Nice picture! 👍")



async def main():
    print("Starting bot...")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())