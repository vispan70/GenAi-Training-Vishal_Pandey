# TASK 6.2 — Graph Router

## Objective

The goal of Task 6.2 was to rebuild the Day-3 banking router using LangGraph.

The Day-2 intent classifier was reused for intent classification, while the Day-3 FAQ, mock API, small-talk, and escalation behavior was moved into separate helper functions.

The main difference is that Day 6 represents the routing logic as an explicit LangGraph with nodes and conditional edges.

---

## Day 6 Folder Structure

```text
day06/
│
├── intent_classifier.py
├── router_helpers.py
├── graph_router.py
└── notes.md
```

* `intent_classifier.py` contains the Day-2 intent classification logic.
* `router_helpers.py` contains the Day-3 FAQ, mock API, escalation, and small-talk logic.
* `graph_router.py` builds and runs the LangGraph.
* `notes.md` contains the observations and comparison.

---

## State

The graph uses the following state:

```python
{
    "user_input": str,
    "intent": str,
    "confidence": float,
    "response": str,
    "handover": dict | None
}
```

The state is passed between nodes during graph execution.

---

## Graph Flow

The graph follows this general flow:

```text
START
  ↓
classify
  ↓
conditional routing
  ├── balance_enquiry ───────→ mock_api ───→ END
  ├── card_hotlist ──────────→ mock_api ───→ END
  ├── statement_request ─────→ mock_api ───→ END
  ├── upi_issue ─────────────→ faq ─────────→ END
  ├── small_talk ────────────→ small_talk ──→ END
  ├── out_of_scope ──────────→ escalate ────→ END
  └── confidence < 0.6 ──────→ escalate ───→ END
```

For `upi_issue`, the FAQ node checks whether a matching FAQ answer exists. If no FAQ answer is found, the request is escalated.

---

## Routing Rules

The routing behavior from Day 3 was preserved.

### 1. Low confidence

If:

```text
confidence < 0.6
```

the request is sent to:

```text
escalate
```

### 2. Out of scope

```text
out_of_scope → escalate
```

### 3. Small talk

```text
small_talk → direct reply → END
```

The bot responds:

```text
Hello! How can I help you with your banking request?
```

### 4. Banking operations

The following intents go to the mock API:

```text
balance_enquiry
card_hotlist
statement_request
```

### 5. UPI issues

```text
upi_issue → faq
```

If the FAQ finds a matching answer, the answer is returned.

If no FAQ answer is found, the request is escalated.

---

# Test Results

The graph router was tested using the same type of utterances used in the previous tasks.

## Test 1 — Balance Enquiry

### User

```text
What's my account balance?
```

### Classifier result

```text
Intent: balance_enquiry
Confidence: 0.95
```

### Route

```text
classify → mock_api → END
```

### Response

```text
{'status': 'ok', 'action': 'balance_checked', 'balance': '₹25,430.50'}
```

### Result

```text
PASS
```

---

## Test 2 — Card Hotlist

### User

```text
I lost my debit card, block it now!
```

### Classifier result

```text
Intent: card_hotlist
Confidence: 0.95
```

### Route

```text
classify → mock_api → END
```

### Response

```text
{'status': 'ok', 'action': 'card_hotlisted', 'ref': 'HTL-1029'}
```

### Result

```text
PASS
```

---

## Test 3 — Statement Request

### User

```text
Email me my statement for July
```

### Classifier result

```text
Intent: statement_request
Confidence: 0.95
```

The classifier also extracted:

```text
period: July
```

### Route

```text
classify → mock_api → END
```

### Response

```text
{'status': 'ok', 'action': 'statement_requested', 'ref': 'STM-2048'}
```

### Result

```text
PASS
```

---

## Test 4 — UPI Issue

### User

```text
My UPI payment failed but money was deducted
```

### Classifier result

```text
Intent: upi_issue
Confidence: 0.95
```

### Route

```text
classify → faq → END
```

### Response

```text
Please check your UPI PIN and try again.
```

### Result

```text
PASS
```

---

## Test 5 — Small Talk

### User

```text
Hi, good morning!
```

### Classifier result

```text
Intent: small_talk
Confidence: 0.95
```

### Route

```text
classify → small_talk → END
```

### Response

```text
Hello! How can I help you with your banking request?
```

### Result

```text
PASS
```

---

## Test 6 — Out of Scope

### User

```text
Which mutual fund should I invest in?
```

### Classifier result

```text
Intent: out_of_scope
Confidence: 1.0
```

### Route

```text
classify → escalate → END
```

### Response

```text
Your request has been handed over to a customer-service representative.
```

### Handover

```text
{
    'reason': 'Request is out of scope',
    'intent': 'out_of_scope',
    'entities': {},
    'summary_for_agent': 'Which mutual fund should I invest in?'
}
```

### Result

```text
PASS
```

---

# Additional Tests

The following repeated tests also produced the expected behavior.

### Balance

```text
What's my account balance?
```

Result:

```text
balance_enquiry → mock_api
```

### Card Hotlist

```text
I lost my debit card, block it now!
```

Result:

```text
card_hotlist → mock_api
```

### Statement

```text
I need last 3 months' transactions
```

Result:

```text
statement_request → mock_api
```

Confidence:

```text
0.9
```

### UPI

```text
My UPI payment failed but money was deducted
```

Result:

```text
upi_issue → faq
```

---

# Observations

1. The Day-2 classifier successfully produced the expected intents.
2. The confidence values were above the 0.6 threshold for the tested normal requests.
3. Banking intents were routed to the mock API node.
4. UPI issues were routed to the FAQ node.
5. Small-talk requests received a direct response instead of being escalated.
6. Out-of-scope requests were correctly escalated.
7. The graph preserved the routing behavior from Day 3.
8. The graph makes the control flow easier to visualize and audit than a large sequence of `if/elif` statements.

---

# Day 3 vs Day 6

## Day 3

```text
User input
    ↓
Classifier
    ↓
if/elif routing
    ↓
Handler
    ↓
Response
```

## Day 6

```text
User input
    ↓
classify node
    ↓
conditional edge
    ↓
Handler node
    ↓
END
```

The business behavior remains the same, but the control flow is now explicitly represented as a graph.

---

# Why This Matters in a Bank

The graph makes customer-request routing visible and auditable, so developers and reviewers can clearly see where each request goes.

This helps with debugging, monitoring, compliance, and safely controlling sensitive banking operations.

---

# Final Conclusion

Task 6.2 successfully rebuilt the Day-3 router using LangGraph.

The important concepts demonstrated are:

* Shared graph state
* Nodes
* Conditional edges
* `START`
* `END`
* Intent-based routing
* Confidence-based escalation
* Reusing existing classifier logic
* Explicit and auditable control flow

The main learning is:

```text
Day 2:
User input → Intent + Confidence

Day 3:
Intent + Confidence → Routing decision

Day 6:
User input → classify node → conditional graph edge → handler node → END
```

Therefore, the Day-6 graph router provides the same routing behavior as the earlier router while making the control flow explicit, drawable, and auditable.
