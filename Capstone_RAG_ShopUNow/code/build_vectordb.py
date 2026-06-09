import json
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()

with open("qa_datasets.json", "r") as f:
    qa_data = json.load(f)

embeddings = OpenAIEmbeddings()

all_documents = []

for dept_name, dept_data in qa_data.items():
    print(f"Processing {dept_name}...")
    
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

print(f"\nCreating vector database with {len(all_documents)} documents...")

vectorstore = FAISS.from_documents(all_documents, embeddings)

vectorstore.save_local("shopunow_vectordb")

print("Vector database created and saved to 'shopunow_vectordb'")

test_query = "How do I return a product?"
results = vectorstore.similarity_search(test_query, k=3)
print(f"\nTest query: '{test_query}'")
print(f"Top result department: {results[0].metadata['department']}")
