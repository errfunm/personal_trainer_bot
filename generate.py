from openai import OpenAI

def workout_plan(answers):
    messages=[
        {
        "role": "assistant",
        "content": "Hi, \nas a personal trainer I have several questions to ask you.\nWhat is Your goal?\n"
        },
        {
        "role": "user",
        "content": f"{answers[0]}"
        },

        {
        "role": "assistant",
        "content": "What is your fitness level?"
        },
        {
        "role": "user",
        "content": f"{answers[1]}"
        },

        {
        "role": "assistant",
        "content": "How many times per week can you work out?"
        },
        {
        "role": "user",
        "content": f"{answers[2]}"
        },

        {
        "role": "assistant",
        "content": "Do you have any equipment available?"
        },
        {
        "role": "user",
        "content": f"{answers[3]}"
        },

        {
        "role": "assistant",
        "content": "Do you have any limitations or injuries?"
        },
        {
        "role": "user",
        "content": f"{answers[4]}"
        },

        {
        "role": "assistant",
        "content": "Any further description?"
        },
        {
        "role": "user",
        "content": f"{answers[5]}"
        },

        {
        "role": "assistant",
        "content": "Ok, fine. wait a moment to build your personalized workout plan."
        },
        {
        "role": "user",
        "content": "Thanks."
        }
    ]

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1,
        max_tokens=450,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content