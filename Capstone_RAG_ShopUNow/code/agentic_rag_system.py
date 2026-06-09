from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from dotenv import load_dotenv
import os

load_dotenv()

class State(TypedDict):
    query: str
    sentiment: str
    department: str
    response: str
    route: str

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local("shopunow_vectordb", embeddings, allow_dangerous_deserialization=True)

VALID_DEPARTMENTS = [
    "Customer Support",
    "Product Information", 
    "HR Department",
    "IT Support",
    "Shipping and Delivery",
    "Finance Department"
]

def analyze_query(state: State) -> State:
    query = state["query"]
    
    prompt = f"""Analyze this user query and determine:
1. Sentiment (positive, neutral, or negative)
2. Which department should handle it from this list: {', '.join(VALID_DEPARTMENTS)}

Query: {query}

Respond in this exact format:
Sentiment: [positive/neutral/negative]
Department: [exact department name from list or "unknown"]"""

    response = llm.invoke(prompt)
    content = response.content
    
    sentiment = "neutral"
    department = "unknown"
    
    for line in content.split("\n"):
        if "Sentiment:" in line:
            sentiment = line.split(":")[-1].strip().lower()
        if "Department:" in line:
            dept = line.split(":")[-1].strip()
            if dept in VALID_DEPARTMENTS:
                department = dept
    
    print(f"Analysis - Sentiment: {sentiment}, Department: {department}")
    
    return {"sentiment": sentiment, "department": department}

def route_query(state: State) -> Literal["human_escalation", "rag_response"]:
    sentiment = state.get("sentiment", "neutral")
    department = state.get("department", "unknown")
    
    if sentiment == "negative" or department == "unknown":
        return "human_escalation"
    else:
        return "rag_response"

def human_escalation(state: State) -> State:
    query = state["query"]
    sentiment = state.get("sentiment", "unknown")
    
    response = f"""Thank you for contacting ShopUNow. 

We understand your concern and want to provide you with the best possible assistance. A human support agent from our team will review your query and call you back within 24 hours.

Your query has been logged and prioritized.

Reference ID: SU-{hash(query) % 100000:05d}

Is there anything else we can help you with?"""
    
    print(f"Routing to human escalation (Sentiment: {sentiment})")
    
    return {"response": response, "route": "human_escalation"}

def rag_response(state: State) -> State:
    query = state["query"]
    department = state.get("department", "")
    
    print(f"Retrieving from RAG for department: {department}")
    
    results = vectorstore.similarity_search(
        query,
        k=3,
        filter={"department": department}
    )
    
    context = "\n\n".join([
        f"Q: {doc.metadata['question']}\nA: {doc.metadata['answer']}"
        for doc in results
    ])
    
    prompt = f"""You are a helpful assistant for ShopUNow's {department} department.

Based on the following knowledge base information, answer the user's query professionally and helpfully.

Knowledge Base:
{context}

User Query: {query}

Provide a clear, concise and helpful response. If the knowledge base doesn't contain enough information, say so politely."""

    response = llm.invoke(prompt)
    
    return {"response": response.content, "route": f"rag_{department}"}

builder = StateGraph(State)

builder.add_node("analyze", analyze_query)
builder.add_node("human_escalation", human_escalation)
builder.add_node("rag_response", rag_response)

builder.add_edge(START, "analyze")

builder.add_conditional_edges(
    "analyze",
    route_query,
    ["human_escalation", "rag_response"]
)

builder.add_edge("human_escalation", END)
builder.add_edge("rag_response", END)

agent = builder.compile()

def query_agent(user_query: str):
    print("="*80)
    print(f"User Query: {user_query}")
    print("-"*80)
    
    result = agent.invoke({"query": user_query})
    
    print(f"\nRoute Taken: {result.get('route', 'unknown')}")
    print(f"\nResponse:")
    print(result["response"])
    print("="*80)
    print()
    
    return result

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SHOPUNOW AGENTIC RAG SYSTEM")
    print("="*80)
    print("Enter your queries (type 'exit' to quit):\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'exit':
            print("Thank you for using ShopUNow Assistant!")
            break
        if user_input:
            query_agent(user_input)
