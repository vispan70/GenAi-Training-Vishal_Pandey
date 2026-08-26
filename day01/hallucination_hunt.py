import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")
base_url = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")

if not api_key or not MODEL:
    raise ValueError(
        "OPENROUTER_API_KEY and MODEL must be set in .env"
    )


client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

questions = [
    "What is the capital of Maharashtra?",
    "Who wrote the Ramayana?",
    "What are the annual charges of the Platinum Sapphire Credit Card from SuryaFirst Bank?",
    "What are the current RBI repo rate and today's date?",
    "What is the customer-care number of SuryaFirst Bank?",
]


# without system message

# for question in questions:
#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {
#                 "role": "user",
#                 "content": question,
#             }
#         ],
#     )

#     answer = response.choices[0].message.content

#     print("\n" + "=" * 70)
#     print("Question:", question)
#     print("Answer:", answer)


SYSTEM_PROMPT = """
If you are not certain or the information may be out of date,
say "I don't know" instead of guessing.
"""

# with system message

for question in questions:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    answer = response.choices[0].message.content

    print("\n" + "=" * 70)
    print("Question:", question)
    print("Answer:", answer)
