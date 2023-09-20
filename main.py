import os
import argparse
# import tg_bot_markups
import logging
import random
import redis
# import tg


# from telegram import Update
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv

# global questions_answers

r = redis.Redis(host='localhost', port=6379, db=0)


def main():
    # global questions_answers
    # load_dotenv()

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

    r.mset({'questions_answers': str(questions_answers), })

    questions_answers.clear()

    print(questions_answers)
    questions_answers = r.get('questions_answers').decode('utf-8')
    print(questions_answers[:500])


if __name__ == '__main__':
    main()
