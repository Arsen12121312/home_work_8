from telegram import Update, Bot
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, run_async
from telegram.utils.helpers import mention_html
from threading import Thread
from datetime import datetime, timedelta
from time import sleep


BOT_TOKEN = "my_bot"

bad_words = ['durak', 'tupoi', 'debil']

user_violations = {}


def is_admin(user_id):
    return user_id == ADMIN_ID


def get_username(user_id):
    user = bot.get_chat(user_id)
    return user.username or user.first_name


def is_bad_word(text):
    return any(word in text for word in bad_words)


def handle_new_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = get_username(user_id)
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    message_text = update.message.text

    if is_bad_word(message_text):
        if not is_admin(user_id):
            user_violations[user_id] = user_violations.get(user_id, 0) + 1
            if user_violations[user_id] >= 3:
                bot.kick_chat_member(chat_id, user_id)
                bot.send_message(chat_id, f"{mention_html(user_id, username)} покинул группу.")
                del user_violations[user_id]
            else:
                context.bot.restrict_chat_member(chat_id, user_id, can_send_messages=False,
                                                 until_date=datetime.now() + timedelta(days=1))
                bot.send_message(chat_id, f"{mention_html(user_id, username)} забанен на 24 часа.")
        else:
            bot.send_message(chat_id, f"{mention_html(user_id, username)} - админ, его нельзя забанить.")


def main():
    bot = Bot(BOT_TOKEN)

    dp = bot.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_new_message))

    bot.set_my_commands(["/start", "/help"])
    print(f"Start listening @{bot.get_me().username} for {bot.username} with token: {BOT_TOKEN}")
    run_async(dp)

    while True:
        sleep(10)


if __name__ == '__main__':
    main()