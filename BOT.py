from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import hbold, hlink
import json
import aiogram.utils.exceptions
from retrying import retry
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from datetime import datetime, timedelta
import pandas as pd
from aiogram.dispatcher.filters import Command
from API import get_matches
import asyncio
import time
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN_BOT'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


select_date_callback = CallbackData("select_date", "date")


#retry(wait_fixed=200000, retry_on_exception=lambda e: isinstance(e, aiogram.utils.exceptions.RetryAfter))
@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_button = KeyboardButton('/start')
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(start_button)
    date_now = datetime.utcnow()
    dates = list(pd.date_range(start=date_now, end=date_now + timedelta(days=7)))
    keyboard = InlineKeyboardMarkup()
    for date in dates:
        button = InlineKeyboardButton(date.strftime("%d.%m"), callback_data=select_date_callback.new(date=date.strftime("%Y%m%d")))
        keyboard.add(button)
    await message.answer("Нажмите на кнопку для выбор даты", reply_markup=reply_markup)
    await message.answer("Выберите дату:", reply_markup=keyboard)


@retry(wait_fixed=20000, retry_on_exception=lambda e: isinstance(e, aiogram.utils.exceptions.RetryAfter))
async def select_date_handler(callback_query: CallbackQuery, callback_data: dict):
    try:
        selected_date = callback_data["date"]
        selected_date_obj = datetime.strptime(selected_date, "%Y%m%d")
        formatted_date = selected_date_obj.strftime("%d.%m")
        await bot.answer_callback_query(callback_query.id, text=f"Вы выбрали дату {formatted_date}\n Идёт сбор данных...")
        get_matches(selected_date)

        with open("all_matches.json") as file:
            data = json.load(file)

        for item in data:
            card = f"{hbold('Match: ')} {hlink(item.get('match_name'), item.get('link'))}\n" \
                   f"{hbold('Data: ')} {item.get('time')}\n" \
                   f"{hbold('Based on the last: ')} {item.get('sr_home')} and {item.get('sr_away')} games\n" \
                   f"{hbold('Expected total: ')} {item.get('sr_total')}\n" \
                   f"{hbold('Expected handicap: ')} {item.get('sr_handi')}\n" \
                   f"{hbold('Bookmaker total: ')} {item.get('sr_total_book')}\n" \
                   f"{hbold('Bookmaker handicap: ')} {item.get('sr_handi_book')}\n" \
                   f"{hbold('Different total: ')} {item.get('dif_total')}\n" \
                   f"{hbold('Different handicap: ')} {item.get('dif_handi')}\n" \
                   f"{hbold('H2H: ')}\n" \
                   f"{item.get('h2h')}\n"
            try:
                await asyncio.sleep(1)
                await bot.send_message(chat_id=callback_query.from_user.id, text=card)
            except asyncio.TimeoutError:
                await asyncio.sleep(1)
                await bot.send_message(chat_id=callback_query.from_user.id, text=card)
    except aiogram.utils.exceptions.InvalidQueryID:
        pass


dp.register_callback_query_handler(select_date_handler, select_date_callback.filter())
dp.register_message_handler(start, Command("start"))


def main():
    while True:
        try:
            executor.start_polling(dp, skip_updates=True, timeout=3000)
            time.sleep(10)
            bot.get_updates(timeout=1200)
        except (TimeoutError, ConnectionError, ConnectionResetError):
            time.sleep(10)
            continue


if __name__ == "__main__":
    main()
