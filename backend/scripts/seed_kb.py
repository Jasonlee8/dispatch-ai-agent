# scripts/seed_kb.py

import os
import sys
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.infrastructure.mongo import get_db

load_dotenv()

client = OpenAI()

def main():
    db = get_db()
    kb = db["kb_chunks"]

    documents = [
        {
            "company_id": "demo_company",
            "text": "Our business hours are Monday to Friday, 9am to 6pm.",
            "tags": ["hours", "business hours"],
        },
        {
            "company_id": "demo_company",
            "text": "We charge $120 for the first hour of plumbing work and $80 for each additional hour.",
            "tags": ["pricing", "plumber", "cost"],
        },
        {
            "company_id": "demo_company",
            "text": "Emergency plumbing services are available 24/7 with an additional $150 callout fee.",
            "tags": ["emergency", "pricing"],
        },
        {
            "company_id": "demo_company",
            "text": "We service Melbourne CBD and nearby suburbs including Carlton, Fitzroy, Docklands, and Southbank.",
            "tags": ["service area"],
        },
        {
            "company_id": "demo_company",
            "text": "You can cancel or reschedule appointments up to 24 hours before the booking time.",
            "tags": ["policy", "cancel"],
        },
    ]

    print("Generating embeddings for KB...")

    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=[d["text"] for d in documents],
    )

    for doc, emb in zip(documents, resp.data):
        doc["embedding"] = emb.embedding

    kb.delete_many({"company_id": "demo_company"})
    kb.insert_many(documents)

    print("Inserted KB docs:", len(documents))
    print("Done.")

if __name__ == "__main__":
    main()
