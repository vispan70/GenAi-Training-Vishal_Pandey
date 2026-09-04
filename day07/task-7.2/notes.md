# Task 7.2 – Capstone Banking Assistant Notes

## Overview

In this task, I tested the Capstone Banking Assistant by combining multiple concepts learned in the previous tasks.

The assistant integrates:

* Intent Classification
* LangGraph Routing
* RAG (Retrieval-Augmented Generation)
* Multi-Query Retrieval
* Banking Tools
* Conversation State / Context

The application decides whether a user query should be answered using the Knowledge Base (RAG) or by calling a banking tool.

---

## Observed Flow

The overall flow of the application is:

```text
User Input
    ↓
Classifier Node
    ↓
Intent + Confidence
    ↓
Router
   ↙       ↘
 RAG       Tools
   ↓         ↓
Knowledge   Banking Functions
Base        (Balance/Statement)
   ↓         ↓
       Final Response
```

---

## Test 1 – UPI Daily Limit

### User Input

```text
What is the UPI daily limit?
```

### Classification

```text
Intent: upi_issue
Confidence: 0.95
```

The router identified this as an informational query and routed it to the RAG pipeline.

### Multi-Query Generation

The system generated multiple versions of the user's query:

1. What is the daily transaction limit for UPI?
2. UPI daily transfer limit details
3. How much money can I send via UPI in a day?
4. What is the UPI daily limit?

These queries improve retrieval by searching the knowledge base using different phrasings.

### Final Response

```text
The UPI daily limit is ₹1,00,000 per customer per day.
```

### Observation

The RAG pipeline successfully retrieved the relevant information from the knowledge base and generated the correct answer.

---

## Test 2 – Account Balance

### User Input

```text
What is the balance of ACC1001?
```

### Classification

```text
Intent: balance_enquiry
Confidence: 0.95
```

The router identified this as a transactional query and routed it to the Tools node.

### Tool Called

```text
get_balance(ACC1001)
```

### Final Response

```text
Your account balance for ACC1001 is ₹50,000.
```

### Observation

The assistant correctly extracted the account ID and called the appropriate banking tool instead of searching the knowledge base.

---

## Test 3 – Account Statement

### User Input

```text
Show statement for ACC1001
```

### Classification

```text
Intent: statement_request
Confidence: 0.95
```

The query was routed to the Tools node.

### Tool Called

```text
get_statement(ACC1001, recent transactions)
```

### Final Response

```text
Statement for ACC1001 (recent transactions):

2026-08-01 | Salary Credit | +₹50,000
2026-08-03 | Grocery Store | -₹2,500
2026-08-05 | Electricity Bill | -₹1,800
2026-08-10 | UPI Transfer | -₹5,000
```

### Observation

The assistant successfully selected the statement tool and returned the recent transaction history for the requested account.

---

# Conversation Context Test

I also tested whether the assistant could remember account information provided earlier in the conversation.

### User Input

```text
My account is ACC1001
```

### Classification

```text
Intent: account_information
Confidence: 0.95
```

This query was routed to RAG because it was classified as informational.

### Response

```text
The information is not available in the knowledge base.
```

### Observation

Although RAG could not answer the account-related statement, the system preserved the account ID `ACC1001` in the conversation context.

---

## Follow-up Question

### User Input

```text
What savings accounts do you offer?
```

### Classification

```text
Intent: account_information
Confidence: 0.95
```

The query was routed to RAG.

### Response

```text
The information is not available in the knowledge base.
```

### Observation

The answer was unavailable because the required savings account information was not present in the knowledge base.

This demonstrates that RAG answers depend on the documents available in the vector database.

---

## Context Memory Test

### User Input

```text
And what's my balance?
```

### Classification

```text
Intent: balance_enquiry
Confidence: 0.95
```

The router identified this as a transactional query and sent it to the Tools node.

### Tool Called

```text
get_balance(ACC1001)
```

### Final Response

```text
Your account balance for ACC1001 is ₹50,000.
```

### Important Observation

The user did not provide the account number again in the question.

However, the assistant remembered the previously mentioned account:

```text
ACC1001
```

and successfully used it while calling the balance tool.

This demonstrates that conversation state/context is working correctly.

---

# Key Learnings

Through this task, I observed how different AI components work together in a single banking assistant.

### 1. Intent Classification

The classifier identifies the user's intent and provides a confidence score.

Examples:

```text
upi_issue → RAG
balance_enquiry → Tools
statement_request → Tools
account_information → RAG
```

---

### 2. Intelligent Routing

The router decides which system component should handle the request.

```text
Informational Queries → RAG
Transactional Queries → Banking Tools
```

This prevents unnecessary tool calls and ensures that each query is handled by the appropriate component.

---

### 3. Multi-Query RAG

For informational questions, the system generates multiple variations of the original query.

This improves document retrieval because relevant information may use different wording than the user's original question.

---

### 4. Tool Integration

Transactional banking operations are handled using tools.

Examples:

```text
get_balance(account_id)
get_statement(account_id)
```

The assistant can dynamically select and call the appropriate tool based on the detected intent.

---

### 5. Conversation Context

The assistant can preserve important information from earlier messages.

For example:

```text
User: My account is ACC1001
```

Later:

```text
User: And what's my balance?
```

The assistant successfully used `ACC1001` from the previous conversation context.

---

## Conclusion

The Capstone Banking Assistant successfully integrates multiple concepts learned throughout the training:

* Intent Classification
* LangGraph
* Conditional Routing
* RAG
* Multi-Query Retrieval
* Tool Calling
* Conversation State

The system correctly distinguishes between informational and transactional requests.

Informational queries are routed to the RAG pipeline, while transactional queries such as balance enquiries and statement requests are handled through banking tools.

The final context-memory test also demonstrated that the assistant can remember previously provided account information and use it in follow-up queries, making the conversation more natural and context-aware.
