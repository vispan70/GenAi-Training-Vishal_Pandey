# RAG Results

## Task 4.2 — Grounded Answers with Citations & Refusal

| Question                                             | Sources retrieved                                                                                       | Answer OK? | Refused correctly? |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---------- | ------------------ |
| What is the UPI daily limit?                         | `upi_limits_and_failures.txt`, `upi_limits_and_failures.txt`, `upi_limits_and_failures.txt`             | Yes        | N/A                |
| What documents are required for KYC?                 | `kyc_requirements.txt`, `kyc_requirements.txt`, `savings_account_faq.txt`                               | Yes        | N/A                |
| What is today's USD–INR exchange rate?               | `charges_schedule.txt`, `fixed_deposit_basics.txt`, `upi_limits_and_failures.txt`                       | N/A        | Yes                |
| What are the charges for the Platinum Sapphire card? | `credit_card_types.txt`, `credit_card_types.txt`, `debit_card_hotlisting_process.txt`                   | N/A        | Yes                |
| What are the eligibility criteria for a loan?        | `personal_loan_eligibility.txt`, `personal_loan_eligibility.txt`, `personal_loan_eligibility.txt`       | No         | No                 |
| What are the steps for hotlisting a card?            | `net_banking_activation.txt`, `debit_card_hotlisting_process.txt`, `debit_card_hotlisting_process.txt`  | No         | No                 |
| What is the grievance escalation levels?             | `grievance_escalation_matrix.txt`, `grievance_escalation_matrix.txt`, `grievance_escalation_matrix.txt` | No         | No                 |
| What is the UPI daily limit?                         | `upi_limits_and_failures.txt`, `upi_limits_and_failures.txt`, `upi_limits_and_failures.txt`             | Yes        | N/A                |

## Answers Observed

### 1. UPI Daily Limit

**Question:** What is the UPI daily limit?

**Retrieved source:** `upi_limits_and_failures.txt`

**Answer:**

The fictional daily UPI transaction limit is â‚¹1,00,000 per customer. [upi_limits_and_failures.txt]

**Answer OK:** Yes

---

### 2. KYC Documents

**Question:** What documents are required for KYC?

**Retrieved sources:** `kyc_requirements.txt`, `savings_account_faq.txt`

**Answer:**

Customers must provide one valid identity document and one valid address document when required for KYC verification [kyc_requirements.txt].

**Answer OK:** Yes

---

### 3. USD–INR Exchange Rate

**Question:** What is today's USD–INR exchange rate?

**Retrieved sources:** `charges_schedule.txt`, `fixed_deposit_basics.txt`, `upi_limits_and_failures.txt`

**Answer:**

I don't have that information in my knowledge base — let me connect you to a human agent.

**Refused correctly:** Yes

---

### 4. Platinum Sapphire Card Charges

**Question:** What are the charges for the Platinum Sapphire card?

**Retrieved sources:** `credit_card_types.txt`, `debit_card_hotlisting_process.txt`

**Answer:**

I don't have that information in my knowledge base — let me connect you to a human agent.

**Refused correctly:** Yes

---

### 5. Loan Eligibility

**Question:** What are the eligibility criteria for a loan?

**Retrieved source:** `personal_loan_eligibility.txt`

**Answer:**

I don't have that information in my knowledge base — let me connect you to a human agent.

**Answer OK:** No

**Observation:** The retriever successfully retrieved `personal_loan_eligibility.txt`, so relevant information appears to have been retrieved. However, the LLM refused to answer instead of generating an answer from the retrieved context.

---

### 6. Card Hotlisting

**Question:** What are the steps for hotlisting a card?

**Retrieved sources:** `net_banking_activation.txt`, `debit_card_hotlisting_process.txt`

**Answer:**

I don't have that information in my knowledge base — let me connect you to a human agent.

**Answer OK:** No

**Observation:** `debit_card_hotlisting_process.txt` was retrieved, which indicates that relevant information was found. However, the LLM refused to answer instead of using the retrieved context.

---

### 7. Grievance Escalation

**Question:** What are the grievance escalation levels?

**Retrieved source:** `grievance_escalation_matrix.txt`

**Answer:**

I don't have that information in my knowledge base — let me connect you to a human agent.

**Answer OK:** No

**Observation:** `grievance_escalation_matrix.txt` was retrieved, indicating that the relevant document was found. However, the LLM refused to answer.

---

### 8. UPI Daily Limit — Repeated Test

**Question:** What is the UPI daily limit?

**Retrieved source:** `upi_limits_and_failures.txt`

**Answer:**

The fictional daily UPI transaction limit is â‚¹1,00,000 per customer. [upi_limits_and_failures.txt]

**Answer OK:** Yes

---

## Summary

The RAG system successfully demonstrated both grounded answering and refusal behavior.

### Successful tests

* The UPI daily limit question was answered using `upi_limits_and_failures.txt`.
* The KYC question was answered using `kyc_requirements.txt`.
* The USD–INR exchange-rate question was correctly refused because the information was not available in the knowledge base.
* The Platinum Sapphire card charges question was correctly refused because the information was not available in the knowledge base.

### Issues observed

Three questions retrieved documents that appear relevant but were still refused:

* Loan eligibility → `personal_loan_eligibility.txt`
* Card hotlisting → `debit_card_hotlisting_process.txt`
* Grievance escalation → `grievance_escalation_matrix.txt`

This suggests that the retrieval step is finding the relevant documents, but the generation step is not correctly using the retrieved context for these questions.

### Overall conclusion

The refusal mechanism works correctly for deliberately unanswerable questions, and the system can produce grounded answers with source citations. However, the generation step needs further debugging because some answerable questions are being refused even when the relevant source document is retrieved.
