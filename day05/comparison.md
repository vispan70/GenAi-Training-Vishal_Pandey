# Day 5 — Multi-Query Retrieval Comparison

## Task 5.1 — Multi-Query Retrieval, Measured

### Objective

The goal of this task was to improve the Day 4 single-query RAG system by generating three differently-worded versions of each user question before retrieval.

For each question:

1. The LLM generates exactly three alternative queries.
2. Each query retrieves the top 3 chunks from Chroma.
3. The retrieved chunks are merged.
4. Duplicate chunks are removed based on their content.
5. The remaining chunks are passed to the grounded LLM for the final answer.
6. The same eight questions from Day 4 are used to compare the results.

The Multi-Query RAG therefore retrieves up to 9 chunks initially (3 queries × 3 chunks), followed by content-based deduplication.

---

## Before vs After Comparison

| # | Question                                                   | Day 5 Retrieved Sources                           | Chunks Before Dedup | Unique Chunks | Answer Quality    | Refusal Test |
| - | ---------------------------------------------------------- | ------------------------------------------------- | ------------------: | ------------: | ----------------- | ------------ |
| 1 | What is the UPI daily limit?                               | `upi_limits_and_failures.txt`                     |                   9 |             3 | Good              | N/A          |
| 2 | What are the steps for hotlisting a debit card?            | `debit_card_hotlisting_process.txt`               |                   9 |             3 | Good              | N/A          |
| 3 | What documents are required for KYC?                       | `kyc_requirements.txt`, `savings_account_faq.txt` |                   9 |             5 | Good              | N/A          |
| 4 | What is the minimum tenure for a fixed deposit?            | `fixed_deposit_basics.txt`                        |                   9 |             4 | Refused correctly | N/A          |
| 5 | What are the eligibility requirements for a personal loan? | `personal_loan_eligibility.txt`                   |                   9 |             3 | Good              | N/A          |
| 6 | What are the grievance escalation levels?                  | `grievance_escalation_matrix.txt`                 |                   9 |             3 | Good              | N/A          |
| 7 | What is today's USD-INR exchange rate?                     | `upi_limits_and_failures.txt`                     |                   9 |             3 | Refused correctly | Yes          |
| 8 | What are the charges for the Platinum Sapphire card?       | `charges_schedule.txt`, `credit_card_types.txt`   |                   9 |             5 | Refused correctly | Yes          |

---

## Detailed Results

### 1. UPI Daily Limit

**Question:**
What is the UPI daily limit?

**Generated query variations:**

1. What is the daily limit for UPI transactions?
2. How much can I transact using UPI in a day?
3. What is the maximum amount allowed for UPI transactions each day?

**Retrieval:**

* 9 chunks retrieved initially.
* 3 unique chunks remained after deduplication.
* All retrieved sources came from `upi_limits_and_failures.txt`.

**Final answer:**

> The UPI daily limit is ₹1,00,000 per customer per day [upi_limits_and_failures.txt].

**Assessment:** Good. The answer directly addresses the question and is grounded in the knowledge base.

---

### 2. Debit Card Hotlisting

**Question:**
What are the steps for hotlisting a debit card?

**Generated query variations:**

1. How do I hotlist my debit card?
2. What is the process to hotlist a debit card?
3. Can you outline the steps to hotlist a debit card?

**Retrieval:**

* 9 chunks retrieved initially.
* 3 unique chunks remained.
* All relevant chunks came from `debit_card_hotlisting_process.txt`.

**Assessment:** Good. The final response provided the hotlisting steps and cited the correct source.

---

### 3. KYC Documents

**Question:**
What documents are required for KYC?

**Generated query variations:**

1. What paperwork do I need for KYC?
2. Which documents are necessary for KYC compliance?
3. What are the required documents for Know Your Customer (KYC)?

**Retrieval:**

* 9 chunks retrieved initially.
* 5 unique chunks remained.
* Sources included `kyc_requirements.txt` and `savings_account_faq.txt`.

**Assessment:** Good. Multi-query retrieval found the primary KYC source and also retrieved an additional related source. The final answer was based on the relevant KYC information.

---

### 4. Fixed Deposit Minimum Tenure

**Question:**
What is the minimum tenure for a fixed deposit?

**Generated query variations:**

1. What is the shortest duration for a fixed deposit?
2. How long is the minimum term for a fixed deposit?
3. What is the least amount of time required for a fixed deposit?

**Retrieval:**

* 9 chunks retrieved initially.
* 4 unique chunks remained.
* All retrieved sources came from `fixed_deposit_basics.txt`.

**Final answer:**

> I don't have that information in my knowledge base — let me connect you to a human agent.

**Assessment:** Refused correctly. Although related fixed-deposit chunks were retrieved, the context did not contain the specific minimum-tenure information required to answer the question. The system correctly avoided inventing an answer.

This is an important positive result for the hallucination-safety requirement.

---

### 5. Personal Loan Eligibility

**Question:**
What are the eligibility requirements for a personal loan?

**Generated query variations:**

1. What criteria must be met to qualify for a personal loan?
2. What are the requirements to be eligible for a personal loan?
3. What do I need to qualify for a personal loan?

**Retrieval:**

* 9 chunks retrieved initially.
* 3 unique chunks remained.
* All relevant chunks came from `personal_loan_eligibility.txt`.

**Final answer:**

> A customer may be considered for a personal loan based on the bank's credit and risk assessment [personal_loan_eligibility.txt].

**Assessment:** Good. The response remained grounded in the retrieved knowledge-base information.

---

### 6. Grievance Escalation Levels

**Question:**
What are the grievance escalation levels?

**Generated query variations:**

1. What levels are involved in the grievance escalation process?
2. Can you explain the different levels of grievance escalation?
3. What are the various stages of escalating a grievance?

**Retrieval:**

* 9 chunks retrieved initially.
* 3 unique chunks remained.
* All relevant chunks came from `grievance_escalation_matrix.txt`.

**Assessment:** Good. The final answer correctly listed the four grievance escalation levels and cited the appropriate source.

---

### 7. Today's USD-INR Exchange Rate

**Question:**
What is today's USD-INR exchange rate?

**Generated query variations:**

1. What is the current exchange rate for USD to INR today?
2. Can you tell me the USD to INR exchange rate for today?
3. What is the exchange rate of USD against INR as of today?

**Retrieval:**

* 9 chunks retrieved initially.
* 3 unique chunks remained.
* The retrieved source was `upi_limits_and_failures.txt`, which was unrelated to the exchange-rate question.

**Final answer:**

> I don't have that information in my knowledge base — let me connect you to a human agent.

**Assessment:** Refused correctly. The system did not use the irrelevant retrieved content to invent an exchange rate.

This confirms that Multi-Query Retrieval did not cause the bot to hallucinate when the requested information was unavailable.

---

### 8. Platinum Sapphire Card Charges

**Question:**
What are the charges for the Platinum Sapphire card?

**Generated query variations:**

1. What fees are associated with the Platinum Sapphire card?
2. Can you provide information on the charges for the Platinum Sapphire card?
3. What costs are involved with the Platinum Sapphire card?

**Retrieval:**

* 9 chunks retrieved initially.
* 5 unique chunks remained.
* Sources included `charges_schedule.txt` and `credit_card_types.txt`.

**Final answer:**

> I don't have that information in my knowledge base — let me connect you to a human agent.

**Assessment:** Refused correctly. Although related card and charges documents were retrieved, the retrieved context did not provide enough specific information about the Platinum Sapphire card charges. The system correctly avoided guessing.

---

# Multi-Query Retrieval Observations

## Where Multi-Query Helped

Multi-query retrieval successfully generated three semantically similar versions of every question and retrieved multiple sets of chunks. This was particularly useful for questions where different wording could point the vector search toward related documents.

The KYC question demonstrated this clearly because the three query variations resulted in five unique chunks from two related sources: `kyc_requirements.txt` and `savings_account_faq.txt`.

The approach also maintained good retrieval for questions such as UPI limits, debit-card hotlisting, personal-loan eligibility, and grievance escalation.

---

## Where Multi-Query Did Not Provide a Major Benefit

For several straightforward questions, all three query variations retrieved essentially the same relevant chunks.

For example, the UPI daily-limit, debit-card-hotlisting, personal-loan, and grievance questions produced only three unique chunks from nine retrieved chunks.

This means that the additional query variations increased retrieval work without necessarily adding new information.

Therefore, Multi-Query Retrieval is not automatically better for every question.

---

## Hallucination and Refusal Check

The two important out-of-knowledge-base questions were tested:

1. What is today's USD-INR exchange rate?
2. What are the charges for the Platinum Sapphire card?

Both questions correctly produced the required refusal response:

> I don't have that information in my knowledge base — let me connect you to a human agent.

The fixed-deposit minimum-tenure question also correctly refused because the retrieved context did not contain the requested specific information.

This demonstrates that the additional retrieval queries did not cause the LLM to invent unsupported answers.

---

# Three-Line Conclusion

1. **Multi-query helped** by providing alternative search formulations and, in some cases, retrieving additional relevant chunks that could improve the available context.

2. **Multi-query also added overhead** because many straightforward questions returned the same chunks for all three query variations, providing little or no improvement over single-query retrieval.

3. **In production, I would use multi-query selectively** for ambiguous, complex, or poorly phrased questions rather than enabling it for every user query, balancing retrieval quality against additional LLM and vector-search cost.
