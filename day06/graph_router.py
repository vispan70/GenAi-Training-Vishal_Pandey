from typing import TypedDict

from langgraph.graph import StateGraph, START, END

# ============================================================
# IMPORT DAY-6 CLASSIFIER
# ============================================================

from intent_classifier import classify


# ============================================================
# IMPORT DAY-6 ROUTER HELPERS
# ============================================================

from router_helpers import (
    answer_faq,
    call_mock_api,
    escalate,
    small_talk_reply,
)


# ============================================================
# STATE
# ============================================================

class RouterState(TypedDict):
    user_input: str
    intent: str
    confidence: float
    response: str
    handover: dict | None


# ============================================================
# NODE 1: CLASSIFY
# ============================================================

def classify_node(state: RouterState) -> RouterState:

    result = classify(state["user_input"])

    state["intent"] = result.get(
        "intent",
        "out_of_scope"
    )

    state["confidence"] = result.get(
        "confidence",
        0.0
    )

    return state


# ============================================================
# NODE 2: MOCK API
# ============================================================

def mock_api_node(state: RouterState) -> RouterState:

    result = call_mock_api(
        state["intent"],
        {}
    )

    state["response"] = str(result)

    return state


# ============================================================
# NODE 3: FAQ
# ============================================================

def faq_node(state: RouterState) -> RouterState:

    faq_answer = answer_faq(
        state["user_input"]
    )

    if faq_answer:

        state["response"] = faq_answer

    else:

        # No FAQ match.
        # The graph will route this to escalation.
        state["response"] = ""

    return state


# ============================================================
# NODE 4: SMALL TALK
# ============================================================

def small_talk_node(state: RouterState) -> RouterState:

    result = small_talk_reply()

    state["response"] = result["message"]

    return state


# ============================================================
# NODE 5: ESCALATION
# ============================================================

def escalate_node(state: RouterState) -> RouterState:

    result = {
        "intent": state["intent"],
        "confidence": state["confidence"],
        "entities": {}
    }

    handover = escalate(
        state["user_input"],
        result
    )

    state["handover"] = handover

    state["response"] = (
        "Your request has been handed over "
        "to a customer-service representative."
    )

    return state


# ============================================================
# ROUTING AFTER CLASSIFICATION
# ============================================================

def route_after_classify(state: RouterState) -> str:

    intent = state["intent"]
    confidence = state["confidence"]

    # --------------------------------------------------------
    # Rule 1: Low confidence always escalates
    # --------------------------------------------------------

    if confidence < 0.6:
        return "escalate"

    # --------------------------------------------------------
    # Rule 2: Out of scope → escalate
    # --------------------------------------------------------

    if intent == "out_of_scope":
        return "escalate"

    # --------------------------------------------------------
    # Rule 3: Small talk → direct reply
    # --------------------------------------------------------

    if intent == "small_talk":
        return "small_talk"

    # --------------------------------------------------------
    # Rule 4: Banking actions → mock API
    # --------------------------------------------------------

    if intent in {
        "balance_enquiry",
        "card_hotlist",
        "statement_request"
    }:
        return "mock_api"

    # --------------------------------------------------------
    # Rule 5: UPI → FAQ
    # --------------------------------------------------------

    if intent == "upi_issue":
        return "faq"

    # --------------------------------------------------------
    # Safety fallback
    # --------------------------------------------------------

    return "escalate"


# ============================================================
# FAQ ROUTING
# ============================================================

def route_after_faq(state: RouterState) -> str:

    # If FAQ produced an answer
    if state["response"]:
        return "end"

    # If FAQ could not resolve the issue
    return "escalate"


# ============================================================
# BUILD GRAPH
# ============================================================

builder = StateGraph(RouterState)


# ------------------------------------------------------------
# Add nodes
# ------------------------------------------------------------

builder.add_node(
    "classify",
    classify_node
)

builder.add_node(
    "mock_api",
    mock_api_node
)

builder.add_node(
    "faq",
    faq_node
)

builder.add_node(
    "small_talk",
    small_talk_node
)

builder.add_node(
    "escalate",
    escalate_node
)


# ------------------------------------------------------------
# START → CLASSIFY
# ------------------------------------------------------------

builder.add_edge(
    START,
    "classify"
)


# ------------------------------------------------------------
# CLASSIFY → CONDITIONAL ROUTING
# ------------------------------------------------------------

builder.add_conditional_edges(
    "classify",
    route_after_classify,
    {
        "mock_api": "mock_api",
        "faq": "faq",
        "small_talk": "small_talk",
        "escalate": "escalate",
    }
)


# ------------------------------------------------------------
# FAQ → CONDITIONAL ROUTING
# ------------------------------------------------------------

builder.add_conditional_edges(
    "faq",
    route_after_faq,
    {
        "end": END,
        "escalate": "escalate",
    }
)


# ------------------------------------------------------------
# OTHER HANDLERS → END
# ------------------------------------------------------------

builder.add_edge(
    "mock_api",
    END
)

builder.add_edge(
    "small_talk",
    END
)

builder.add_edge(
    "escalate",
    END
)


# ============================================================
# COMPILE
# ============================================================

app = builder.compile()


# ============================================================
# GRAPH VISUALIZATION
# ============================================================

print("\n================ GRAPH ================\n")

print(
    app.get_graph().draw_mermaid()
)

print("\n========================================\n")


# ============================================================
# REPL
# ============================================================

if __name__ == "__main__":

    print("Graph Router")
    print("Type 'exit' to stop.\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() in {
            "exit",
            "quit"
        }:

            print("Bot: Goodbye!")
            break

        # ----------------------------------------------------
        # Initial state
        # ----------------------------------------------------

        initial_state = {
            "user_input": user_input,
            "intent": "",
            "confidence": 0.0,
            "response": "",
            "handover": None,
        }

        # ----------------------------------------------------
        # Run graph
        # ----------------------------------------------------

        result = app.invoke(
            initial_state
        )

        # ----------------------------------------------------
        # Print result
        # ----------------------------------------------------

        print("\n--------------------------------")
        print("Intent:", result["intent"])
        print("Confidence:", result["confidence"])
        print("Response:", result["response"])
        print("Handover:", result["handover"])
        print("--------------------------------\n")
