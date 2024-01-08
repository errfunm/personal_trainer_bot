from telebot import types

def handle_start(bot, message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('Create plan')
    markup.add(itembtn1)
    bot.send_message(message.chat.id, "Choose one option:", reply_markup=markup)