## TASK 2.1 — Bad Prompt vs. Good Prompt

# Prompt Comparison

## PROMPT A - SIMPLE PROMPT

**Summary:** The customer visited the MG Road branch twice (Tuesday and Thursday) to update their mobile number but faced a 45-minute wait, system downtime, and missing form requirements. Their UPI has been failing since the 3rd, with an EMI due on the 10th. This is their third complaint. Reference: CMP-88213.

## PROMPT B - STRUCTURED PROMPT

issue: Mobile number update failure causing UPI issues and EMI payment risk

severity: high

requested_action: Complete the mobile number update to restore UPI functionality and enable the EMI payment.

## Observation

1. Prompt A produced a general summary with extra details and no fixed structure.
2. Prompt B produced exactly the requested three fields (`issue`, `severity`, and `requested_action`), making the output easier to read and process programmatically.
3. The structured prompt improved consistency and control over the response, while the constraint prevented the model from inventing a requested action and returned `Not Mentioned` when it was not present in the complaint.