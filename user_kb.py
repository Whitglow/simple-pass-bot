from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

keyb_1 = KeyboardButton('/start')
keyb_2 = KeyboardButton('/set')
keyb_3 = KeyboardButton('/get')
keyb_4 = KeyboardButton('/del')

kb_user = ReplyKeyboardMarkup(resize_keyboard=True)

kb_user.add(keyb_1).add(keyb_3).add(keyb_2).insert(keyb_4)
