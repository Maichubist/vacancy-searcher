from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


find_job = KeyboardButton('Знайти роботу')
subscribe = KeyboardButton('Підписатись на вакансію')
find_by_source = KeyboardButton('Шукати вакансію на певному ресурсі')



markup_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).row(
    find_job,
    subscribe,
).add(
    find_by_source,
)

work_ua = KeyboardButton('Work.ua')
rabota_ua = KeyboardButton('Rabota.ua')
djini = KeyboardButton('Djini')
dou = KeyboardButton('Dou')

markup_keyboard_work = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).row(
    work_ua,
    rabota_ua,
    djini,
    dou,
)