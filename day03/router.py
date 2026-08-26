import os
import json
import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL")


# --------------------------------------------------
# OpenRouter API details
# --------------------------------------------------

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}


# --------------------------------------------------
# Allowed intents
# --------------------------------------------------

ALLOWED = [
    "balance_enquiry",
    "card_hotlist",
    "statement_request",
    "upi_issue",
    "small_talk",
    "out_of_scope"
]


# --------------------------------------------------
# Classifier system prompt
# --------------------------------------------------

SYSTEM = """You are an intent classifier for a bank's customer-service bot.

Respond ONLY with valid JSON, no other text:

{
    "intent": "<one of the allowed intents>",
    "entities": {},
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


# --------------------------------------------------
# Hardcoded FAQ
# --------------------------------------------------

FAQ = {
    "upi_failed": "Please check your UPI PIN and try again.",
    "upi_pending": "A pending UPI transaction may take some time to complete.",
    "upi_not_working": "Please check your internet connection and try again.",
    "upi_limit": "Your UPI transaction may have exceeded the daily limit."
}


# ==================================================
# DAY 2 - CLASSIFIER
# ==================================================

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

            # ------------------------------------------
            # Validate intent
            # ------------------------------------------

            if result.get("intent") not in ALLOWED:
                result["intent"] = "out_of_scope"

            # ------------------------------------------
            # Validate confidence
            # ------------------------------------------

            confidence = result.get("confidence", 0.0)

            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                confidence = 0.0

            confidence = max(0.0, min(1.0, confidence))

            result["confidence"] = confidence

            # ------------------------------------------
            # Validate entities
            # ------------------------------------------

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


# ==================================================
# DAY 3 - HANDLER 1: FAQ
# ==================================================

def answer_faq(utterance):
    """
    Search the hardcoded FAQ for a matching UPI issue.
    """

    text = utterance.lower()

    # UPI failed
    if "failed" in text or "failure" in text:
        return FAQ["upi_failed"]

    # UPI pending
    if "pending" in text or "stuck" in text:
        return FAQ["upi_pending"]

    # UPI not working
    if "not working" in text or "doesn't work" in text:
        return FAQ["upi_not_working"]

    # UPI limit
    if "limit" in text:
        return FAQ["upi_limit"]

    # Nothing matched
    return None


# ==================================================
# DAY 3 - HANDLER 2: MOCK API
# ==================================================

def call_mock_api(intent, entities):
    """
    Simulates a backend API call.
    No real network request is made here.
    """

    if intent == "balance_enquiry":

        return {
            "status": "ok",
            "action": "balance_checked",
            "balance": "₹25,430.50"
        }

    elif intent == "card_hotlist":

        return {
            "status": "ok",
            "action": "card_hotlisted",
            "ref": "HTL-1029"
        }

    elif intent == "statement_request":

        return {
            "status": "ok",
            "action": "statement_requested",
            "ref": "STM-2048"
        }

    # Safety fallback
    return {
        "status": "error",
        "action": "unknown_action"
    }


# ==================================================
# DAY 3 - HANDLER 3: ESCALATION
# ==================================================

def escalate(utterance, result):
    """
    Creates a structured handover for a human agent.
    """

    confidence = result.get("confidence", 0.0)
    intent = result.get("intent", "unknown")
    entities = result.get("entities", {})

    if confidence < 0.6:
        reason = "Low classifier confidence"
    elif intent == "out_of_scope":
        reason = "Request is out of scope"
    else:
        reason = "Unable to resolve automatically"

    return {
        "reason": reason,
        "intent": intent,
        "entities": entities,
        "summary_for_agent": utterance
    }


# ==================================================
# DAY 3 - MAIN ROUTER
# ==================================================

def route(utterance):

    # ----------------------------------------------
    # Step 1: Classify
    # ----------------------------------------------

    result = classify(utterance)

    intent = result.get("intent")
    confidence = result.get("confidence", 0.0)
    entities = result.get("entities", {})

    print("\nClassifier result:")
    print(result)

    # ----------------------------------------------
    # Step 2: Low confidence → Escalate
    # ----------------------------------------------

    if confidence < 0.6:
        return escalate(utterance, result)

    # ----------------------------------------------
    # Step 3: Out of scope → Escalate
    # ----------------------------------------------

    if intent == "out_of_scope":
        return escalate(utterance, result)

    # ----------------------------------------------
    # Step 4: Small talk → Direct reply
    # ----------------------------------------------

    if intent == "small_talk":

        return {
            "type": "direct_reply",
            "message": "Hello! How can I help you with your banking request?"
        }

    # ----------------------------------------------
    # Step 5: Banking actions → Mock API
    # ----------------------------------------------

    if intent in {
        "balance_enquiry",
        "card_hotlist",
        "statement_request"
    }:

        return call_mock_api(intent, entities)

    # ----------------------------------------------
    # Step 6: UPI issue → FAQ first
    # ----------------------------------------------

    if intent == "upi_issue":

        faq_answer = answer_faq(utterance)

        # FAQ found
        if faq_answer:

            return {
                "type": "faq_answer",
                "message": faq_answer
            }

        # FAQ not found → escalate
        return escalate(utterance, result)

    # ----------------------------------------------
    # Safety fallback
    # ----------------------------------------------

    return escalate(utterance, result)


# ==================================================
# DAY 3 - REPL
# ==================================================

if __name__ == "__main__":

    while True:

        user = input("\nYou: ")

        if user.lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break

        result = route(user)

        print("Bot:", result)
