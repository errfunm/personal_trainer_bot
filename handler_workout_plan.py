from openai import OpenAI

QUESTIONS = [
"What is Your goal?",
"What is your fitness level?",
"How many times per week can you work out?",
"Do you have any equipment available?",
"Do you have any limitations or injuries?",
"Any further description?"
]
USER_ROLE = {
    "role": "user",
    "content": ""
}
ASSIS_ROLE = {
    "role": "assistant", 
    "content": ""
}

user_answers_dict = {} 
answers_list = [] 


def handle_create(bot, message):
    user_id = message.from_user.id
    user_answers_dict[user_id] = []
    bot.send_message(message.chat.id, "Hi, \nas a personal trainer I have several questions to ask you.")
    ask_question(bot, message.chat.id, 0)

def ask_question(bot, chat_id, question_index):
    if question_index < len(QUESTIONS):
        bot.send_message(chat_id, QUESTIONS[question_index])
        bot.register_next_step_handler_by_chat_id(chat_id, save_answer, bot)
    else:
        user_id = chat_id
        answers_list = user_answers_dict.get(user_id, [])

        saved_answers = ', '.join(answers_list)
        bot.send_message(chat_id, f"Thank you for answering the questions! Your answers are: {saved_answers}")
        # openai generated plan
        plan = generate_workout_plan(answers_list)
        bot.send_message(chat_id, plan)

def save_answer(message, bot):
    user_id = message.from_user.id
    answer = message.text
    user_answers_dict[user_id].append(answer)
    next_question_index = len(user_answers_dict[user_id]) 
    ask_question(bot, message.chat.id, next_question_index)

def generate_workout_plan(answers_list):
    conversation = []
    for i in range(len(QUESTIONS)):
        assis_msg = ASSIS_ROLE["content"] = QUESTIONS[i]
        user_msg = USER_ROLE["content"] = f"{answers_list[i]}"
        conversation.extend([assis_msg, user_msg])

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        conversation=conversation,
        temperature=1,
        max_tokens=450,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content