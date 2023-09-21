import os
import random
import urllib
import vk_api as vk
import logging

from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from urllib.error import HTTPError


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def echo(event, vk_api, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1,1000),
        keyboard=keyboard.get_keyboard(),
    )


# def answer(event, vk_api, project_id):
#     # intent_text, is_fallback = functions.detect_intent_text(project_id, event.user_id, event.text, 'ru')
#     # if not is_fallback:
#     vk_api.messages.send(
#         user_id=event.user_id,
#         message=intent_text,
#         random_id=random.randint(1, 1000)
#     )


def main():
    load_dotenv()
    # logger = functions.set_logger()
    # project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    vk_token = os.getenv('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Белая кнопка', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Зелёная кнопка', color=VkKeyboardColor.POSITIVE)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Красная кнопка', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Синяя кнопка', color=VkKeyboardColor.PRIMARY)

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                echo(event, vk_api, keyboard)
                # answer(event, vk_api, project_id)
            except urllib.error.HTTPError as error:
                logger.error(f'VK-бот упал с ошибкой: {error} {error.url}')
            except Exception as error:
                logger.error(f'VK-бот упал с ошибкой: {error}')


if __name__ == '__main__':
    main()
