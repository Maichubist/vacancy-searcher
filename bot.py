import asyncio
import time

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from dotenv import dotenv_values

from logger import logger
from keyboards.keyboard_buttons import markup_keyboard, markup_keyboard_work
from keyboards.inline_keyboard import markup_city
from parsers.parse_work_ua import WorkUaParser
from parsers.parse_djini import DjiniParser
from parsers.parse_dou import DouParser
from waiting_state import GetCity, GetExperience, GetProfession
from db.user import user_service

config = dotenv_values(".env")
TOKEN = config["TOKEN"]

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
users = {}


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    logger.info(
        f'{message.from_user.id} | {message.from_user.full_name} registred {time.asctime()}')
    await bot.send_message(chat_id=message.chat.id, text="Hello", parse_mode="HTML", reply_markup=markup_keyboard)


@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    logger.info(f'{message.from_user.id} | {message.from_user.full_name} asked help')
    await bot.send_message(chat_id=message.chat.id, text="Help")


@dp.message_handler(commands=["subscribe"])
async def cmd_subscribe(message: types.Message):
    logger.info(f'{message.from_user.id} | {message.from_user.full_name} subscribed')
    await bot.send_message(chat_id=message.chat.id, text="Text")


@dp.message_handler(lambda message: message.text == "Знайти роботу")
async def to_find_job(message: types.Message):
    logger.info(f'{message.from_user.id} | {message.from_user.full_name} pressed "Знайти роботу"')
    logger.info(f"Created new user {message.chat.id}")
    users[message.chat.id] = {'state': 1}
    logger.info(users)
    await bot.send_message(chat_id=message.chat.id,
                           text='Обери місто, де хочеш знайти роботу', reply_markup=markup_city)


@dp.message_handler(lambda message: message.text == "Шукати вакансію на певному ресурсі")
async def find_vacancy(message: types.Message):
    logger.info(f'{message.from_user.id} | {message.from_user.full_name} pressed "Шукати вакансію на певному ресурсі"')
    users[message.chat.id] = {'state': 2}
    logger.info(users)
    await bot.send_message(chat_id=message.chat.id, text="Обери ресурс, де прагнеш знайти вакансію мрії",
                           reply_markup=markup_keyboard_work)


@dp.message_handler(lambda message: message.text in ["Dou", "Djini", "Work.ua", "Rabota.ua"])
async def find_vacancy_by_source(message: types.Message):
    logger.info(f'{message.from_user.id} | {message.from_user.full_name} path {users}"')
    users[message.chat.id]['source'] = message.text
    await bot.send_message(chat_id=message.chat.id, text="Обери місто, де бажаєш знайти роботу",
                           reply_markup=markup_city)


@dp.callback_query_handler(lambda calback_query: calback_query.data.startswith('city_'))
async def city_processor(callback_query: types.CallbackQuery):
    users[callback_query.from_user.id]["city"] = callback_query.data.replace('city_', '')
    logger.info(f'{callback_query.from_user.id} | {callback_query.from_user.full_name} path {users}')
    await bot.send_message(callback_query.from_user.id, text="Веди професію")
    await GetProfession.waiting_for_profession.set()

    @dp.message_handler(state=GetProfession.waiting_for_profession)
    async def proffesion_processor(message: types.Message, state: FSMContext):
        await state.finish()
        users[message.from_user.id]['profession'] = message.text
        logger.info(f'{callback_query.from_user.id} | {callback_query.from_user.full_name} path {users}')

        if users[message.chat.id]['state'] == 2:
            source = users[message.from_user.id]['source']
            if source == "Dou":
                try:
                    result_do = DouParser(vacancy=users[message.from_user.id]['profession'],
                                          city=users[message.from_user.id]['city']).get_result()
                    await bot.send_message(chat_id=message.chat.id, text=f'{result_do}')
                    logger.info(f'{message.from_user.id} | {message.from_user.full_name} got asked result {result_do}')
                except Exception as er:
                    logger.error(f'{message.from_user.id} | {message.from_user.full_name} ERROR {er}')
                logger.info(f'{message.from_user.id} | {message.from_user.full_name} got asked result')
            elif source == "Djini":
                try:
                    result_d = DjiniParser(vacancy=users[message.from_user.id]['profession'],
                                           city=users[message.from_user.id]['city']).get_result()
                    await bot.send_message(chat_id=message.chat.id, text=f'{result_d}')
                    logger.info(f'{message.from_user.id} | {message.from_user.full_name} got asked result {result_d}')
                except Exception as er:
                    logger.error(f'{message.from_user.id} | {message.from_user.full_name} ERROR {er}')
            elif source == "Work.ua":
                try:
                    result_w = WorkUaParser(vacancy=users[message.from_user.id]['profession'],
                                            city=users[message.from_user.id]['city']).get_result()
                    await bot.send_message(chat_id=message.chat.id, text=f'{result_w}')
                    logger.info(f'{message.from_user.id} | {message.from_user.full_name} got asked result {result_w}')
                except Exception as err:
                    logger.error(f'{message.from_user.id} | {message.from_user.full_name} ERROR {err}')
            elif source == "Rabota.ua":
                await bot.send_message(chat_id=message.chat.id, text=f'Сервіс в розробці')
                logger.info(f'{message.from_user.id} | {message.from_user.full_name} got asked result')
            else:
                await bot.send_message(chat_id=message.chat.id, text="Something went wrong")
                logger.error(f'{message.from_user.id} | {message.from_user.full_name} invalid source {source}')

        elif users[message.chat.id]['state'] == 1:
            try:
                result_d = DjiniParser(vacancy=users[message.from_user.id]['profession'],
                                       city=users[message.from_user.id]['city']).get_result()
                result_w = WorkUaParser(vacancy=users[message.from_user.id]['profession'],
                                        city=users[message.from_user.id]['city']).get_result()
                result_do = DouParser(vacancy=users[message.from_user.id]['profession'],
                                       city=users[message.from_user.id]['city']).get_result()
                await bot.send_message(callback_query.from_user.id, f'{result_w}, {result_d}, {result_do}, {users}')
                logger.info(
                    f'{message.from_user.id} | {message.from_user.full_name} got asked result {result_d} {result_w} {result_do}')
            except Exception as error:
                logger.error(f'{message.from_user.id} | {message.from_user.full_name} ERROR {error}')
        else:
            logger.critical(f'{message.from_user.id} | {message.from_user.full_name} DIDN`T GET RESULT. PROBLEM IS '
                            f'|| {users}')
        del users[message.from_user.id]
        logger.info(f"Deleted user {message.chat.id}")


@dp.message_handler(lambda message: message.text == "Підписатись на вакансію")
async def find_job(message: types.Message):
    logger.info(f'{message.from_user.id} | {message.from_user.full_name} pressed "Підписатись на вакансію"')
    users[message.chat.id] = {'state': 3}
    logger.info(users)
    user_service.add_user(tg_id=message.chat.id, profession='Python', city='Dnipro')
    await bot.send_message(chat_id=message.chat.id,
                           text="Ти успішно підписався на вакансію, чекай підбірку нових вакансій кожного вечора")


async def send_updates():
    while True:

        r = user_service.get_update()
        # user_service.update_time(tg_id=message.chat.id)
        if r and len(r[0][1]) > 0:

            for i in range(len(r)):
                await bot.send_message(chat_id=r[i][0], text=f"Ти підписався  на вакансію {r}")
        await asyncio.sleep(5)


async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(send_updates())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
