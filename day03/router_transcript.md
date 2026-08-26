# Day 3.2 — Router Transcript

**You:** What's my account balance?  
**Bot:** `{'status': 'ok', 'action': 'balance_checked', 'balance': '₹25,430.50'}`

**You:** I lost my debit card, please block it.  
**Bot:** `{'status': 'ok', 'action': 'card_hotlisted', 'ref': 'HTL-1029'}`

**You:** Email me my statement for July.  
**Bot:** `{'status': 'ok', 'action': 'statement_requested', 'ref': 'STM-2048'}`

**You:** My UPI payment failed.  
**Bot:** `{'type': 'faq_answer', 'message': 'Please check your UPI PIN and try again.'}`

**You:** Hi, good morning!  
**Bot:** `{'type': 'direct_reply', 'message': 'Hello! How can I help you with your banking request?'}`

**You:** Which mutual fund should I invest in?  
**Bot:** `{'reason': 'Request is out of scope', 'intent': 'out_of_scope', 'entities': {}, 'summary_for_agent': 'Which mutual fund should I invest in?'}`


## Summary

The router successfully demonstrates the main Day 3.2 workflow:

- **Balance enquiry** → routed to the mock API.
- **Card hotlist** → routed to the mock API.
- **Statement request** → routed to the mock API.
- **UPI issue** → checked against the FAQ first.
- **Small talk** → handled with a direct reply.
- **Out-of-scope request** → escalated to a human agent.

This is a **workflow, not an agent**, because the routing decisions are predefined using fixed `if/elif` rules. The system does not autonomously decide what actions or tools to use.