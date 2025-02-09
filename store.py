import os
import openai
from pinecone import Pinecone, ServerlessSpec
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Set up OpenAI API key and Pinecone API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# pinecone.init(api_key=os.getenv("PINECONE_API_KEY"))

pc = Pinecone(
api_key=os.environ.get("PINECONE_API_KEY")
)

# PostgreSQL connection string from Railway (replace with actual values)
DATABASE_URL = os.getenv("DATABASE_URL")  # Railway provides this as an env variable
engine = create_engine(DATABASE_URL)

Base = declarative_base()
Session = sessionmaker(bind=engine)

# Define Document model for PostgreSQL
class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # Store embeddings as a string for simplicity

# Create the table if not exists
Base.metadata.create_all(engine)

import json
import numpy as np

# Initialize Pinecone index (replace with your index name)
index_name = "document-index"
if index_name not in pc.list_indexes().names():
    index = pc.create_index(
        name=index_name,
        dimension=100,
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-west-2'
        )
    )


def embed_document(content):
    response = openai.Embedding.create(
        model="text-embedding-ada-002", 
        input=content
    )
    return response['data'][0]['embedding']

def store_document(doc_content):
    # Embed document content
    embedding = embed_document(doc_content)
    
    # Store in PostgreSQL
    session = Session()
    new_doc = Document(content=doc_content, embedding=json.dumps(embedding))  # Store embedding as JSON
    session.add(new_doc)
    session.commit()

    # Store in Pinecone
    doc_id = str(new_doc.id)
    index.upsert([(doc_id, embedding, {'content': doc_content})])

    session.close()

# Example of storing a document
doc_content = "This is a sample document."
store_document(doc_content)

def retrieve_top_k_documents(query, k=5):
    # Embed the query
    query_embedding = embed_document(query)

    # Perform similarity search in Pinecone
    results = index.query(query_embedding, top_k=k, include_metadata=True)
    
    # Extract document IDs from the results
    doc_ids = [match['id'] for match in results['matches']]

    # Retrieve full document content from PostgreSQL
    session = Session()
    docs = session.query(Document).filter(Document.id.in_(doc_ids)).all()
    session.close()

    return docs

