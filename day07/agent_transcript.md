# Day 7 — Task 7.1: ReAct Agent with Banking Tools

## Overview

In this task, I built a ReAct banking agent using LangGraph's `create_react_agent`. The agent was provided with two tools:

* `get_balance` — retrieves the balance for a given account ID.
* `hotlist_card` — blocks a card using its last four digits and returns a reference number.

The agent uses the tools when required instead of inventing balances or hotlisting reference numbers.

---

# Test A — Balance Enquiry

## User Input

> What's the balance of ACC1001?

## Agent Execution

### Tool Call

```text
Tool: get_balance
Arguments: {'account_id': 'ACC1001'}
```

### Tool Result

```text
Account ACC1001 balance is ₹42,500.50.
```

### Agent Response

```text
The balance of ACC1001 is ₹42,500.50.
```

## Observation

The agent correctly identified that account information was required and called the `get_balance` tool. It used the result returned by the tool to answer the user.

---

# Test B — Card Hotlisting

## User Input

> Block my card ending 4412, I lost it.

## Agent Execution

### Tool Call

```text
Tool: hotlist_card
Arguments: {'card_last4': '4412', 'reason': 'lost'}
```

### Tool Result

```text
Card ending 4412 has been hotlisted successfully.
Reason: lost.
Reference: HTL-7042
```

### Agent Response

```text
Your card ending in 4412 has been successfully hotlisted due to being lost.
The reference number for this action is HTL-7042.
```

## Observation

The agent understood that the user wanted to block a lost card. It called the `hotlist_card` tool with the card number and reason, then used the tool-generated reference number in its response.

---

# Test C — Chained Tool Calls

## User Input

> I lost my card ending 4412 — block it and then tell me my remaining balance in ACC1001.

## Agent Execution

### Tool Calls

```text
Tool: hotlist_card
Arguments: {'card_last4': '4412', 'reason': 'lost'}

Tool: get_balance
Arguments: {'account_id': 'ACC1001'}
```

### Tool Result 1

```text
Card ending 4412 has been hotlisted successfully.
Reason: lost.
Reference: HTL-9839
```

### Tool Result 2

```text
Account ACC1001 balance is ₹42,500.50.
```

### Agent Response

```text
Your card ending 4412 has been hotlisted successfully.
Reference number: HTL-9839.

Your remaining balance in account ACC1001 is ₹42,500.50.
```

## Observation

This was the most important test. The agent successfully used both tools in a single user request:

1. `hotlist_card`
2. `get_balance`

The agent completed both requested actions and combined the results into a final response. This demonstrates that a ReAct agent can perform multiple tool calls to complete a more complex request.

---

# Test D — Unknown Account

## User Input

> What's the balance of ACC9999?

## Agent Execution

### Tool Call

```text
Tool: get_balance
Arguments: {'account_id': 'ACC9999'}
```

### Tool Result

```text
Error: Account ACC9999 was not found.
```

### Agent Response

```text
I encountered an error while checking the balance for ACC9999:
the account was not found. Please verify the account ID and try again.
```

## Observation

The account `ACC9999` does not exist in the mock data. The `get_balance` tool returned an error, and the agent reported the error honestly instead of inventing a balance.

---

# Key Learnings

## 1. Tools give agents access to external functionality

The agent itself does not contain the account balances or card information. It uses tools to retrieve or process information when needed.

```text
User
  ↓
ReAct Agent
  ↓
Decides which tool is needed
  ↓
Calls Tool
  ↓
Receives Tool Result
  ↓
Generates Final Response
```

---

## 2. The `@tool` decorator converts Python functions into agent tools

The two Python functions:

```python
get_balance()
hotlist_card()
```

were exposed to the ReAct agent using the `@tool` decorator.

This allowed the model to understand the available actions and call them with appropriate arguments.

---

## 3. The agent decides when to use a tool

Unlike the Day 6 graph router, where routing decisions were manually defined using conditional edges, the ReAct agent decides which tool to use based on the user's request.

Conceptually:

```text
                ┌──────────────┐
                │    Agent     │
                └──────┬───────┘
                       │
                 Need a tool?
                  /         \
                Yes          No
                 │            │
                 ▼            ▼
               Tool          END
                 │
                 ▼
            Tool Result
                 │
                 └──────► Agent
```

---

## 4. Agents can chain multiple tool calls

The chained request demonstrated that an agent can use more than one tool while handling a single user message.

```text
User Request
     ↓
hotlist_card
     ↓
Tool Result
     ↓
get_balance
     ↓
Tool Result
     ↓
Final Agent Response
```

---

## 5. Tool results help prevent hallucination

For the unknown account `ACC9999`, the tool returned an error.

The agent did not invent a balance. Instead, it honestly communicated that the account was not found.

This demonstrates an important principle when building AI agents:

> Tools should be the source of truth for external data, and the agent should use tool results rather than inventing information.

---

# Conclusion

The ReAct banking agent successfully completed all four required tests.

* Balance enquiry successfully triggered `get_balance`.
* Card blocking successfully triggered `hotlist_card`.
* The chained request successfully triggered both tools.
* The unknown account produced an honest error without hallucinating a balance.

The main learning from this task was understanding how a ReAct agent can dynamically select and use tools, process tool results, chain multiple actions, and provide grounded responses based on external data.
