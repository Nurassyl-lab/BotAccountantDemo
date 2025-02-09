import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os, sys

load_dotenv()

# Connect to Railway PostgreSQL
DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL")

# Initialize embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Sample documents
documents = [
    "The sky is blue and the sun is shining.",
    "Cats are small, carnivorous mammals.",
    "Artificial intelligence is transforming industries.",
    "The stock market fluctuates daily.",
    "Climate change affects global temperatures.",
    "Football is a popular sport worldwide.",
    "Python is a widely-used programming language.",
    "Cooking requires patience and skill.",
    "Traveling broadens one's perspective.",
    "Music has a profound impact on emotions."
]

# Generate embeddings
embeddings = [model.encode(doc).tolist() for doc in documents]

# Connect to PostgreSQL and setup table
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Enable pgvector
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

# Create table with vector column
cur.execute("""
    CREATE TABLE IF NOT EXISTS document_vectors (
        id SERIAL PRIMARY KEY,
        doc TEXT,
        embedding vector(384) -- Adjust dimension based on model output
    );
""")

# Insert document embeddings
for doc, emb in zip(documents, embeddings):
    cur.execute("INSERT INTO document_vectors (doc, embedding) VALUES (%s, %s)", (doc, emb))

conn.commit()

# Querying
query = "Tell me about programming languages."
query_embedding = model.encode(query).tolist()

# Find top 3 similar documents
cur.execute("""
    SELECT doc, 1 - (embedding <=> %s) AS similarity 
    FROM document_vectors 
    ORDER BY similarity DESC 
    LIMIT 3;
""", (query_embedding,))

# Fetch and display results
results = cur.fetchall()
print("\nTop 3 Similar Documents:")
for doc, sim in results:
    print(f"- {doc} (Similarity: {sim:.4f})")

# Cleanup
cur.close()
conn.close()

