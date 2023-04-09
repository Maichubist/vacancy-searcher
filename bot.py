import asyncio
import time
import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from logger import logger
from keyboards.keyboard_buttons import markup_keyboard, markup_keyboard_work
from keyboards.inline_keyboard import markup_city
from user import UserParser, user_service
from waiting_state import GetProfession, GetResponse



TOKEN =os.environ['TOKEN']

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


@dp.message_handler(commands=["response"])
async def cmd_start(message: types.Message):
    logger.info(
        f'{message.from_user.id} {message.from_user.full_name} left response {message.text} {time.asctime()}')
    await bot.send_message(chat_id=message.chat.id, text=f"Left a response")
    await GetResponse.waiting_for_response.set()

    @dp.message_handler(state=GetResponse.waiting_for_response)
    async def send_response(message: types.Message, state: FSMContext,):
        await state.finish()
        response = message.text
        logger.info(f"User {message.from_user.id}|{message.from_user.full_name} left response {response}")
        await bot.send_message(chat_id=message.chat.id, text=f"Thank you !{message.chat.id}")
        with open('bot.log', "rb") as f:
            document = types.InputFile(f)
            await bot.send_document(chat_id=404237030, document=document)
        with open("db/users.db", "rb") as f:
            document = types.InputFile(f)
            await bot.send_document(chat_id=404237030, document=document)



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


@dp.message_handler(lambda message: message.text == "Підписатись на вакансію")
async def find_job(message: types.Message):
    logger.info(f'{message.from_user.id} | {message.from_user.full_name} pressed "Підписатись на вакансію"')
    users[message.chat.id] = {'state': 3}
    users[message.chat.id]["tg_id"] = message.chat.id
    logger.info(users)
    await bot.send_message(chat_id=message.chat.id,
                           text="Обери місто, де плануєш шукати роботу",
                           reply_markup=markup_city)


@dp.message_handler(lambda message: message.text in ["Dou", "Djini", "Work.ua"])
async def find_vacancy_by_source(message: types.Message):
    logger.info(f'{message.from_user.id} | {message.from_user.full_name} path {users}"')
    users[message.chat.id]['source'] = message.text
    await bot.send_message(chat_id=message.chat.id, text="Обери місто, де бажаєш знайти роботу",
                           reply_markup=markup_city)


@dp.callback_query_handler(lambda calback_query: calback_query.data.startswith('city_'))
async def city_processor(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    users[callback_query.from_user.id]["city"] = callback_query.data.replace('city_', '')
    logger.info(f'{callback_query.from_user.id} | {callback_query.from_user.full_name} path {users}')
    await bot.send_message(callback_query.from_user.id, text="Веди професію", reply_markup=None)
    await GetProfession.waiting_for_profession.set()

    @dp.message_handler(state=GetProfession.waiting_for_profession)
    async def proffesion_processor(message: types.Message, state: FSMContext):
        await state.finish()
        users[message.from_user.id]['profession'] = message.text
        logger.info(f'{callback_query.from_user.id} | {callback_query.from_user.full_name} path {users}')
        try:
            await bot.send_message(chat_id=message.chat.id,
                                   text=f'{UserParser(users[message.from_user.id]).process_user_request()}')
        except TypeError as tr:
            logger.error(f"Got unexpected variable {tr}")
            await bot.send_message(chat_id=message.chat.id, text="There was unexpected error")
        except ValueError:
            await bot.send_message(chat_id=message.chat.id, text="You have already subscribed")
        except Exception:
            await bot.send_message(chat_id=message.chat.id, text="There was unexpected error")
        del users[message.from_user.id]
        logger.info(f"Deleted user {message.chat.id}")


async def send_updates():
    while True:

        r = user_service.get_update()

        for i in range(len(r)):
            if r and len(r[i][1]) > 0:
                await bot.send_message(chat_id=r[i][0], text=f"Ти підписався  на вакансію {r[i][1]}")
            else:
                await bot.send_message(chat_id=r[i][0], text=f"Нових вакансій не знайдено")

        await asyncio.sleep(60*60*4)


async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(send_updates())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
