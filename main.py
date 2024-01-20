import os
import sqlite3
from dotenv import load_dotenv
from telebot import TeleBot
from handler_general import handle_start, handle_cancel, handle_change_lang
from handler_workout_plan import handle_create

# Initialize the bot with your token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start_handler(message, bot=bot):
    lang_code = get_user_language(message)
    handle_start(bot, message, lang_code)


@bot.message_handler(commands=["cancel"])
def cancel_handler(message, bot=bot):
    lang_code = get_user_language(message)
    handle_cancel(bot, message, lang_code)


@bot.message_handler(regexp="(ساخت برنامه تمرینی|Create workout plan)")
def create_handler(message, bot=bot):
    lang_code = get_user_language(message)
    handle_create(bot, message, lang_code)


@bot.message_handler(regexp="(تغییر زبان 🌐|Change language 🌐)")
def change_lang_handler(message, bot=bot):
    lang_code = get_user_language(message)
    handle_change_lang(bot, message, lang_code)


def get_user_language(message):
    con = sqlite3.connect("sqlite3.db")
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM user WHERE {message.from_user.id}")
    user = res.fetchall()[0]
    lang_code = user[1]
    return lang_code

if __name__ == "__main__":
    bot.polling()
