import json
import os

from aiogram.client.session import aiohttp
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY=os.getenv("WEATHER_API_KEY")


async def kanye_quote():
    url = "https://api.kanye.rest"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = json.loads(await response.text())
            return data["quote"]


async def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Бишкек&appid={WEATHER_API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(f"RESPONSE = {data}")
                type_ = data["weather"][0]["main"]
                temp_c = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                city = data["name"]
                return f"Погода в городе {city}:{type_}\n Температура:{temp_c}\n Чувствуется как:{feels_like}"
            else:
                return f"Произошла ошибка"


# async def get_currency():
#     url = ""
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
