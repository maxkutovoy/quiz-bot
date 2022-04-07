import logging
import random

import redis
import requests
import telegram
from environs import Env
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext)

logger = logging.getLogger('TG logger')


custom_keyboard = [
    ['Новый вопрос', 'Сдаться'],
    ['Мой счет']
]

reply_markup = telegram.ReplyKeyboardMarkup(
    custom_keyboard,
    resize_keyboard=True
)

remove_markup = telegram.ReplyKeyboardRemove()


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Привет! Давай начнем',
        reply_markup=reply_markup
    )


def tg_send_answer(update: Update, context: CallbackContext):

    text = update.message.text
    tg_chat_id = update.message.chat_id
    last_question = r.get(f'{tg_chat_id}_last_question')
    answer = r.get(last_question).decode('utf-8')
    print(f'Ответ пользователя: {text}')
    print(answer)

    if text == answer:
        context.bot.send_message(
            chat_id=tg_chat_id,
            text="Правильно!",
            reply_markup=reply_markup
        )
        r.delete(f'{tg_chat_id}_last_question')
    else:
        context.bot.send_message(
            chat_id=tg_chat_id,
            text="Плохой ответ",
            reply_markup=reply_markup
        )


def tg_send_random_question(update: Update, context: CallbackContext):
    tg_chat_id = update.message.chat_id

    questions = r.keys("Вопрос*")
    random_question = (random.choice(questions)).decode('utf-8')

    while r.get(f'{tg_chat_id}_last_question') is random_question:
        random_question = (random.choice(questions)).decode('utf-8')

    context.bot.send_message(
        chat_id=tg_chat_id,
        text=random_question,
        reply_markup=reply_markup
    )

    r.set(f'{tg_chat_id}_last_question', random_question)


def start_bot(tg_token):
    updater = Updater(tg_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(
        Filters.text('Новый вопрос') & ~Filters.command,
        tg_send_random_question,
        pass_user_data=True
    )
    )
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        tg_send_answer
    )
    )

    updater.start_polling()
    updater.idle()


def main():
    pass

    # questions_from_db = r.keys()
    # dispatcher.bot_data['questions'] = questions_from_db


if __name__ == '__main__':
    env = Env()
    env.read_env()

    tg_token = env.str('TG_TOKEN')

    redis_host = env.str('REDIS_DB_NAME')
    redis_port = env.int('REDIS_PORT')
    redis_pass = env.str('REDIS_PASSWORD')

    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_pass,
        db=0
    )

    tg_bot = telegram.Bot(token=tg_token)
    logger.setLevel(logging.WARNING)
    # logger.addHandler(log_handler.TelegramLogsHandler(tg_bot))

    start_bot(tg_token)
