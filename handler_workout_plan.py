from openai import OpenAI
from handler_general import handle_cancel
from telebot import types


language_options = {
    "en": {
        "prompts": {
            "create": "Hi, \nas a personal trainer I have several questions to ask you.\nIf your answer is not among"
                      " those we have prepared for you, you can type."
        },
        "reply_keyboard_options": {
            0: ["Muscle gain", "Fat loss", "Overall fitness", "Endurance", "Flexibility"],
            1: ["Beginner", "Intermediate", "Advanced"],
            2: ["1-2 times", "3-4 times", "5 or more times"],
            3: ["Gym equipment", "Dumbbells", "Resistance bands", "No equipment"],
        },
        "questions": [
            "What is Your goal?",
            "What is your fitness level?",
            "How many times per week can you work out?",
            "Do you have any equipment available?",
            "Do you have any limitations or injuries?(explain)",
            "Any further description?",
        ]
    },
    "fa": {
        "prompts": {
            "create": "سلام،\nبه عنوان یک مربی شخصی چند سوال هست که باید از شما بپرسم.\nاگر "
                      "جواب شما در بین آنهایی که ما برای شما آماده کرده‌ایم نبود، میتوانید تایپ کنید."
        },
        "reply_keyboard_options": {
            0: ["افزایش عضله", "کاهش چربی", "تناسب اندام کلی", "استقامت", "انعطاف‌پذیری"],
            1: ["مبتدی", "متوسط", "پیشرفته"],
            2: ["1-2 بار", "3-4 بار", "5 یا بیشتر"],
            3: ["تجهیزات باشگاه", "دمبل", "باندهای مقاومتی", "بدون تجهیزات"],
        },
        "questions": [
            "هدفتان چیست؟",
            "از لحاظ تناسب اندام در چه سطحی هستید؟",
            "چند بار در هفته میتوانید برای تمرین کردن اختصاص دهید؟",
            "آیا تجهیزات ورزشی دارید؟",
            "آیا از هرگونه محدودیت یا مصدومیت برخوردار هستید؟(توضیح دهید)",
            "آیا توضیحات اضافی دارید؟",
        ]
    }
}


user_answers_dict = {}
answers_list = []


def handle_create(bot, message, lang_code):
    user_id = message.from_user.id
    user_answers_dict[user_id] = []
    bot.send_message(message.chat.id, language_options[lang_code]["prompts"]["create"])
    ask_question(bot, message, 0, lang_code)


def ask_question(bot, message, question_index, lang_code):

    chat_id = message.chat.id
    questions = language_options[lang_code]["questions"]

    if question_index < len(questions):
        try:
            markup = types.ReplyKeyboardMarkup(row_width=1)
            for i in language_options[lang_code]["reply_keyboard_options"][question_index]:
                btn = types.KeyboardButton(i)
                markup.add(btn)

        except KeyError:
            # Hide reply keyboard when there is no need
            markup = types.ReplyKeyboardRemove()

        bot.send_message(
            chat_id,
            questions[question_index],
            reply_markup=markup,
        )    
        bot.register_next_step_handler_by_chat_id(chat_id, save_answer, bot, lang_code)

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


def save_answer(message, bot, lang_code):
    user_id = message.from_user.id
    answer = message.text
    # handle cancel command
    if answer == "/cancel":
        handle_cancel(bot, message, lang_code)
    else:
        user_answers_dict[user_id].append(answer)
        next_question_index = len(user_answers_dict[user_id])
        ask_question(bot, message, next_question_index, lang_code)


# creates the initial conversation for AI to continue
def prepare_initial_conversation(answers, lang):
    conversation = []
    for i in range(len(language_options[lang]["questions"])):
        ASSIS_ROLE = {"role": "assistant", "content": language_options[lang]["questions"][i]}
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
