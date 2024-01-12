from openai import OpenAI
from handler_general import handle_cancel

QUESTIONS = [
    "Hi, \nas a personal trainer I have several questions to ask you.\nWhat is Your goal?",
    "What is your fitness level?",
    "How many times per week can you work out?",
    "Do you have any equipment available?",
    "Do you have any limitations or injuries?",
    "Any further description?",
]

user_answers_dict = {}
answers_list = []


def handle_create(bot, message):
    user_id = message.from_user.id
    user_answers_dict[user_id] = []
    ask_question(bot, message.chat.id, 0)


def ask_question(bot, chat_id, question_index):
    if question_index < len(QUESTIONS):
        bot.send_message(chat_id, QUESTIONS[question_index])
        bot.register_next_step_handler_by_chat_id(chat_id, save_answer, bot)
    else:
        user_id = chat_id
        answers_list = user_answers_dict.get(user_id, [])

        user_answers = ", ".join(answers_list)
        bot.send_message(
            chat_id,
            f"Thank you for answering the questions! Your answers are: {user_answers}",
        )
        conversation = prepare_initial_conversation(answers_list)
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
        ask_question(bot, message.chat.id, next_question_index)


# creates the initial conversation for AI to continue
def prepare_initial_conversation(answers):
    conversation = []
    for i in range(len(QUESTIONS)):
        ASSIS_ROLE = {"role": "assistant", "content": QUESTIONS[i]}
        USER_ROLE = {"role": "user", "content": answers[i]}
        conversation.append(ASSIS_ROLE)
        conversation.append(USER_ROLE)
    # predefined messages for the end of conversation
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
