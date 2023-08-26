import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


buttons = [
    [
        InlineKeyboardButton('top-left', callback_data='top-left'),
        InlineKeyboardButton('top-right', callback_data='top-right'),
    ],
    [
        InlineKeyboardButton('center', callback_data='center'),
    ],
    [
        InlineKeyboardButton('bottom-left', callback_data='bottom-left'),
        InlineKeyboardButton('bottom-right', callback_data='bottom-right'),
    ],
]
second_markup = InlineKeyboardMarkup(buttons)

keyboard = [['Новый вопрос', 'Сдаться'],
            ['Мой счет']]
first_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

remove_markup = telegram.ReplyKeyboardRemove()
