from fastapi import FastAPI, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
import openai
from twilio.rest import Client
from dotenv import load_dotenv
import os

import pinecone
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import json
import numpy as np

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# Initialize OpenAI, Pinecone, and Twilio API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"))

twilio_sid = os.getenv("TWILIO_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

# PostgreSQL connection string from Railway
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

Base = declarative_base()
Session = sessionmaker(bind=engine)

client = Client(twilio_sid, twilio_auth_token)

# Define Document model for PostgreSQL
class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # Store embeddings as a string for simplicity

# Create the table if not exists
Base.metadata.create_all(engine) # -- comment

# Initialize Pinecone index (replace with your index name)
index_name = "document-index"
index = pinecone.Index(index_name)

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


@app.post("/whatsapp")
async def whatsapp_bot(request: dict):
    incoming_message = request.get("Body", "").strip().lower()

    # Process message with GPT-4 (Chat Model)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # You can use gpt-4 or gpt-3.5-turbo
            messages=[{"role": "user", "content": incoming_message}],
            max_tokens=100
        )
        message = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        raise HTTPException(status_code=500, detail="Error in processing the message with OpenAI")

    # Respond via Twilio
    try:
        resp = MessagingResponse()
        resp.message(message)
        return str(resp)
    except Exception as e:
        print(f"Twilio error: {e}")
        raise HTTPException(status_code=500, detail="Error in sending message via Twilio")

