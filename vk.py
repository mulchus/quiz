import os
import random
import urllib
import vk_api as vk
import logging
import redis

from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from urllib.error import HTTPError


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def handle_new_question_request(event, vk_api, storage):
    questions_answers = storage.hgetall('questions-answers')
    message = list(questions_answers)[random.randrange(len(questions_answers) - 1)]
    storage.mset({str(event.user_id): message})
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1,1000),
    )


def handle_solution_attempt(event, vk_api, storage):
    questions_answers = storage.hgetall('questions-answers')
    short_correct_answer = questions_answers[storage.get(str(event.user_id))].\
        split('.', 1)[0].replace('"', '')
    if event.text.lower() in short_correct_answer.lower() and \
            ((event.text.lower().count(' ') + 1) / (short_correct_answer.lower().count(' ') + 1) * 100) > 50:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    else:
        message = 'Неправильно… Попробуешь ещё раз?'
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1,1000),
    )


def handle_give_up(event, vk_api, storage):
    questions_answers = storage.hgetall('questions-answers')
    short_correct_answer = questions_answers[storage.get(str(event.user_id))]. \
        split('.', 1)[0].replace('"', '')
    vk_api.messages.send(
        user_id=event.user_id,
        message=short_correct_answer,
        random_id=random.randint(1,1000),
    )
    return handle_new_question_request(event, vk_api, storage)


def handle_my_count(event, vk_api, storage):
    pass


def _error(update, _error):
    logger.warning(f'Update {update} caused error {_error}')


def echo(event, vk_api, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1,1000),
        keyboard=keyboard.get_keyboard(),
    )


def main():
    load_dotenv()
    storage = redis.Redis(
        host=os.environ.get('REDIS_HOST', default='localhost'),
        port=os.environ.get('REDIS_PORT', default=6379),
        db=os.environ.get('REDIS_DB', default=0),
        decode_responses=True)

    vk_token = os.getenv('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Завершить', color=VkKeyboardColor.PRIMARY)

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                if event.text.lower() == "привет" or event.text.lower() == "старт":
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message="Привет. Стартуем викторину!",
                        random_id=random.randint(1,1000),
                        keyboard=keyboard.get_keyboard(),
                    )
                    handle_new_question_request(event, vk_api, storage)
                elif event.text == "Новый вопрос":
                    handle_new_question_request(event, vk_api, storage)
                elif event.text == "Сдаться":
                    handle_give_up(event, vk_api, storage)
                elif event.text == "Мой счет":
                    handle_my_count(event, vk_api, storage)
                elif event.text == "Завершить":
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message='Пока-пока!!!!',
                        random_id=random.randint(1,1000),
                    )
                else:
                    handle_solution_attempt(event, vk_api, storage)
            except urllib.error.HTTPError as error:
                logger.error(f'VK-бот упал с ошибкой: {error} {error.url}')
            except Exception as error:
                logger.error(f'VK-бот упал с ошибкой: {error}')


if __name__ == '__main__':
    main()
