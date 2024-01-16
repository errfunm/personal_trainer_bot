from telebot import types
import sqlite3


def handle_start(bot, message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton("Create plan")
    itembtn2 = types.KeyboardButton("Change language🌐")
    markup.add(itembtn1)
    markup.add(itembtn2)
    bot.send_message(message.chat.id, "Choose one option:", reply_markup=markup)


def handle_cancel(bot, message):
    bot.send_message(message.chat.id, "Cancel command called.")
    handle_start(bot, message)


def handle_change_lang(bot, message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton("English")
    itembtn2 = types.KeyboardButton("فارسی")
    markup.add(itembtn1)
    markup.add(itembtn2)
    bot.send_message(message.chat.id, "Choose bot's language:", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id, set_lang, bot)


def set_lang(message, bot):
    lang_code = str()

    if message.text == "English":
        lang_code = "en"

    elif message.text == "فارسی":
        lang_code = "fa"

    # updating user settings proccess
    con = sqlite3.connect("sqlite3.db")
    cur = con.cursor()
    # command that will be executed in the database to update record
    sql_command = f"""
        UPDATE user
        SET lang_code = "{lang_code}"
        WHERE user_id = {message.from_user.id};"""

    cur.execute(sql_command)
    con.commit()
    con.close()

    bot.send_message(message.chat.id, "language changed")
    handle_start(bot, message)
