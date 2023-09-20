import os
import argparse
import tg_bot_markups
import logging
import random
import redis

# from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv

global questions_answers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

CHOOSING, TYPING_ANSWER = range(2)


def start(update, _):
    update.message.reply_text(
        fr'Привет! Я бот для викторин.',
        reply_markup=tg_bot_markups.first_markup,
    )
    return CHOOSING


def handle_new_question_request(update, _):
    global questions_answers
    message = list(questions_answers)[random.randrange(len(questions_answers) - 1)]
    r.mset({str(update.effective_user.id): message.encode('utf-8'), })
    update.message.reply_text(
        message,
        reply_markup=tg_bot_markups.first_markup,
    )
    return TYPING_ANSWER


def handle_solution_attempt(update, _):
    global questions_answers
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
    global questions_answers
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
    global questions_answers
    load_dotenv()

    parser = argparse.ArgumentParser(description='Приложение "Викторина"')
    parser.add_argument(
        '--path',
        nargs='?',
        default=os.path.join(os.getcwd(), 'quiz-questions'),
        help='имя папки в корне проекта с файлами вопросов-ответов '
             '(по умолчанию - quiz-questions)'
    )
    parser.add_argument(
        '--files',
        nargs='*',
        default='questions-answers.txt',
        help='имена файлов вопросов-ответов для викторины '
             '(по умолчанию - questions-answers.txt)'
    )

    path = os.path.join(os.getcwd(), parser.parse_args().path)

    for file in parser.parse_args().files:
        try:
            with open(os.path.join(path, file), "r", encoding="KOI8-R") as my_file:
                file_contents = my_file.read()
                # print(f'{file}: {file_contents[:50]}' )
        except (FileNotFoundError, ValueError) as error:
            print(f'Неверно указан путь к файлу.\nОшибка: {error}')

    separated_contents = file_contents.split('\n\n')
    questions_answers = {}
    for content in separated_contents:
        if 'Вопрос ' in content:
            question = content[content.find(':') + 2:].replace('\n', ' ')
        elif 'Ответ:' in content:
            answer = content[content.find(':') + 2:].replace('\n', ' ')
            questions_answers[question] = answer

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
