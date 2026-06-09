from openai import OpenAI
import json
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

departments = {
    "Customer Support": {
        "description": "Handles external customer queries about orders, returns, refunds and general product inquiries",
        "type": "external",
        "num_qa": 15
    },
    "Product Information": {
        "description": "Provides detailed information about products, specifications, availability and recommendations to external customers",
        "type": "external", 
        "num_qa": 15
    },
    "HR Department": {
        "description": "Manages internal employee queries about benefits, leave policies, payroll and workplace policies",
        "type": "internal",
        "num_qa": 15
    },
    "IT Support": {
        "description": "Assists internal employees with technical issues, software access, hardware problems and system troubleshooting",
        "type": "internal",
        "num_qa": 15
    },
    "Shipping and Delivery": {
        "description": "Handles external customer questions about shipping status, delivery times, tracking and shipping costs",
        "type": "external",
        "num_qa": 12
    },
    "Finance Department": {
        "description": "Manages internal employee queries about expense reimbursements, budgets and financial procedures",
        "type": "internal",
        "num_qa": 12
    }
}

all_qa_data = {}

for dept_name, dept_info in departments.items():
    print(f"Generating QA pairs for {dept_name}...")
    
    prompt = f"""You are creating a FAQ dataset for the {dept_name} department at ShopUNow, an e-commerce company.

Department Description: {dept_info['description']}
User Type: {dept_info['type']} ({'customers' if dept_info['type'] == 'external' else 'employees'})

Generate {dept_info['num_qa']} question-answer pairs that would be frequently asked by {'customers' if dept_info['type'] == 'external' else 'employees'}.

Format your response as a JSON array with this structure:
[
    {{"question": "...", "answer": "..."}},
    {{"question": "...", "answer": "..."}}
]

Make the questions realistic and diverse. Answers should be helpful and professional."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates realistic FAQ data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content
        content = content.rsplit("```", 1)[0]
        if content.lstrip().startswith("json"):
            content = content.lstrip()[4:]
    qa_pairs = json.loads(content.strip())
    all_qa_data[dept_name] = {
        "description": dept_info['description'],
        "type": dept_info['type'],
        "qa_pairs": qa_pairs
    }
    
    print(f"Generated {len(qa_pairs)} QA pairs for {dept_name}")

with open("qa_datasets.json", "w") as f:
    json.dump(all_qa_data, f, indent=2)

print("\nAll QA datasets saved to qa_datasets.json")
print(f"Total departments: {len(all_qa_data)}")
for dept, data in all_qa_data.items():
    print(f"  - {dept}: {len(data['qa_pairs'])} QA pairs ({data['type']})")
