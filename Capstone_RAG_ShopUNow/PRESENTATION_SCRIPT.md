# Capstone Project - 1:1 Presentation Script

ShopUNow Agentic RAG System. 10 slides, aim for 8-12 min.

---

## Slide 1: Title
**Content**
- ShopUNow Agentic RAG System
- Capstone Project - Agentic AI Program
- Your Name | Date

**Notes**: Introduce yourself and the project in one line: a router-based support system with sentiment analysis and RAG.

---

## Slide 2: Problem & Goal
**Content**
- ShopUNow needs to answer customer AND employee queries at scale
- Route each query to the right department
- Escalate upset customers to a human
- Ground answers in a knowledge base (no hallucinations)

**Notes**: Set the business context - why an agentic RAG system instead of a single prompt.

---

## Slide 3: System Overview
**Content**
- Router-based customer/employee support assistant
- Stack: LangGraph, FAISS, OpenAI GPT-4o-mini, LangChain
- 6 departments (3 external, 3 internal)

**Notes**: Name the tech and why each was chosen (LangGraph for state/routing, FAISS for retrieval).

---

## Slide 4: Architecture
**Content**
- Query -> Analyze (sentiment + department) -> Route
- Route to: Human Escalation OR RAG Response
- Negative/unknown -> escalate; positive/neutral + valid -> RAG

**Notes**: Show the flow diagram from README.md. Walk through the routing decision step by step.

---

## Slide 5: Departments & Knowledge Base
**Content**
- External: Customer Support, Product Info, Shipping & Delivery
- Internal: HR, IT Support, Finance
- 84 QA pairs (12-15 per department) with metadata

**Notes**: Explain how department metadata enables filtered retrieval in FAISS.

---

## Slide 6: Key Files
**Content**
- generate_qa_data.py - creates 84 QA pairs via LLM
- build_vectordb.py - builds FAISS DB + department metadata
- agentic_rag_system.py - LangGraph router system

**Notes**: One sentence per file. Tie each to a requirement.

---

## Slide 7: Required Goals Met
**Content**
- 4+ departments -> delivered 6
- 2+ internal + 2+ external use cases
- 10-15 QA pairs/department -> 84 total
- Vector DB with metadata filtering
- Router + human escalation + RAG responses

**Notes**: Confirm every compulsory requirement is satisfied.

---

## Slide 8: Stretch Goal (Option 3)
**Content**
- Chosen: Option 3 - more departments + diverse routes
- 6 departments instead of the required 4
- Both internal and external workflows
- Sentiment-driven escalation path

**Notes**: Explain why Option 3 and how it added meaningful complexity.

---

## Slide 9: Demo / Sample Run
**Content**
- Positive query -> RAG response (e.g., order tracking)
- Negative sentiment -> human escalation + reference ID
- Department filtering in action

**Notes**: Run live or show 2 contrasting screenshots. This is the highlight - practice it.

---

## Slide 10: Lessons Learned & Next Steps
**Content**
- Routing + RAG grounding reduces hallucinations
- State machines make complex flows debuggable
- Next: conversation memory, analytics, more channels
- Thank you / Questions

**Notes**: Close with what you learned and one realistic improvement. Invite questions.

---

## Delivery Tips
- 8-12 minutes total, ~1 min/slide
- Have the architecture diagram (Slide 4) and 2 demo screenshots (Slide 9) ready
- Be ready to explain: sentiment routing, FAISS metadata filtering, escalation logic
