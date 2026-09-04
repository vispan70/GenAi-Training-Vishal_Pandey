import json
from pathlib import Path


# ============================================================
# Load Mock Data
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "mock_data.json"


def load_data():

    with open(DATA_FILE, "r") as file:
        return json.load(file)


# ============================================================
# Tool 1 - Get Balance
# ============================================================

def get_balance(account_id: str):

    data = load_data()

    for account in data["accounts"]:

        if account["account_id"] == account_id:

            return {
                "status": "success",
                "account_id": account_id,
                "balance": account["balance"]
            }

    return {
        "status": "error",
        "message": "Account not found"
    }


# ============================================================
# Tool 2 - Hotlist Card
# ============================================================

def hotlist_card(card_last4: str, reason: str):

    data = load_data()

    for account in data["accounts"]:

        for card in account.get("cards", []):

            if card["last4"] == card_last4:

                card["status"] = "hotlisted"

                return {
                    "status": "success",
                    "message": (
                        f"Card ending with {card_last4} "
                        f"has been hotlisted. Reason: {reason}"
                    )
                }

    return {
        "status": "error",
        "message": "Card not found"
    }


# ============================================================
# Tool 3 - Get Statement
# ============================================================

def get_statement(account_id: str, period: str):

    statements = {
        "ACC1001": [
            "2026-08-01 | Salary Credit | +₹50,000",
            "2026-08-03 | Grocery Store | -₹2,500",
            "2026-08-05 | Electricity Bill | -₹1,800",
            "2026-08-10 | UPI Transfer | -₹5,000"
        ],
        "ACC1002": [
            "2026-08-01 | Salary Credit | +₹60,000",
            "2026-08-04 | Restaurant | -₹1,200",
            "2026-08-07 | Mobile Recharge | -₹500",
            "2026-08-12 | ATM Withdrawal | -₹10,000"
        ],
        "ACC1003": [
            "2026-08-02 | Salary Credit | +₹40,000",
            "2026-08-05 | Online Shopping | -₹3,500",
            "2026-08-08 | Fuel | -₹2,000",
            "2026-08-15 | UPI Payment | -₹1,000"
        ]
    }

    if account_id not in statements:

        return {
            "status": "error",
            "message": "Account not found"
        }

    return {
        "status": "success",
        "account_id": account_id,
        "period": period,
        "transactions": statements[account_id]
    }


# ============================================================
# Testing
# ============================================================

if __name__ == "__main__":

    print("\n--- BALANCE TEST ---")
    print(get_balance("ACC1001"))

    print("\n--- HOTLIST TEST ---")
    print(hotlist_card("1234", "Card lost"))

    print("\n--- STATEMENT TEST ---")
    print(get_statement("ACC1001", "August"))
