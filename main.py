import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from services import kanye_quote, get_weather
from states import Survey
from keyboards import reply_kb, inline_kb
from db import Database

load_dotenv()

bot_token = os.getenv("TOKEN")
bot = Bot(token=bot_token)
db = Database(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME")
)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await db.check_user(message.from_user.id)
    if not user:
        await db.add_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
        await message.answer(f"Hello {message.from_user.first_name}, Ты добавлен в Базу Данных")
    else:
        await message.answer(f"С возвращением {message.from_user.username}")


@router.message(Command("help"))
async def cmd_help(message: Message):
    commands = "\n".join([
        "/start - Начать",
        "/help - Список команд",
        "/quiz - Начать викторину",
        "/survey - Пройти опрос",
        "/inet - Полезные ссылки"
    ])
    await message.answer(f"<i>Привет {message.from_user.first_name}!</i>\n{commands}", parse_mode="HTML")


@router.message(Command("inet"))
async def cmd_inet(message: Message):
    await message.answer("Вот ссылки:", reply_markup=inline_kb)



@router.message(Command("survey"))
async def cmd_survey(message: Message, state: FSMContext):
    await message.answer("Как вас зовут?")
    await state.set_state(Survey.name)


@router.message(Survey.name, F.text)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько вам лет?")
    await state.set_state(Survey.age)


@router.message(Survey.age, F.text)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Какой ваш любимый цвет?")
    await state.set_state(Survey.color)


@router.message(Survey.color, F.text)
async def process_color(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    age = data.get("age")
    color = message.text
    answer_text = (
        f"Отлично!\nСпасибо за пройденный опрос!\n"
        f"Ваш любимый цвет: {color}\n"
        f"Вам: {age} лет\n"
        f"Вас зовут: {name}"
    )
    await message.answer(answer_text)

    user = await db.check_user(message.from_user.id)
    await db.add_survey(user["id"], age, color)
    await state.clear()



@router.message(F.text)
async def reply_text(message: Message):
    if message.text.lower() == "hi":
        await message.reply("И тебе привет")
    elif message.text == "KB":
        await message.answer("Выберите опцию:", reply_markup=reply_kb)
    elif len(message.text) > 20:
        await message.reply("У тебя слишком длинный текст")
    else:
        await message.reply(f"You typed: {message.text}")


@router.message(F.photo)
async def reply_image(message: Message):
    await message.answer("Nice picture! 👍")


@router.callback_query(F.data == "quote")
async def callback_quote(call: CallbackQuery):
    quote = await kanye_quote()
    await call.message.answer(quote)
    await call.answer()


@router.callback_query(F.data == "weather")
async def callback_weather(call: CallbackQuery):
    weather = await get_weather()
    await call.message.answer(weather)
    await call.answer()



questions = [
    {"question": "Какие цвета у флага России?", "options": ["⬜🟦⬜", "⬛🟨⬜", "⬜🟦🟥", "🟨🟥🟥"], "correct": "⬜🟦🟥"},
    {"question": "Какая армия самая сильная во всём мире?", "options": ["США", "Китай", "Россия", "Северная Корея"], "correct": "армия Российской Федерации(ВСРФ)"},
    {"question": "Какая самая большая страна в мире?", "options": ["Бразилия", "Россия", "Канада", "США"], "correct": "Российская Федерация"},
    {"question": "Как зовут президента Мира?", "options": ["Байден", "Си Цзиньпин", "Путин", "Трамп"], "correct": "Владимир Путин"},
    {"question": "Как называется столица Мира?", "options": ["Берлин", "Лондон", "Москва", "Нью-Йорк"], "correct": "Москва"}
]

user_scores = {}


@router.message(Command("quiz"))
async def start_quiz(message: Message):
    user_scores[message.from_user.id] = 0
    await send_question(message.from_user.id, 0)


async def send_question(user_id: int, q_index: int):
    if q_index >= len(questions):
        score = user_scores.get(user_id, 0)
        await bot.send_message(user_id, f"Викторина окончена! Ваш результат: {score}/{len(questions)}")
        return

    question = questions[q_index]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=option, callback_data=f"quiz_{q_index}_{option}")]
            for option in question["options"]
        ]
    )
    await bot.send_message(user_id, question["question"], reply_markup=keyboard)


@router.callback_query(F.data.startswith("quiz_"))
async def handle_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    _, q_index, answer = callback.data.split("_", 2)
    q_index = int(q_index)

    correct_answer = questions[q_index]["correct"]
    if answer == correct_answer:
        user_scores[user_id] += 1
        await callback.answer("✅ Правильно!")
    else:
        await callback.answer(f"❌ Неправильно! Правильный ответ: {correct_answer}")

    await send_question(user_id, q_index + 1)



async def main():
    logging.basicConfig(level=logging.INFO)
    print("Starting bot...")
    await db.connect()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
