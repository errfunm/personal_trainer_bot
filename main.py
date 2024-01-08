import os
from dotenv import load_dotenv
from telebot import TeleBot
from handler_general import handle_start
from handler_workout_plan import handle_create

# Initialize the bot with your token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_handler(message, bot=bot):
    handle_start(bot, message)

@bot.message_handler(regexp='Create plan')
def create_handler(message, bot=bot):
    handle_create(bot, message)

if __name__ == "__main__":
    bot.polling()
