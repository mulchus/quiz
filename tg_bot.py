import os
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import tg_bot_murkups


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\! \/nЯ бот для викторин\.',
        reply_markup=tg_bot_murkups.first_markup,
    )


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(
        update.message.text,
        reply_markup=tg_bot_murkups.remove_markup,
    )


def start_bot():
    updater = Updater(os.environ.get('TELEGRAM_TOKEN'))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()
