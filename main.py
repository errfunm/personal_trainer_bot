import os
from dotenv import load_dotenv
import telebot
import generate

# Initialize the bot with your token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Number of questions you want to ask
QUESTIONS = [
    "What is Your goal?",
    "What is your fitness level?",
    "How many times per week can you work out?",
    "Do you have any equipment available?",
    "Do you have any limitations or injuries?",
    "Any further description?"
]
num_questions = len(QUESTIONS)

# answers for each user
answers = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    answers[user_id] = []
    bot.send_message(message.chat.id, "Hi, \nas a personal trainer I have several questions to ask you.")
    ask_question(message.chat.id, 0)

def ask_question(chat_id, question_index):
    if question_index < num_questions:
        bot.send_message(chat_id, QUESTIONS[question_index])
        bot.register_next_step_handler_by_chat_id(chat_id, save_answer)
    else:
        user_id = chat_id
        answers_list = answers.get(user_id, [])
        saved_answers = ', '.join(answers_list)
        bot.send_message(chat_id, f"Thank you for answering the questions! Your answers are: {saved_answers}")
        # openai generated plan
        plan = generate.workout_plan(answers_list)
        bot.send_message(chat_id, plan)

def save_answer(message):
    user_id = message.from_user.id
    answer = message.text
    answers[user_id].append(answer)
    question_index = len(answers[user_id]) - 1
    ask_question(message.chat.id, question_index + 1)

if __name__ == "__main__":
    bot.polling()
