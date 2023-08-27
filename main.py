import os
import argparse
import tg_bot_markups
import logging
import random
import redis

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv


global questions_answers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\! Я бот для викторин\.',
        reply_markup=tg_bot_markups.first_markup,
    )


def echo(update: Update, context: CallbackContext):
    global questions_answers
    if update.message.text == 'Новый вопрос':
        message = list(questions_answers)[random.randrange(len(questions_answers)-1)]
        print(update.effective_user.id)
        r.mset({str(update.effective_user.id): message.encode('utf-8'),})
    else:
        message = update.message.text
    update.message.reply_text(
        message,
        reply_markup=tg_bot_markups.first_markup,
    )
    print(r.get(str(update.effective_user.id)).decode('utf-8'))


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
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
