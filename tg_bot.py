import logging

import requests
import telegram
from environs import Env
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext)

logger = logging.getLogger('TG logger')


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Давай начнем')


def tg_send_answer(update: Update, context: CallbackContext):
    text = update.message.text
    update.message.reply_text(text)
    # chat_id = update.message.chat_id
    # context.bot.send_message(
    #     chat_id=chat_id,
    #     text=text
    # )


def main():
    env = Env()
    env.read_env()

    tg_token = env.str('TG_TOKEN')

    tg_bot = telegram.Bot(token=tg_token)
    logger.setLevel(logging.WARNING)
    # logger.addHandler(log_handler.TelegramLogsHandler(tg_bot))

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        tg_send_answer
        )
    )

    try:
        updater.start_polling()
        updater.idle()
    except requests.exceptions.HTTPError as error:
        logger.warning('Проблема с телеграм ботом ')


if __name__ == '__main__':
    main()
