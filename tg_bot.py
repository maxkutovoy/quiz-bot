import logging
import random

import redis
import requests
import telegram
from environs import Env
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext, ConversationHandler)

import log_handler

logger = logging.getLogger('TG logger')



new_question_markup = telegram.ReplyKeyboardMarkup(
    [
        ['Новый вопрос'],
        ['Мой счет']
    ],
    resize_keyboard=True
)

answer_keyboard = telegram.ReplyKeyboardMarkup(
    [
        ['Сдаться'],
        ['Мой счет']
    ],
    resize_keyboard=True
)

remove_markup = telegram.ReplyKeyboardRemove()

QUESTION = range(3)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Привет! Давай начнем',
        reply_markup=new_question_markup
    )
    return QUESTION


def tg_check_answer(update: Update, context: CallbackContext):

    text = update.message.text
    tg_chat_id = update.message.chat_id
    last_question = r.get(f'{tg_chat_id}_last_question')
    answer = r.get(last_question).decode('utf-8')
    edited_answer = answer.split('.')[0].split('(')[0]

    if text == edited_answer:
        context.bot.send_message(
            chat_id=tg_chat_id,
            text='Правильно! Для следующего вопроса нажми "Новый вопрос"',
            reply_markup=new_question_markup
        )
        r.delete(f'{tg_chat_id}_last_question')
    else:
        context.bot.send_message(
            chat_id=tg_chat_id,
            text='Неправильно… Попробуешь ещё раз?',
            reply_markup=answer_keyboard
        )
    return QUESTION


def tg_send_random_question(update: Update, context: CallbackContext):
    tg_chat_id = update.message.chat_id

    questions = r.keys('Вопрос*')
    random_question = (random.choice(questions)).decode('utf-8')

    context.bot.send_message(
        chat_id=tg_chat_id,
        text=random_question,
        reply_markup=answer_keyboard
    )

    r.set(f'{tg_chat_id}_last_question', random_question)

    return QUESTION


def skip_question(update: Update, context: CallbackContext):
    tg_chat_id = update.message.chat_id
    last_question = r.get(f'{tg_chat_id}_last_question')
    answer = r.get(last_question).decode('utf-8')
    edited_answer = answer.split('.')[0].split('(')[0]

    context.bot.send_message(
        chat_id=tg_chat_id,
        text=f'Правильный ответ на прошлый вопрос: {edited_answer}',
        reply_markup=answer_keyboard
    )

    return tg_send_random_question(update, context)


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('До свидания',
                              reply_markup=remove_markup)

    return ConversationHandler.END


def start_bot(tg_token):
    updater = Updater(tg_token, use_context=True)
    dispatcher = updater.dispatcher

    question_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            QUESTION: [
                MessageHandler(Filters.text('Новый вопрос'), tg_send_random_question),
                MessageHandler(Filters.text('Сдаться'), skip_question),
                MessageHandler(Filters.text, tg_check_answer),
            ],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(question_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    env = Env()
    env.read_env()

    tg_token = env.str('TG_TOKEN')
    tg_chat_id = env.str('TG_CHAT_ID')

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
    logger.addHandler(log_handler.TelegramLogsHandler(tg_bot, tg_chat_id))

    try:
        start_bot(tg_token)
    except requests.exceptions.HTTPError as error:
        logger.warning('Проблема с ботом Телеграм')
