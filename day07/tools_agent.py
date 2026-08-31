
import os
import json
import random
from pathlib import Path

from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# MOCK DATA FILE
# ============================================================

BASE_DIR = Path(__file__).parent

DATA_FILE = BASE_DIR / "mock_data.json"


# ============================================================
# HELPER: LOAD MOCK DATA
# ============================================================

def load_mock_data():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# TOOL 1: GET BALANCE
# ============================================================

@tool
def get_balance(account_id: str) -> str:
    """
    Return the current balance for an account id like ACC1001.
    Use this tool whenever the user asks for an account balance.
    """

    data = load_mock_data()

    account_id = account_id.upper()

    # --------------------------------------------------------
    # Check if account exists
    # --------------------------------------------------------

    if account_id not in data:

        return (
            f"Error: Account {account_id} was not found."
        )

    # --------------------------------------------------------
    # Get balance
    # --------------------------------------------------------

    balance = data[account_id]["balance"]

    return (
        f"Account {account_id} balance is "
        f"₹{balance:,.2f}."
    )


# ============================================================
# TOOL 2: HOTLIST CARD
# ============================================================

@tool
def hotlist_card(
    card_last4: str,
    reason: str
) -> str:
    """
    Block a card by its last 4 digits and return a reference number.
    Use this tool when a user wants to block, hotlist, or report
    a lost or stolen card.
    """

    # --------------------------------------------------------
    # Validate card number
    # --------------------------------------------------------

    if (
        not card_last4.isdigit()
        or len(card_last4) != 4
    ):

        return (
            "Error: Card number must contain exactly 4 digits."
        )

    # --------------------------------------------------------
    # Load mock data
    # --------------------------------------------------------

    data = load_mock_data()

    # --------------------------------------------------------
    # Check if card exists
    # --------------------------------------------------------

    card_found = False

    for account in data.values():

        if card_last4 in account["cards"]:

            card_found = True

            break

    if not card_found:

        return (
            f"Error: Card ending {card_last4} "
            "was not found."
        )

    # --------------------------------------------------------
    # Generate hotlist reference
    # --------------------------------------------------------

    reference_number = (
        f"HTL-{random.randint(1000, 9999)}"
    )

    return (
        f"Card ending {card_last4} "
        f"has been hotlisted successfully. "
        f"Reason: {reason}. "
        f"Reference: {reference_number}"
    )


# ============================================================
# MODEL
# ============================================================

model = ChatOpenAI(

    model="openai/gpt-4o-mini",

    openai_api_key=os.getenv(
        "OPENROUTER_API_KEY"
    ),

    openai_api_base=(
        "https://openrouter.ai/api/v1"
    )
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a helpful banking assistant.

Rules:

1. Use tools whenever the user asks for an account balance.

2. Use tools whenever the user asks to block, hotlist,
   report lost, or report stolen a card.

3. Never invent account balances.

4. Never invent hotlisting reference numbers.

5. If a tool returns an error, report that error honestly.

6. If the user asks for multiple actions, complete all actions
   using the appropriate tools.

7. Follow the order requested by the user.

Keep responses clear and concise.
"""


# ============================================================
# TOOLS
# ============================================================

tools = [

    get_balance,

    hotlist_card

]


# ============================================================
# CREATE REACT AGENT
# ============================================================

agent = create_react_agent(

    model=model,

    tools=tools,

    prompt=SYSTEM_PROMPT

)


# ============================================================
# RUN AGENT
# ============================================================

def run_agent(user_input: str):

    # --------------------------------------------------------
    # Invoke agent
    # --------------------------------------------------------

    result = agent.invoke(

        {
            "messages": [

                (
                    "user",
                    user_input
                )

            ]
        }

    )

    # --------------------------------------------------------
    # Print agent execution
    # --------------------------------------------------------

    print(
        "\n================ AGENT EXECUTION ================\n"
    )

    for message in result["messages"]:

        # ----------------------------------------------------
        # AI MESSAGE
        # ----------------------------------------------------

        if message.type == "ai":

            # Tool calls made by AI
            if (
                hasattr(message, "tool_calls")
                and message.tool_calls
            ):

                print("AI TOOL CALL:")

                for tool_call in message.tool_calls:

                    print(
                        "Tool:",
                        tool_call["name"]
                    )

                    print(
                        "Arguments:",
                        tool_call["args"]
                    )

                    print()

            # Final AI response
            elif message.content:

                print(
                    "AGENT RESPONSE:"
                )

                print(
                    message.content
                )

                print()

        # ----------------------------------------------------
        # TOOL MESSAGE
        # ----------------------------------------------------

        elif message.type == "tool":

            print(
                "TOOL RESULT:"
            )

            print(
                message.content
            )

            print()


# ============================================================
# REPL
# ============================================================

if __name__ == "__main__":

    print(
        "\nBanking ReAct Agent"
    )

    print(
        "Type 'exit' to stop.\n"
    )

    while True:

        user_input = input(
            "You: "
        ).strip()

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_input.lower() in {

            "exit",

            "quit"

        }:

            print(
                "Bot: Goodbye!"
            )

            break

        # ----------------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------------

        if not user_input:

            continue

        try:

            # ------------------------------------------------
            # Run agent
            # ------------------------------------------------

            run_agent(
                user_input
            )

        except Exception as error:

            print(
                "\nERROR:"
            )

            print(
                error
            )

            print()
