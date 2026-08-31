# ============================================================
# DAY 3 ROUTER HELPERS
# ============================================================


# ============================================================
# FAQ
# ============================================================

FAQ = {
    "upi_failed": "Please check your UPI PIN and try again.",
    "upi_pending": "A pending UPI transaction may take some time to complete.",
    "upi_not_working": "Please check your internet connection and try again.",
    "upi_limit": "Your UPI transaction may have exceeded the daily limit."
}


# ============================================================
# FAQ HANDLER
# ============================================================

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


# ============================================================
# MOCK API
# ============================================================

def call_mock_api(intent, entities):
    """
    Simulates a backend API call.
    No real network request is made.
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


# ============================================================
# ESCALATION
# ============================================================

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


# ============================================================
# SMALL TALK
# ============================================================

def small_talk_reply():
    """
    Direct reply for small-talk requests.
    """

    return {
        "type": "direct_reply",
        "message": "Hello! How can I help you with your banking request?"
    }
