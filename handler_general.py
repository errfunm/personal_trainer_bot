from telebot import types
import sqlite3

language_options = {
    "en": {
        "reply_keyboard_options": {
            "start": ["Create workout plan", "Change language 🌐"]
        },
        "prompts": {
            "start": "Choose one of the options:",
            "handle_change_lang": "Choose bot's lang:",
            "set_lang": "language changed",
            "cancel": "canceled",
        }
    },

    "fa": {
        "reply_keyboard_options": {
            "start": ["ساخت برنامه تمرینی", "تغییر زبان 🌐"]
        },
        "prompts": {
            "start": "یکی از گزینه ها را انتخاب کنید:",
            "handle_change_lang": "زبان بات را انتخاب  کنید:",
            "set_lang": "زبان تغییر یافت.",
            "cancel": "متوقف شد."
        }
    }
}


def handle_start(bot, message, lang_code):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    for i in language_options[lang_code]["reply_keyboard_options"]["start"]:
        btn = types.KeyboardButton(i)
        markup.add(btn)
    bot.send_message(message.chat.id, language_options[lang_code]["prompts"]["start"], reply_markup=markup)


def handle_cancel(bot, message, lang_code):
    prompt_message = language_options[lang_code]["prompts"]["cancel"]
    bot.send_message(message.chat.id, prompt_message)
    handle_start(bot, message, lang_code)


def handle_change_lang(bot, message, lang_code):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton("English")
    itembtn2 = types.KeyboardButton("فارسی")
    markup.add(itembtn1, itembtn2)
    prompt_message = language_options[lang_code]["prompts"]["handle_change_lang"]
    bot.send_message(message.chat.id, prompt_message, reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(message.chat.id, set_lang, bot)


def set_lang(message, bot):
    lang_code = str()

    if message.text == "English":
        lang_code = "en"

    elif message.text == "فارسی":
        lang_code = "fa"

    # updating user settings process
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

    prompt_message = language_options[lang_code]["prompts"]["set_lang"]
    bot.send_message(message.chat.id, prompt_message)
    handle_start(bot, message, lang_code)
