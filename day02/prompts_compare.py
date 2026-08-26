
import os
import requests
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("OPENROUTER_API_KEY")
cla


# Read complaint from file
with open("complaint.txt", "r", encoding="utf-8") as f:
    complaint = f.read()


# OpenRouter API details
MODEL = os.getenv("MODEL")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}


# Prompt A - Simple Prompt


promptA = f"""
Summarize this email:

{complaint}
"""


responseA = requests.post(
    url=url,
    headers=headers,
    json={
        "model": MODEL,
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": promptA
            }
        ]
    }
)


# Convert response to JSON
dataA = responseA.json()
print(dataA)


# Get AI response
resultA = dataA["choices"][0]["message"]["content"]


# Prompt B - Good / Structured Prompt


promptB = f"""
You are a complaints triage assistant for a bank.

Analyze the following customer complaint.

Return the result using exactly these three fields:

issue:
severity:
requested_action:

Severity must be exactly one of:
- low
- medium
- high

Rules:
1. Use only information provided in the email.
2. Do not invent or assume any details.
3. Keep each field concise.
4. If the requested action is not explicitly mentioned, write "Not Mentioned".
5. Return only the three fields. Do not add explanations, summaries, or extra fields.

Customer complaint:

{complaint}
"""

# paid chatgpt model = "~openai/gpt-latest"

responseB = requests.post(
    url=url,
    headers=headers,
    json={
        "model": MODEL,
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": promptB
            }
        ]
    }
)


# Convert response to JSON
dataB = responseB.json()


# Get AI response
resultB = dataB["choices"][0]["message"]["content"]


# Print Prompt A result

print("=" * 50)
print("PROMPT A - SIMPLE PROMPT")
print("=" * 50)


print(resultA)


# Print Prompt B result


print("\n" + "=" * 50)
print("PROMPT B - STRUCTURED PROMPT")
print("=" * 50)

print(resultB)
