import os
import json
import requests
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")


# ============================================================
# OPENROUTER API DETAILS
# ============================================================

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}


# ============================================================
# ALLOWED INTENTS
# ============================================================

ALLOWED = [
    "balance_enquiry",
    "card_hotlist",
    "statement_request",
    "upi_issue",
    "small_talk",
    "out_of_scope"
]


# ============================================================
# CLASSIFIER SYSTEM PROMPT
# ============================================================

SYSTEM = """You are an intent classifier for a bank's customer-service bot.

Respond ONLY with valid JSON, no other text:

{
    "intent": "<one of the allowed intents>",
    "entities": {
        "card_last4": "...",
        "account_ref": "...",
        "period": "..."
    },
    "confidence": <number between 0 and 1>
}

Allowed intents:
balance_enquiry,
card_hotlist,
statement_request,
upi_issue,
small_talk,
out_of_scope.

Anything about investments, other customers, or unrelated topics is out_of_scope.

Include only the entities actually present in the message.
"""


# ============================================================
# CLASSIFIER
# ============================================================

def classify(utterance: str) -> dict:

    # Try at most 2 times
    for attempt in range(2):

        try:

            response = requests.post(
                url=url,
                headers=headers,
                json={
                    "model": MODEL,
                    "max_tokens": 500,
                    "messages": [
                        {
                            "role": "system",
                            "content": SYSTEM
                        },
                        {
                            "role": "user",
                            "content": utterance
                        }
                    ]
                },
                timeout=30
            )

            response.raise_for_status()

            response_data = response.json()

            raw = response_data["choices"][0]["message"]["content"]

            print("\nRaw model response:")
            print(raw)

            result = json.loads(raw)

            # =================================================
            # VALIDATE INTENT
            # =================================================

            if result.get("intent") not in ALLOWED:
                result["intent"] = "out_of_scope"

            # =================================================
            # VALIDATE CONFIDENCE
            # =================================================

            confidence = result.get("confidence", 0.0)

            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                confidence = 0.0

            confidence = max(0.0, min(1.0, confidence))

            result["confidence"] = confidence

            # =================================================
            # VALIDATE ENTITIES
            # =================================================

            if not isinstance(result.get("entities"), dict):
                result["entities"] = {}

            return result

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
            requests.RequestException
        ) as error:

            print(f"Attempt {attempt + 1} failed: {error}")

            if attempt == 0:
                print("Retrying...")
                continue

            # Safe fallback
            return {
                "intent": "out_of_scope",
                "entities": {},
                "confidence": 0.0
            }
