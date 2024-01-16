from openai import OpenAI
from handler_general import handle_cancel
from telebot import types
import sqlite3

QUESTIONS = {
    "en": [
        "Hi, \nas a personal trainer I have several questions to ask you.\nWhat is Your goal?",
        "What is your fitness level?",
        "How many times per week can you work out?",
        "Do you have any equipment available?",
        "Do you have any limitations or injuries?",
        "Any further description?",
    ],
    "fa": [
        "سلامِ، به عنوان مربی شخصی\n به این سوالات پاسخ دهید.\nهدف تان چیست؟",
        "از لحاظ تناسب اندام در چه سطحی هستید؟",
        "چند بار در هفته میتوانید برای تمرین کردن اختصاص دهید؟",
        "آیا تجهیزات ورزشی دارید؟",
        "آیا از هرگونه محدودیت یا مصدومیت برخوردار هستید؟",
        "آیا توضیحات اضافی دارید؟",
    ],
}

# Reply keyboard markup options
default_options = {
    0: ["Gain muscle", "loose weight"],
    1: ["Beginner(0-1 year)", "Intermediate(1-3 year)", "Pro(more than 3 years)"],
    2: ["1", "2", "3", "4", "5"],
    3: ["No", "Yes"],
    4: ["No", "Yes"],
}


user_answers_dict = {}
answers_list = []


def handle_create(bot, message):
    user_id = message.from_user.id
    user_answers_dict[user_id] = []
    ask_question(bot, message, 0)


def ask_question(bot, message, question_index):
    # fetch database
    con = sqlite3.connect("sqlite3.db")
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM user WHERE {message.from_user.id}")
    user = res.fetchall()[0]
    lang_code = user[1]

    chat_id = message.chat.id
    questions = []
    if lang_code == "fa":
        questions = QUESTIONS["fa"]
    else:
        questions = QUESTIONS["en"]

    if question_index < len(questions):
        try:
            default_options[question_index]
            markup = types.ReplyKeyboardMarkup(row_width=1)
            for i in default_options[question_index]:
                itembtn = types.KeyboardButton(i)
                markup.add(itembtn)
            bot.send_message(chat_id, questions[question_index], reply_markup=markup)
            bot.register_next_step_handler_by_chat_id(chat_id, save_answer, bot)

        except KeyError:
            # Hide reply keyboard when there is no need
            bot.send_message(
                chat_id,
                questions[question_index],
                reply_markup=types.ReplyKeyboardRemove(),
            )
            bot.register_next_step_handler_by_chat_id(chat_id, save_answer, bot)

    else:
        user_id = chat_id
        answers_list = user_answers_dict.get(user_id, [])

        user_answers = ", ".join(answers_list)
        bot.send_message(
            chat_id,
            f"Thank you for answering the questions! Your answers are: {user_answers}",
        )
        conversation = prepare_initial_conversation(answers_list, lang_code)
        # openai generated plan
        plan = generate_workout_plan(conversation)
        bot.send_message(chat_id, plan)


def save_answer(message, bot):
    user_id = message.from_user.id
    answer = message.text
    # handle cancel command
    if answer == "/cancel":
        handle_cancel(bot, message)
    else:
        user_answers_dict[user_id].append(answer)
        next_question_index = len(user_answers_dict[user_id])
        ask_question(bot, message, next_question_index)


# creates the initial conversation for AI to continue
def prepare_initial_conversation(answers, lang):
    conversation = []
    for i in range(len(QUESTIONS[lang])):
        ASSIS_ROLE = {"role": "assistant", "content": QUESTIONS[lang][i]}
        USER_ROLE = {"role": "user", "content": answers[i]}
        conversation.append(ASSIS_ROLE)
        conversation.append(USER_ROLE)
    # add predefined messages to the end of conversation
    final_messages = [
        {
            "role": "assistant",
            "content": "Wait a moment and your personalized plan will be ready.",
        },
        {"role": "user", "content": "Thanks."},
    ]
    for i in final_messages:
        conversation.append(i)

    return conversation


def generate_workout_plan(conversation):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        temperature=1,
        max_tokens=450,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return response.choices[0].message.content
