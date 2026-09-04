# ============================================================
# CAPSTONE BANKING ASSISTANT
# graph/bot.py
# ============================================================


# ============================================================
# 1. IMPORTS
# ============================================================

from tools.banking_tools import (
    get_balance,
    hotlist_card,
    get_statement
)
import os
import sys
import json
import re
import requests

from pathlib import Path
from typing import TypedDict, List, Dict

from dotenv import load_dotenv

from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma

from langgraph.graph import StateGraph, START, END


# ============================================================
# 2. PATH SETUP
# ============================================================

# Current file:
# task-7.2/graph/bot.py

GRAPH_DIR = Path(__file__).resolve().parent

# task-7.2 folder
TASK_DIR = GRAPH_DIR.parent

# day07 folder
DAY07_DIR = TASK_DIR.parent

# repository root
ROOT_DIR = DAY07_DIR.parent


# Add task-7.2 folder to Python path
if str(TASK_DIR) not in sys.path:
    sys.path.insert(0, str(TASK_DIR))


# ============================================================
# 3. IMPORT LOCAL BANKING TOOLS
# ============================================================


# ============================================================
# 4. LOAD ENVIRONMENT VARIABLES
# ============================================================

ENV_PATH = ROOT_DIR / ".env"

load_dotenv(ENV_PATH)

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError(
        f"OPENROUTER_API_KEY not found.\n"
        f"Expected .env file at: {ENV_PATH}"
    )


# ============================================================
# 5. PATHS
# ============================================================

CHROMA_DIR = TASK_DIR / "chroma_db"


# ============================================================
# 6. OPENROUTER CONFIGURATION
# ============================================================

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

CHAT_MODEL = "openai/gpt-4o-mini"


# ============================================================
# 7. LLM HELPER FUNCTION
# ============================================================

def call_llm(messages, temperature=0):

    response = requests.post(
        CHAT_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": CHAT_MODEL,
            "messages": messages,
            "temperature": temperature
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


# ============================================================
# 8. OPENROUTER EMBEDDINGS
# ============================================================

class OpenRouterEmbeddings(Embeddings):

    def __init__(self):

        self.api_key = API_KEY

        self.model = (
            "liquid/lfm-2.5-embedding-350m:free"
        )

        self.url = (
            "https://openrouter.ai/api/v1/embeddings"
        )

    def embed_documents(self, texts):

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "input": texts
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return [
            item["embedding"]
            for item in data["data"]
        ]

    def embed_query(self, text):

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "input": [text]
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["data"][0]["embedding"]


# ============================================================
# 9. CONNECT TO CHROMADB
# ============================================================

if not CHROMA_DIR.exists():

    raise FileNotFoundError(
        f"ChromaDB not found at:\n{CHROMA_DIR}\n\n"
        "Please run build_index.py first."
    )


embeddings = OpenRouterEmbeddings()


vector_db = Chroma(
    persist_directory=str(CHROMA_DIR),
    embedding_function=embeddings
)


# ============================================================
# 10. GRAPH STATE
# ============================================================

class BotState(TypedDict):

    user_input: str
    intent: str
    confidence: float
    response: str
    messages: List[Dict[str, str]]


# ============================================================
# 11. FORMAT CONVERSATION HISTORY
# ============================================================

def format_history(messages, limit=6):

    recent_messages = messages[-limit:]

    history = []

    for message in recent_messages:

        role = message.get("role", "user").upper()

        content = message.get("content", "")

        history.append(
            f"{role}: {content}"
        )

    return "\n".join(history)


# ============================================================
# 12. GET ACCOUNT ID FROM MEMORY
# ============================================================

def get_account_from_history(messages):

    for message in reversed(messages):

        content = message.get("content", "")

        match = re.search(
            r"\bACC\d+\b",
            content,
            re.IGNORECASE
        )

        if match:

            return match.group().upper()

    return None


# ============================================================
# 13. CLASSIFY NODE
# ============================================================

def classify_node(state):

    history = format_history(
        state["messages"]
    )

    prompt = f"""
You are an intent classifier for a banking chatbot.

Classify ONLY the current user message.

Possible intents:

- balance_enquiry
- card_hotlist
- statement_request
- upi_issue
- account_information
- kyc_information
- loan_information
- fd_information
- net_banking_information
- charges_information
- small_talk
- out_of_scope

Conversation history:
{history}

Current user message:
{state["user_input"]}

Return ONLY valid JSON in this format:

{{
    "intent": "intent_name",
    "confidence": 0.95
}}
"""

    try:

        result = call_llm([
            {
                "role": "user",
                "content": prompt
            }
        ])

        # Remove markdown code blocks if present
        result = result.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        data = json.loads(result)

        intent = data.get(
            "intent",
            "out_of_scope"
        )

        confidence = float(
            data.get(
                "confidence",
                0.0
            )
        )

    except Exception as error:

        print(
            f"\n[CLASSIFIER ERROR] {error}"
        )

        intent = "out_of_scope"
        confidence = 0.0

    print("\n" + "-" * 50)
    print("[CLASSIFIER NODE]")
    print(f"Intent: {intent}")
    print(f"Confidence: {confidence}")
    print("-" * 50)

    return {
        "intent": intent,
        "confidence": confidence
    }


# ============================================================
# 14. CONDITIONAL ROUTER
# ============================================================

def route_intent(state):

    confidence = state["confidence"]
    intent = state["intent"]

    # Low confidence -> escalate
    if confidence < 0.6:

        print(
            "\n[ROUTER] Low confidence -> ESCALATE"
        )

        return "escalate"

    # Transactional intents -> tools
    transactional_intents = [
        "balance_enquiry",
        "card_hotlist",
        "statement_request"
    ]

    if intent in transactional_intents:

        print(
            "\n[ROUTER] Transactional intent -> TOOLS"
        )

        return "tools"

    # Out of scope -> escalate
    if intent == "out_of_scope":

        print(
            "\n[ROUTER] Out of scope -> ESCALATE"
        )

        return "escalate"

    # Everything informational -> RAG
    print(
        "\n[ROUTER] Informational intent -> RAG"
    )

    return "rag"


# ============================================================
# 15. RAG NODE
# ============================================================

def rag_node(state):

    question = state["user_input"]

    history = format_history(
        state["messages"]
    )

    # --------------------------------------------------------
    # Generate Multiple Queries
    # --------------------------------------------------------

    query_prompt = f"""
You are helping retrieve information from a banking
knowledge base.

Generate exactly 3 different search queries related to
the user's current question.

Conversation history:
{history}

Current question:
{question}

Return ONLY the 3 search queries.
One query per line.
No numbering.
No explanation.
"""

    try:

        query_response = call_llm([
            {
                "role": "user",
                "content": query_prompt
            }
        ])

        queries = [
            query.strip()
            for query in query_response.split("\n")
            if query.strip()
        ]

    except Exception as error:

        print(
            f"[QUERY GENERATION ERROR] {error}"
        )

        queries = [question]

    # Add original question
    queries.append(question)

    print("\n[MULTI-QUERY RAG]")
    print("Generated Queries:")

    for index, query in enumerate(
        queries,
        start=1
    ):

        print(
            f"{index}. {query}"
        )

    # --------------------------------------------------------
    # Retrieve Documents
    # --------------------------------------------------------

    retrieved_docs = []

    for query in queries[:4]:

        docs = vector_db.similarity_search(
            query,
            k=3
        )

        retrieved_docs.extend(docs)

    # --------------------------------------------------------
    # Deduplicate Documents
    # --------------------------------------------------------

    unique_docs = []

    seen = set()

    for doc in retrieved_docs:

        if doc.page_content not in seen:

            seen.add(doc.page_content)

            unique_docs.append(doc)

    # --------------------------------------------------------
    # Build Context
    # --------------------------------------------------------

    context = "\n\n".join(
        doc.page_content
        for doc in unique_docs[:6]
    )

    # --------------------------------------------------------
    # Generate Final Answer
    # --------------------------------------------------------

    answer_prompt = f"""
You are a helpful banking assistant.

Answer the user's question using ONLY the knowledge
base context provided below.

If the answer is not available in the context, clearly
say that the information is not available in the
knowledge base.

Conversation history:
{history}

Knowledge Base Context:
{context}

Current Question:
{question}

Give a clear and concise answer.
"""

    try:

        answer = call_llm([
            {
                "role": "user",
                "content": answer_prompt
            }
        ])

    except Exception as error:

        answer = (
            "Sorry, I encountered an error while "
            "searching the knowledge base."
        )

        print(
            f"[RAG ERROR] {error}"
        )

    print(
        "\n[RAG NODE] Answer generated successfully."
    )

    return {
        "response": answer
    }


# ============================================================
# 16. TOOLS NODE
# ============================================================

def tools_node(state):

    user_input = state["user_input"]

    messages = state["messages"]

    intent = state["intent"]

    # --------------------------------------------------------
    # Find Account ID
    # --------------------------------------------------------

    account_id = None

    # First check current user message

    current_account = re.search(
        r"\bACC\d+\b",
        user_input,
        re.IGNORECASE
    )

    if current_account:

        account_id = current_account.group().upper()

    # Otherwise search conversation memory

    if not account_id:

        account_id = get_account_from_history(
            messages
        )

    # --------------------------------------------------------
    # BALANCE ENQUIRY
    # --------------------------------------------------------

    if intent == "balance_enquiry":

        if not account_id:

            return {
                "response": (
                    "Please provide your account ID "
                    "to check your balance."
                )
            }

        result = get_balance(account_id)

        if result["status"] == "success":

            response = (
                f"Your account balance for "
                f"{account_id} is "
                f"₹{result['balance']:,}."
            )

        else:

            response = result["message"]

        print(
            f"\n[TOOLS NODE]"
        )

        print(
            f"Calling: get_balance({account_id})"
        )

        return {
            "response": response
        }

    # --------------------------------------------------------
    # STATEMENT REQUEST
    # --------------------------------------------------------

    elif intent == "statement_request":

        if not account_id:

            return {
                "response": (
                    "Please provide your account ID "
                    "to get the statement."
                )
            }

        # Default period
        period = "recent transactions"

        # Try detecting a period
        months = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december"
        ]

        for month in months:

            if month in user_input.lower():

                period = month.capitalize()

                break

        result = get_statement(
            account_id,
            period
        )

        if result["status"] == "success":

            transactions = "\n".join(
                result["transactions"]
            )

            response = (
                f"Statement for {account_id} "
                f"({period}):\n\n"
                f"{transactions}"
            )

        else:

            response = result["message"]

        print(
            "\n[TOOLS NODE]"
        )

        print(
            f"Calling: get_statement({account_id}, {period})"
        )

        return {
            "response": response
        }

    # --------------------------------------------------------
    # CARD HOTLIST
    # --------------------------------------------------------

    elif intent == "card_hotlist":

        # Look for 4 digit card number

        match = re.search(
            r"\b\d{4}\b",
            user_input
        )

        if not match:

            return {
                "response": (
                    "Please provide the last 4 digits "
                    "of your card."
                )
            }

        card_last4 = match.group()

        result = hotlist_card(
            card_last4,
            "Requested by customer"
        )

        print(
            "\n[TOOLS NODE]"
        )

        print(
            f"Calling: hotlist_card({card_last4})"
        )

        return {
            "response": result.get(
                "message",
                "Card request processed."
            )
        }

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return {
        "response": (
            "I could not determine which banking "
            "operation to perform."
        )
    }


# ============================================================
# 17. ESCALATE NODE
# ============================================================

def escalate_node(state):

    print(
        "\n[ESCALATE NODE] Request escalated."
    )

    return {
        "response": (
            "I'm sorry, but I'm unable to confidently "
            "handle this request. Please contact a human "
            "support representative."
        )
    }


# ============================================================
# 18. BUILD LANGGRAPH
# ============================================================

builder = StateGraph(BotState)


# Add nodes

builder.add_node(
    "classify",
    classify_node
)

builder.add_node(
    "rag",
    rag_node
)

builder.add_node(
    "tools",
    tools_node
)

builder.add_node(
    "escalate",
    escalate_node
)


# START -> CLASSIFY

builder.add_edge(
    START,
    "classify"
)


# CLASSIFY -> CONDITIONAL ROUTING

builder.add_conditional_edges(
    "classify",
    route_intent,
    {
        "rag": "rag",
        "tools": "tools",
        "escalate": "escalate"
    }
)


# RAG -> END

builder.add_edge(
    "rag",
    END
)


# TOOLS -> END

builder.add_edge(
    "tools",
    END
)


# ESCALATE -> END

builder.add_edge(
    "escalate",
    END
)


# Compile graph

graph = builder.compile()


# ============================================================
# 19. MAIN CHAT LOOP
# ============================================================

if __name__ == "__main__":

    # Conversation memory

    messages = []

    print("\n" + "=" * 60)
    print("       CAPSTONE BANKING ASSISTANT")
    print("=" * 60)

    print("Type 'exit' to stop.")

    while True:

        # ----------------------------------------------------
        # Get User Input
        # ----------------------------------------------------

        user_input = input(
            "\nYou: "
        ).strip()

        # Exit condition

        if user_input.lower() == "exit":

            print(
                "\nThank you for using the Banking Assistant."
            )

            break

        # Ignore empty input

        if not user_input:

            continue

        # ----------------------------------------------------
        # Add User Message to Memory
        # ----------------------------------------------------

        messages.append({
            "role": "user",
            "content": user_input
        })

        # ----------------------------------------------------
        # Invoke Graph
        # ----------------------------------------------------

        result = graph.invoke({
            "user_input": user_input,
            "intent": "",
            "confidence": 0.0,
            "response": "",
            "messages": messages
        })

        # ----------------------------------------------------
        # Get Response
        # ----------------------------------------------------

        response = result["response"]

        print(
            f"\nBot: {response}"
        )

        # ----------------------------------------------------
        # Add Bot Response to Memory
        # ----------------------------------------------------

        messages.append({
            "role": "assistant",
            "content": response
        })
