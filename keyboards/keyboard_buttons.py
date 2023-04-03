from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


find_job = KeyboardButton('Знайти роботу')
subscribe = KeyboardButton('Підписатись на вакансію')



markup_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).row(
    find_job,
    subscribe,
)
