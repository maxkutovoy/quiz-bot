import logging
import random

import redis
import requests.exceptions
import telegram
import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

import log_handler

logger = logging.getLogger('VK logger')


def vk_send_random_question(event, vk_api):
    vk_user_id = event.user_id

    questions = r.keys('Вопрос*')
    random_question = (random.choice(questions)).decode('utf-8')

    vk_api.messages.send(
        user_id=vk_user_id,
        random_id=random.randint(1, 1000),
        keyboard=answer_keyboard.get_keyboard(),
        message=random_question,
    )
    r.set(f'{vk_user_id}_last_question', random_question)


def vk_check_answer(event, vk_api):
    vk_user_id = event.user_id
    last_question = r.get(f'{vk_user_id}_last_question')

    if last_question:
        answer = r.get(last_question).decode('utf-8')
        edited_answer = answer.split('.')[0].split('(')[0]

        if event.text == edited_answer:
            vk_api.messages.send(
                user_id=vk_user_id,
                message='Правильно! Для следующего вопроса нажми "Новый вопрос"',
                keyboard=new_question_keyboard.get_keyboard(),
                random_id=random.randint(1, 1000)
            )
            r.delete(f'{vk_user_id}_last_question')
        else:
            vk_api.messages.send(
                user_id=vk_user_id,
                message='Неправильно… Попробуешь ещё раз?',
                keyboard=answer_keyboard.get_keyboard(),
                random_id=random.randint(1, 1000)
            )


def skip_question(event, vk_api):
    vk_user_id = event.user_id
    last_question = r.get(f'{vk_user_id}_last_question')
    answer = r.get(last_question).decode('utf-8')
    edited_answer = answer.split('.')[0].split('(')[0]

    vk_api.messages.send(
        user_id=vk_user_id,
        message=f'Правильный ответ на прошлый вопрос: {edited_answer}',
        keyboard=answer_keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )

    return vk_send_random_question(event, vk_api)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    tg_chat_id = env.str('TG_CHAT_ID')
    tg_bot = telegram.Bot(token=env.str('TG_TOKEN'))
    logger.setLevel(logging.WARNING)
    logger.addHandler(log_handler.TelegramLogsHandler(tg_bot, tg_chat_id))

    redis_host = env.str('REDIS_DB_NAME')
    redis_port = env.int('REDIS_PORT')
    redis_pass = env.str('REDIS_PASSWORD')

    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_pass,
        db=0
    )

    vk_token = env.str('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    new_question_keyboard = VkKeyboard(one_time=True)
    answer_keyboard = VkKeyboard(one_time=True)
    new_question_keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    answer_keyboard.add_button('Сдаться')

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                if event.text == 'Новый вопрос':
                    vk_send_random_question(event, vk_api)
                elif event.text == 'Сдаться':
                    skip_question(event, vk_api)
                else:
                    vk_check_answer(event, vk_api)

            except requests.exceptions.HTTPError as error:
                logger.warning('Проблема с ботом Вконтакте')
