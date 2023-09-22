import os
import logging
import random
import redis

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

TG_BOT_KEYBOARD = [['Новый вопрос', 'Сдаться'],
                   ['Мой счет']]
CHOOSING, TYPING_ANSWER = range(2)


def start(update, _):
    update.message.reply_text(
        fr'Привет! Я бот для викторин.',
        reply_markup=ReplyKeyboardMarkup(TG_BOT_KEYBOARD, resize_keyboard=True),
    )
    return CHOOSING


def handle_new_question_request(update, _, storage):
    questions_answers = storage.hgetall('questions-answers')
    message = random.choice(list(questions_answers))
    storage.mset({str(update.effective_user.id): message})
    update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(TG_BOT_KEYBOARD, resize_keyboard=True),
    )
    return TYPING_ANSWER


def handle_solution_attempt(update, _, storage):
    questions_answers = storage.hgetall('questions-answers')
    short_correct_answer = questions_answers[storage.get(str(update.effective_user.id))].\
        split('.', 1)[0].replace('"', '')
    if update.message.text.lower() in short_correct_answer.lower() and \
            ((update.message.text.lower().count(' ') + 1) / (short_correct_answer.lower().count(' ') + 1) * 100) > 50:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        return_params = CHOOSING
    else:
        message = 'Неправильно… Попробуешь ещё раз?'
        return_params = TYPING_ANSWER
    update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(TG_BOT_KEYBOARD, resize_keyboard=True),
    )
    return return_params


def handle_give_up(update, _, storage):
    questions_answers = storage.hgetall('questions-answers')
    short_correct_answer = questions_answers[storage.get(str(update.effective_user.id))]. \
        split('.', 1)[0].replace('"', '')
    update.message.reply_text(short_correct_answer)
    handle_new_question_request(update, _, storage)
    return TYPING_ANSWER


def handle_count(update, _, storage):
    # здесь будет подсчет результата ответов
    pass


def cancel(update, _):
    user = update.message.from_user
    logger.info(f'User {user.first_name} canceled the conversation.')
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def _error(update, _error):
    logger.warning(f'Update {update} caused error {_error}')


def main():
    load_dotenv()
    storage = redis.Redis(
        host=os.environ.get('REDIS_HOST', default='localhost'),
        port=os.environ.get('REDIS_PORT', default=6379),
        db=os.environ.get('REDIS_DB', default=0),
        decode_responses=True
    )

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    updater = Updater(os.environ.get('TELEGRAM_TOKEN'))
    dispatcher = updater.dispatcher
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^Новый вопрос$'),
                                      lambda update, _: handle_new_question_request(update, _, storage)
                                      ),
                       ],
            TYPING_ANSWER: [MessageHandler(Filters.regex('^Сдаться$'),
                                           lambda update, _: handle_give_up(update, _, storage)),
                            MessageHandler(Filters.regex('^Мой счет$'),
                                           lambda update, _: handle_count(update, _, storage)),
                            MessageHandler(Filters.text,
                                           lambda update, _: handle_solution_attempt(update, _, storage),
                                           pass_user_data=True),
                            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(_error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
