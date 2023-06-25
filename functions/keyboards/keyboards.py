from aiogram import types

from disp import web_app

menu_btn = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Меню", web_app=web_app)]
    ],
    resize_keyboard=True
)

buttons = [
    [types.InlineKeyboardButton(text="Копим", callback_data="Yes"),
     types.InlineKeyboardButton(text="Списываем", callback_data="No")]
]
points_kbd = types.InlineKeyboardMarkup(inline_keyboard=buttons)

