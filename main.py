import os
import argparse
import tg_bot_markups
import logging
import random
import redis

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, RegexHandler
from dotenv import load_dotenv


global questions_answers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

CHOOSING = 0


def start(bot, update):
    # print(update.message)
    # user = update.message.from_user
    update.message.reply_markdown_v2(
        fr'Привет! Я бот для викторин\.',  # {user.mention_markdown_v2()}\
        reply_markup=tg_bot_markups.first_markup,
    )
    return CHOOSING


def new_question(bot, update):
    global questions_answers
    message = list(questions_answers)[random.randrange(len(questions_answers) - 1)]
    r.mset({str(update.effective_user.id): message.encode('utf-8'), })
    update.message.reply_text(
        message,
        reply_markup=tg_bot_markups.first_markup,
    )


def echo(update: Update, context: CallbackContext):
    global questions_answers
    short_correct_answer = questions_answers[r.get(str(update.effective_user.id)).\
        decode('utf-8')].split('.', 1)[0].replace('"', '')
    if update.message.text.lower() in short_correct_answer.lower() and \
        (update.message.text.lower().count(' ') / short_correct_answer.lower().count(' ') * 100) > 50:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        message = 'Неправильно… Попробуешь ещё раз?'
    update.message.reply_text(
        message,
        reply_markup=tg_bot_markups.first_markup,
    )


def give_up(bot, update):
    pass


def my_count(bot, update):
    pass


def cancel(bot, update):
    user = update.message.from_user
    logger.info(f'User {user.first_name} canceled the conversation.')
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=tg_bot_markups.remove_markup)
    return ConversationHandler.END


def _error(bot, update, _error):
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
            question = content[content.find(':')+2:].replace('\n', ' ')
        elif 'Ответ:' in content:
            answer = content[content.find(':')+2:].replace('\n', ' ')
            questions_answers[question] = answer

    updater = Updater(os.environ.get('TELEGRAM_TOKEN'))
    dispatcher = updater.dispatcher
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [RegexHandler('^Новый вопрос$', new_question),
                       RegexHandler('^Сдаться$', give_up),
                       RegexHandler('^Мой счет$', my_count),
                       ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(_error)
    # dispatcher.add_handler(CommandHandler("start", start))
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
