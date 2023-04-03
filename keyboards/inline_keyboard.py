from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

markup_city = InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
markup_city.add(
    InlineKeyboardButton("Вся Україна", callback_data='city_all'),
    InlineKeyboardButton("Дніпро", callback_data='city_dnipro'),
    InlineKeyboardButton("Київ", callback_data='city_kiyv'),
    InlineKeyboardButton("Харків", callback_data='city_kharkiv'),
    InlineKeyboardButton("Одеса", callback_data='city_odesa'),
    InlineKeyboardButton("Львів", callback_data='city_lviv'),
    InlineKeyboardButton("Івано-Франківськ", callback_data='city_franik'),
    InlineKeyboardButton("Ужгород", callback_data='city_uzhhorod'),
)
