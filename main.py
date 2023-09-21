import os
import argparse
import redis


storage = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def main():
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
    question = ''
    for content in separated_contents:
        if 'Вопрос ' in content:
            question = content[content.find(':') + 2:].replace('\n', ' ')
        elif 'Ответ:' in content:
            answer = content[content.find(':') + 2:].replace('\n', ' ')
            questions_answers[question] = answer

    storage.hmset(name='questions_answers', mapping=questions_answers)
    questions_answers.clear()


if __name__ == '__main__':
    main()
