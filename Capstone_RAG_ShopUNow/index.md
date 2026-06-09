---
layout: default
title: ShopUNow Agentic RAG System
---
 
[← Back to portfolio](../)
 
# ShopUNow Agentic RAG System
 
A router-based agentic RAG (Retrieval-Augmented Generation) system for an e-commerce platform. It analyzes incoming customer and employee queries, detects sentiment, routes them to the right department, and either answers from a knowledge base or escalates to a human.
 
## How it works
 
User query → query analysis → routing decision → **either** human escalation **or** a RAG-grounded answer → final response.
 
## Highlights
 
- Sentiment detection that escalates upset customers to a human agent
- Routing across 6 departments (3 customer-facing, 3 internal)
- 84 QA pairs stored in a FAISS vector database with department filtering
- Human-escalation flow that issues reference IDs
**Tech:** LangGraph, FAISS, OpenAI (GPT-4o-mini + embeddings), Python
 
[View the code on GitHub »](https://github.com/Skyblockforlige/koolhere/tree/main/Capstone_RAG_ShopUNow)
