import os
import tg_bot_markups
import logging
import random
import redis

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_ANSWER = range(2)

# global questions_answers

r = redis.Redis(host='localhost', port=6379, db=0)


def start(update, _):
    update.message.reply_text(
        fr'Привет! Я бот для викторин.',
        reply_markup=tg_bot_markups.first_markup,
    )
    return CHOOSING


def handle_new_question_request(update, _):
    # global questions_answers
    questions_answers = r.get('questions_answers').decode('utf-8')
    print(questions_answers[:600])
    message = list(questions_answers)[random.randrange(len(questions_answers) - 1)]
    r.mset({str(update.effective_user.id): message.encode('utf-8'), })
    update.message.reply_text(
        message,
        reply_markup=tg_bot_markups.first_markup,
    )
    return TYPING_ANSWER


def handle_solution_attempt(update, _):
    # global questions_answers
    questions_answers = r.get('questions_answers').decode('utf-8')
    short_correct_answer = questions_answers[r.get(str(update.effective_user.id)).decode('utf-8')].\
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
        reply_markup=tg_bot_markups.first_markup,
    )
    return return_params


def handle_give_up(update, _):
    # global questions_answers
    questions_answers = r.get('questions_answers').decode('utf-8')
    short_correct_answer = questions_answers[r.get(str(update.effective_user.id)).decode('utf-8')]. \
        split('.', 1)[0].replace('"', '')
    update.message.reply_text(short_correct_answer)
    handle_new_question_request(update, _)
    return TYPING_ANSWER


def my_count(update, _):
    pass


def cancel(update, _):
    user = update.message.from_user
    logger.info(f'User {user.first_name} canceled the conversation.')
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=tg_bot_markups.remove_markup)
    return ConversationHandler.END


def _error(update, _error):
    logger.warning(f'Update {update} caused error {_error}')


def main():
    load_dotenv()

    updater = Updater(os.environ.get('TELEGRAM_TOKEN'))
    dispatcher = updater.dispatcher
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^Новый вопрос$'), handle_new_question_request),
                       ],
            TYPING_ANSWER: [MessageHandler(Filters.regex('^Сдаться$'), handle_give_up),
                            MessageHandler(Filters.regex('^Мой счет$'), my_count),
                            MessageHandler(Filters.text, handle_solution_attempt, pass_user_data=True),
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
