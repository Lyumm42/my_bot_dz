from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/help')],
        [KeyboardButton(text='/start')],
        [KeyboardButton(text='/survey')],
        [KeyboardButton(text='/inet')]
    ],
    resize_keyboard=True
)


inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='GOOGLE', url='https://google.com')],
        [InlineKeyboardButton(text='YOUTUBE', url='https://www.youtube.com')],
        [InlineKeyboardButton(text='Цитата', callback_data='quote')],
        [InlineKeyboardButton(text='Погода', callback_data='weather')],
    ]
)