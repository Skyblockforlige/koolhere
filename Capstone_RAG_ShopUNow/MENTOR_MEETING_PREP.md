# Capstone Project - Mentor Meeting Preparation Guide

## Project Overview
**ShopUNow Agentic RAG System**: A Router-based intelligent assistant that handles customer and employee queries by analyzing sentiment, routing to appropriate departments, and using RAG (Retrieval Augmented Generation) to provide accurate responses.

---

## LINE-BY-LINE CODE EXPLANATION

### **File 1: agentic_rag_system.py**

#### **Imports (Lines 1-7)**
```python
from langchain_openai import ChatOpenAI
```
- Imports the OpenAI chat model wrapper from LangChain
- Used to interact with GPT-4o-mini for generating responses

```python
from langchain_community.vectorstores import FAISS
```
- FAISS (Facebook AI Similarity Search) is a vector database
- Stores document embeddings for fast similarity search
- Allows filtering by metadata (department in our case)

```python
from langchain_openai import OpenAIEmbeddings
```
- Converts text into numerical vectors (embeddings)
- Uses OpenAI's text-embedding-3-small model
- Embeddings capture semantic meaning of text

```python
from langgraph.graph import StateGraph, START, END
```
- **StateGraph**: Core LangGraph class for building state machines
- **START**: Special node marking the entry point of the graph
- **END**: Special node marking the exit point of the graph

```python
from typing import TypedDict, Literal
```
- **TypedDict**: Defines the structure of our state with type hints
- **Literal**: Restricts return values to specific strings (for routing)

```python
from dotenv import load_dotenv
import os
```
- Loads environment variables from .env file (API keys)
- `os` module for environment variable access

#### **Setup (Lines 9-21)**
```python
load_dotenv()
```
- Loads OPENAI_API_KEY from .env file into environment

```python
class State(TypedDict):
    query: str
    sentiment: str
    department: str
    response: str
    route: str
```
- Defines the **state structure** that flows through the graph
- Each node can read from and write to this state
- **query**: User's input question
- **sentiment**: positive/neutral/negative
- **department**: Which department handles this
- **response**: Final answer to user
- **route**: Which path was taken (for tracking)

```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
```
- Creates LLM instance with GPT-4o-mini model
- **temperature=0.3**: Low randomness for more consistent outputs
- Higher temp = more creative, lower temp = more deterministic

```python
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local("shopunow_vectordb", embeddings, allow_dangerous_deserialization=True)
```
- Creates embedding model instance
- Loads pre-built FAISS vector database from disk
- **allow_dangerous_deserialization=True**: Required to load pickled data (security flag)

```python
VALID_DEPARTMENTS = [
    "Customer Support",
    "Product Information", 
    "HR Department",
    "IT Support",
    "Shipping and Delivery",
    "Finance Department"
]
```
- List of valid departments for validation
- Used to check if LLM's department classification is valid

---

### **Node Functions**

#### **analyze_query (Lines 32-61)**
```python
def analyze_query(state: State) -> State:
    query = state["query"]
```
- First node in the graph - analyzes incoming queries
- Extracts user query from state

```python
    prompt = f"""Analyze this user query and determine:
1. Sentiment (positive, neutral, or negative)
2. Which department should handle it from this list: {', '.join(VALID_DEPARTMENTS)}

Query: {query}

Respond in this exact format:
Sentiment: [positive/neutral/negative]
Department: [exact department name from list or "unknown"]"""
```
- Creates a structured prompt for the LLM
- Asks for both sentiment analysis and department classification
- Specifies exact output format for easier parsing

```python
    response = llm.invoke(prompt)
    content = response.content
```
- Sends prompt to GPT-4o-mini
- Extracts text content from response object

```python
    sentiment = "neutral"
    department = "unknown"
    
    for line in content.split("\n"):
        if "Sentiment:" in line:
            sentiment = line.split(":")[-1].strip().lower()
        if "Department:" in line:
            dept = line.split(":")[-1].strip()
            if dept in VALID_DEPARTMENTS:
                department = dept
```
- **Parsing logic**: Extracts sentiment and department from LLM response
- Splits response by newlines, looks for keywords
- **Default values**: neutral sentiment, unknown department
- **Validation**: Only accepts departments from VALID_DEPARTMENTS list

```python
    print(f"Analysis - Sentiment: {sentiment}, Department: {department}")
    return {"sentiment": sentiment, "department": department}
```
- Logs the analysis results
- Returns dictionary that updates the state

---

#### **route_query (Lines 63-70)**
```python
def route_query(state: State) -> Literal["human_escalation", "rag_response"]:
    sentiment = state.get("sentiment", "neutral")
    department = state.get("department", "unknown")
```
- **Routing function**: Decides which node to go to next
- Uses `.get()` with defaults for safety
- **Literal return type**: Can only return these two specific strings

```python
    if sentiment == "negative" or department == "unknown":
        return "human_escalation"
    else:
        return "rag_response"
```
- **Routing logic**:
  - Negative sentiment → Human agent (customer is upset)
  - Unknown department → Human agent (can't categorize)
  - Otherwise → RAG response (can handle automatically)

---

#### **human_escalation (Lines 72-88)**
```python
def human_escalation(state: State) -> State:
    query = state["query"]
    sentiment = state.get("sentiment", "unknown")
```
- Handles cases that need human intervention
- Retrieves query and sentiment from state

```python
    response = f"""Thank you for contacting ShopUNow. 

We understand your concern and want to provide you with the best possible assistance. A human support agent from our team will review your query and call you back within 24 hours.

Your query has been logged and prioritized.

Reference ID: SU-{hash(query) % 100000:05d}

Is there anything else we can help you with?"""
```
- Creates professional escalation message
- **Reference ID**: Uses hash function to generate unique 5-digit ID
  - `hash(query)` creates integer from string
  - `% 100000` keeps it under 100,000
  - `:05d` formats as 5 digits with leading zeros

```python
    print(f"Routing to human escalation (Sentiment: {sentiment})")
    return {"response": response, "route": "human_escalation"}
```
- Logs the escalation
- Updates state with response and route tracking

---

#### **rag_response (Lines 90-120)**
```python
def rag_response(state: State) -> State:
    query = state["query"]
    department = state.get("department", "")
    
    print(f"Retrieving from RAG for department: {department}")
```
- Handles queries using RAG (Retrieval Augmented Generation)
- Gets query and department from state

```python
    results = vectorstore.similarity_search(
        query,
        k=3,
        filter={"department": department}
    )
```
- **Similarity search**: Finds most relevant documents
- **k=3**: Retrieves top 3 most similar documents
- **filter**: Only searches within specified department
- Uses cosine similarity on embeddings

```python
    context = "\n\n".join([
        f"Q: {doc.metadata['question']}\nA: {doc.metadata['answer']}"
        for doc in results
    ])
```
- Formats retrieved documents into context string
- Each document has metadata with original Q&A pairs
- Joins multiple results with double newlines

```python
    prompt = f"""You are a helpful assistant for ShopUNow's {department} department.

Based on the following knowledge base information, answer the user's query professionally and helpfully.

Knowledge Base:
{context}

User Query: {query}

Provide a clear, concise and helpful response. If the knowledge base doesn't contain enough information, say so politely."""
```
- Creates RAG prompt with retrieved context
- Instructs LLM to use knowledge base information
- Maintains professional tone

```python
    response = llm.invoke(prompt)
    return {"response": response.content, "route": f"rag_{department}"}
```
- Generates response using LLM with context
- Tracks which department handled the query

---

### **Graph Construction (Lines 122-139)**

```python
builder = StateGraph(State)
```
- Creates a new state graph with our State type

```python
builder.add_node("analyze", analyze_query)
builder.add_node("human_escalation", human_escalation)
builder.add_node("rag_response", rag_response)
```
- **Adds nodes**: Each node is a function that processes state
- Node names are strings, functions are the handlers

```python
builder.add_edge(START, "analyze")
```
- **Unconditional edge**: Always go from START to analyze node
- Every query begins with analysis

```python
builder.add_conditional_edges(
    "analyze",
    route_query,
    ["human_escalation", "rag_response"]
)
```
- **Conditional edge**: After analyze, call route_query function
- route_query returns either "human_escalation" or "rag_response"
- Graph follows the returned path

```python
builder.add_edge("human_escalation", END)
builder.add_edge("rag_response", END)
```
- Both paths end after generating response
- No loops - linear flow

```python
agent = builder.compile()
```
- **Compiles the graph**: Creates executable agent
- Validates all edges and nodes are properly connected

---

### **Helper Function (Lines 141-154)**

```python
def query_agent(user_query: str):
    print("="*80)
    print(f"User Query: {user_query}")
    print("-"*80)
```
- Wrapper function for cleaner testing
- Prints formatted output

```python
    result = agent.invoke({"query": user_query})
```
- **Invokes the agent**: Runs the entire graph
- Passes initial state with user query
- Returns final state after execution

```python
    print(f"\nRoute Taken: {result.get('route', 'unknown')}")
    print(f"\nResponse:")
    print(result["response"])
```
- Displays which path was taken
- Shows final response to user

---

### **Main Execution (Lines 156-189)**

```python
if __name__ == "__main__":
```
- Only runs if script is executed directly (not imported)

```python
    test_queries = [
        "How can I track my order?",
        "What is your return policy?",
        "I'm very angry, my package never arrived and customer service is terrible!",
        ...
    ]
```
- **Test cases** covering:
  - External customer queries (orders, returns, shipping)
  - Internal employee queries (HR, IT, finance)
  - Negative sentiment (angry customer)
  - Unknown topics (company history)

```python
    for query in test_queries:
        query_agent(query)
```
- Runs automated tests on all queries

```python
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'exit':
            print("Thank you for using ShopUNow Assistant!")
            break
        if user_input:
            query_agent(user_input)
```
- **Interactive mode**: Allows manual testing
- Loops until user types 'exit'
- `.strip()` removes whitespace

---

## KEY CONCEPTS TO EXPLAIN

### **1. What is RAG (Retrieval Augmented Generation)?**
- **Problem**: LLMs have limited knowledge and can hallucinate
- **Solution**: Retrieve relevant documents first, then generate response
- **Process**:
  1. Convert query to embedding
  2. Find similar documents in vector DB
  3. Pass documents as context to LLM
  4. LLM generates response based on context
- **Benefits**: Accurate, up-to-date, grounded in facts

### **2. What is LangGraph?**
- Framework for building **stateful, multi-step** AI applications
- Uses **graph structure** with nodes and edges
- **State** flows through the graph and gets updated
- Supports **conditional routing** based on state
- Better than simple chains for complex workflows

### **3. What is a Vector Database?**
- Stores **embeddings** (numerical representations of text)
- Enables **semantic search** (meaning-based, not keyword)
- **FAISS** is fast and efficient for similarity search
- Supports **metadata filtering** (by department)

### **4. Why Sentiment Analysis?**
- Detects **negative emotions** that need human touch
- Prevents AI from mishandling upset customers
- **Business value**: Better customer satisfaction

### **5. Why Department Routing?**
- **Specialization**: Each department has specific knowledge
- **Filtering**: Only searches relevant documents
- **Accuracy**: More precise answers

---

## COMMON MENTOR QUESTIONS & ANSWERS

### **Q: Why did you use LangGraph instead of LangChain?**
**A**: LangGraph is better for complex routing logic. LangChain chains are linear, but we needed conditional branching based on sentiment and department. LangGraph's state machine approach makes this cleaner and more maintainable.

### **Q: How does the vector database filtering work?**
**A**: Each document in FAISS has metadata including the department. When we call `similarity_search()` with a filter, FAISS only compares embeddings from documents matching that department. This makes retrieval more accurate and faster.

### **Q: What happens if the LLM misclassifies the department?**
**A**: We validate against VALID_DEPARTMENTS list. If the LLM returns an invalid department, we set it to "unknown" which triggers human escalation. This prevents errors from propagating.

### **Q: Why temperature=0.3?**
**A**: We want consistent, predictable responses for a customer service system. Lower temperature (0-0.5) reduces randomness. We use 0.3 instead of 0 to allow slight variation in phrasing while maintaining consistency.

### **Q: How would you scale this system?**
**A**: 
1. Add more departments and QA pairs
2. Use a production vector DB (Pinecone, Weaviate)
3. Add conversation memory for multi-turn dialogues
4. Implement feedback loop to improve responses
5. Add monitoring and logging
6. Deploy as API with FastAPI

### **Q: What's the difference between this and a simple chatbot?**
**A**: 
- **Routing intelligence**: Decides between AI and human
- **RAG**: Grounds responses in actual company data
- **Department specialization**: Targeted knowledge retrieval
- **Sentiment awareness**: Handles emotions appropriately
- **Stateful**: Can track conversation flow

### **Q: Why use hash for reference ID?**
**A**: Hash function converts any string to a consistent integer. Same query always gets same ID. Modulo 100000 keeps it 5 digits. Simple but effective for tracking without a database.

### **Q: What are the limitations of this system?**
**A**:
1. No conversation memory (each query is independent)
2. Simple sentiment analysis (could use specialized models)
3. No multi-language support
4. Limited error handling
5. No user authentication
6. Static knowledge base (needs manual updates)

### **Q: How do embeddings work?**
**A**: Text is converted to a vector (list of numbers) that captures semantic meaning. Similar meanings have similar vectors. We use cosine similarity to find closest matches. OpenAI's embedding model has 1536 dimensions.

### **Q: What's the stretch goal you implemented?**
**A**: Option 3 - Added 6 departments instead of 4, with diverse workflows covering both internal (HR, IT, Finance) and external (Customer Support, Product Info, Shipping) use cases.

---

## GRAPH FLOW DIAGRAM

```
START
  ↓
analyze_query
  ↓
route_query (decision)
  ↓
  ├─→ [negative OR unknown] → human_escalation → END
  └─→ [positive/neutral AND valid dept] → rag_response → END
```

---

## FILE 2: generate_qa_data.py - Quick Explanation

```python
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```
- Uses OpenAI API directly (not LangChain wrapper)

```python
departments = {
    "Customer Support": {
        "description": "...",
        "type": "external",
        "num_qa": 15
    },
    ...
}
```
- Dictionary defining each department's characteristics
- **type**: external (customers) or internal (employees)
- **num_qa**: How many Q&A pairs to generate

```python
for dept_name, dept_info in departments.items():
    prompt = f"""Generate {dept_info['num_qa']} question-answer pairs..."""
    response = client.chat.completions.create(...)
    qa_pairs = json.loads(response.choices[0].message.content)
```
- Loops through each department
- Uses LLM to generate synthetic QA data
- Parses JSON response into Python objects

```python
with open("qa_datasets.json", "w") as f:
    json.dump(all_qa_data, f, indent=2)
```
- Saves all QA pairs to JSON file
- Used by next script to build vector database

---

## FILE 3: build_vectordb.py - Quick Explanation

```python
with open("qa_datasets.json", "r") as f:
    qa_data = json.load(f)
```
- Loads the generated QA pairs

```python
for dept_name, dept_data in qa_data.items():
    for qa_pair in dept_data["qa_pairs"]:
        doc_text = f"Question: {qa_pair['question']}\nAnswer: {qa_pair['answer']}"
        metadata = {
            "department": dept_name,
            "type": dept_data["type"],
            "question": qa_pair["question"],
            "answer": qa_pair["answer"]
        }
        doc = Document(page_content=doc_text, metadata=metadata)
        all_documents.append(doc)
```
- Converts each QA pair into a LangChain Document
- **page_content**: The text to embed
- **metadata**: Searchable attributes (department, type, etc.)

```python
vectorstore = FAISS.from_documents(all_documents, embeddings)
vectorstore.save_local("shopunow_vectordb")
```
- Creates FAISS index from all documents
- Generates embeddings for each document
- Saves to disk for later use

---

## TESTING STRATEGY

The test queries cover:
1. **Happy path**: Normal questions with clear departments
2. **Negative sentiment**: Angry customer → human escalation
3. **Unknown topic**: Company history → human escalation
4. **Internal vs External**: Both employee and customer queries
5. **All departments**: At least one query per department

---

## PROJECT REQUIREMENTS MET

✅ **4+ departments** (we have 6)
✅ **2+ internal, 2+ external** (3 internal, 3 external)
✅ **10-15 QA pairs per department** (12-15 each)
✅ **Vector database with metadata** (FAISS with department filtering)
✅ **Sentiment analysis** (positive/neutral/negative)
✅ **Routing logic** (conditional edges in LangGraph)
✅ **Human escalation** (for negative/unknown)
✅ **RAG responses** (retrieval + generation)
✅ **Stretch Goal Option 3** (more departments and routes)
✅ **Testing** (10 diverse test queries)

---

## TIPS FOR THE MEETING

1. **Be confident**: You built a real production-ready system
2. **Explain the "why"**: Not just what the code does, but why you made those choices
3. **Know the flow**: Be able to trace a query through the entire system
4. **Admit limitations**: Shows you understand real-world constraints
5. **Discuss improvements**: Shows forward thinking
6. **Use correct terminology**: RAG, embeddings, vector database, sentiment analysis, routing
7. **Connect to business value**: Better customer satisfaction, reduced support costs, scalability

Good luck with your meeting! 🚀
