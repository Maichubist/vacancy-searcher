import asyncio
import time

from aiogram import Bot, Dispatcher, types
from dotenv import dotenv_values

from logger import logger
from keyboards.keyboard_buttons import markup_keyboard
from keyboards.inline_keyboard import markup_city
from parsers.parse_work_ua import WorkUaParser
from waiting_state import GetCity, GetExperience, GetProfession

config = dotenv_values(".env")
TOKEN = config["TOKEN"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
users = {}

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    logger.info(
        f'{message.from_user.id} {message.from_user.full_name} registred {time.asctime()}')
    await bot.send_message(chat_id=message.chat.id, text="Hello", parse_mode="HTML", reply_markup=markup_keyboard)


@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Help")


@dp.message_handler(commands=["subscribe"])
async def cmd_subscribe(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Text")


@dp.message_handler(lambda message: message.text == "Знайти роботу")
async def to_find_job(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,
                           text='Введи бажану професію, розпочни своє повідомлення з "Професія:"')


@dp.message_handler(lambda message: "Професія:" in message.text)
async def job_proccessor(message: types.Message):

    profession = (message.text).replace('Професія: ', '') if (message.text).startswith(' ') else (message.text).replace('Професія:', '')
    users[f'{message.from_user.id}'] = {'profession': profession}

    await bot.send_message(chat_id=message.chat.id, text="Обери місто, де бажаєш знайти роботу", reply_markup=markup_city)

    @dp.callback_query_handler(lambda callback_query: callback_query.from_user.id == message.from_user.id)
    async def city_proccessor(callback_query: types.CallbackQuery):

        users[f'{callback_query.from_user.id}']["city"] = (callback_query.data).replace('city_', '')
        result = WorkUaParser(vacancy=users[f'{callback_query.from_user.id}']['profession'], city=users[f'{callback_query.from_user.id}']['city']).get_result()
        await bot.send_message(callback_query.from_user.id, f"{result}, {users}")









@dp.message_handler(lambda message: message.text == "Підписатись на вакансію")
async def find_job(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=" Ти підписався  на вакансію")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
