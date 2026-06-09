# ShopUNow Agentic RAG System - Spoken Presentation Script

Word-for-word script matched to your 10 slides. Total target: ~9-11 minutes.
Brackets [ ] are stage directions, not spoken.

---

## Slide 1 - Title (~30 sec)
"Hi, I'm [your name], and this is my Capstone Project for the Agentic AI Program: the ShopUNow Agentic RAG System.

In one sentence - it's a router-based intelligent support assistant. It reads a user's query, figures out the sentiment and which department it belongs to, and then either routes the customer to a human or answers the question using retrieval-augmented generation. The whole goal is to answer both customer and employee questions at scale, with grounded, zero-hallucination responses."

[Pause, advance slide.]

---

## Slide 2 - The Problem We're Solving (~75 sec)
"Let me start with why this system needs to exist. There were four problems I designed around.

First, **scale**. ShopUNow gets a high volume of questions from both customers and internal employees, and you can't just keep hiring support staff to keep up.

Second, **routing**. Not every question belongs to the same team. A shipping question and an HR question are completely different, so the system has to identify intent and send each query to the right department automatically.

Third, **escalation**. If a customer is upset, they shouldn't be stuck talking to a bot. I treated sentiment as a first-class signal - if someone's angry, they get handed to a human immediately.

And fourth, **grounding**. A single-prompt LLM can confidently make things up. By using RAG, every answer is pulled from a verified knowledge base, so responses are factual and sourced."

[Advance slide.]

---

## Slide 3 - System Overview / Tech Stack (~75 sec)
"Here's the technology stack and why I chose each piece.

**LangGraph** is the backbone. It's a state-machine framework, so I could build the routing logic as an explicit graph - it tracks the query's state across nodes and lets me use conditional edges to branch the flow.

**FAISS** is the vector store. It does fast similarity search, and critically, it supports metadata filtering, which is what lets me search within a single department.

**OpenAI's GPT-4o-mini** is the LLM. It's lightweight and fast, and I use it for three jobs: classifying sentiment, detecting intent, and generating the final RAG answer.

And **LangChain** is the orchestration layer that ties the LLM, the vector store, and the graph state together into one pipeline."

[Advance slide.]

---

## Slide 4 - Architecture: Routing Decision Flow (~90 sec)
[Point to the diagram as you walk through it.]

"This is the core of the system - the routing flow. Every query goes through the same four stages.

It starts when the user **submits a query**. That query immediately hits a single **analyze** node, where the LLM detects two things at once: the sentiment, and the department.

Then we hit the **route** decision. This is the key branching point. If the sentiment is negative, OR the department comes back as unknown, the system escalates to a human right away. Otherwise - positive or neutral sentiment with a recognized department - it proceeds to FAISS retrieval.

Finally, we **respond** - either with a human handoff message or a grounded RAG answer.

The reason I funnel everything through one analysis node is so that no query falls through the cracks. There's always a defined path: either a human gets it, or the knowledge base answers it."

[Advance slide.]

---

## Slide 5 - Departments & Knowledge Base (~75 sec)
"The system covers six departments, split into two groups.

Three are **external-facing**: Customer Support, Product Information, and Shipping & Delivery. And three are **internal**: Human Resources, IT Support, and Finance.

For the knowledge base, I generated 84 question-answer pairs - between 12 and 15 per department - and each one is tagged with department metadata.

Here's the important design choice: when a query comes in, FAISS **filters by department first**, and then does the similarity search within just that department's pairs. That means an HR question can never accidentally pull a shipping answer. Metadata filtering is really the key to keeping answers accurate and department-specific even though everything lives in one shared vector space."

[Advance slide.]

---

## Slide 6 - Key Project Files (~70 sec)
"The project is three files, and they run as a pipeline.

**generate_qa_data.py** uses GPT-4o-mini to programmatically create all 84 QA pairs across the six departments. So instead of hand-writing FAQs, I had the model generate realistic ones.

**build_vectordb.py** takes those pairs, embeds them, builds the FAISS index, and attaches the department metadata so I can do filtered retrieval later.

And **agentic_rag_system.py** is the core - it's the LangGraph router. It orchestrates the sentiment analysis, the department classification, the escalation logic, and the RAG response generation. That's the file that actually runs at query time."

[Advance slide.]

---

## Slide 7 - All Required Goals Met & Exceeded (~70 sec)
"Now let me map this directly against the project requirements, because I made sure to hit every one.

The brief required **4 departments** - I delivered **6**, all with full QA coverage.

It required **10 to 15 QA pairs per department** - I have **84 total**, exceeding that across all six.

It required at least **2 internal and 2 external** use cases - I delivered **3 of each**.

And it required the three response behaviors - a **router, human escalation, and grounded RAG** - all three are fully implemented and operational.

So every compulsory requirement - the vector DB with metadata filtering, the sentiment-driven escalation, and the department routing - is done."

[Advance slide.]

---

## Slide 8 - Stretch Goal: Option 3 (~60 sec)
"For the stretch goal, I chose **Option 3**, which asked for more departments and more diverse routing paths. I picked it because it was the best way to show real agentic complexity instead of just the baseline.

Concretely, that meant **50% more departments** - six instead of four. It meant **dual workflows** - I'm handling internal HR, IT, and Finance paths alongside the external customer paths. And it meant building the **sentiment-based escalation**, where negative sentiment triggers a tracked human handoff. Those three things together are what take this past the minimum requirement."

[Advance slide.]

---

## Slide 9 - Demo: Two Contrasting Query Paths (~90 sec)
[If running live, run these two queries. Otherwise, walk through the screenshots.]

"Let me show the system in action with two queries that take opposite paths.

First, a normal one: 'Where is my order #12345?' The sentiment comes back neutral-to-positive, and the department is detected as Shipping & Delivery. FAISS retrieves a grounded answer from that department's knowledge base, and the customer gets a response with the order status. That's the happy path - fully automated.

Now the contrast: 'This is unacceptable! My package is lost!' Here the sentiment is detected as negative, so escalation triggers instead of RAG. The system initiates a human handoff immediately, generates a reference ID for tracking, and tells the customer what happens next.

And because of the department filtering, the right team receives each escalation - it's not just a generic dump into one queue."

[Advance slide.]

---

## Slide 10 - Lessons Learned & What's Next (~60 sec)
"To wrap up, two big lessons.

First, **routing plus RAG equals trustworthy AI**. Grounding every answer in a verified knowledge base dramatically cut down hallucinations - the system only says what it actually knows.

Second, **state machines make debugging possible**. Because LangGraph models the flow as explicit state, every multi-path route was traceable and testable as I built it. That structure paid off the whole way through.

For next steps, I'd add conversation memory for multi-turn context, an analytics dashboard to study routing patterns, and expansion to new channels like SMS and email.

That's the ShopUNow Agentic RAG System. Thank you - I'm happy to take any questions."

[End. Smile, pause for Q&A.]

---

## Q&A Prep - likely questions
- **Why two temperatures?** 0.7 when generating QA data for variety; 0.3 in the live agent for consistent answers.
- **How does department filtering work technically?** FAISS `similarity_search` with `filter={"department": dept}` on the metadata before ranking.
- **How is the reference ID made?** Derived from the query hash - good for a demo; I'd use UUID in production for guaranteed uniqueness.
- **What happens on "unknown" department?** It routes to human escalation - the system fails safe rather than guessing.
- **Why GPT-4o-mini?** Fast and cheap for classification + generation; accuracy was sufficient for the FAQ domain.
