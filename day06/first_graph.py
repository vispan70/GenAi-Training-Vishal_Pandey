from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. Define State
# ============================================================

class State(TypedDict):
    name: str
    account_type: str
    message: str


# ============================================================
# 2. Define Nodes
# ============================================================

def greet(state: State):
    return {
        "message": f"Hello {state['name']}!"
    }


def set_account_type(state: State):
    return {
        "account_type": "savings"
    }


def compose(state: State):
    return {
        "message": f"{state['message']} Your account type is {state['account_type']}."
    }


# ============================================================
# 3. Build Graph
# ============================================================

graph = StateGraph(State)

graph.add_node("greet", greet)
graph.add_node("set_account_type", set_account_type)
graph.add_node("compose", compose)

graph.add_edge(START, "greet")
graph.add_edge("greet", "set_account_type")
graph.add_edge("set_account_type", "compose")
graph.add_edge("compose", END)


# ============================================================
# 4. Compile
# ============================================================

app = graph.compile()


# ============================================================
# 5. Get name from user
# ============================================================

name = input("Enter your name: ")


# ============================================================
# 6. Invoke Graph
# ============================================================

result = app.invoke({
    "name": name,
    "account_type": "",
    "message": ""
})


# ============================================================
# 7. Print Final State
# ============================================================

print("\nFinal State:")
print(result)
