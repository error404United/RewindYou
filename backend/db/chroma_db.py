import chromadb
from dotenv import load_dotenv
import os
import chromadb

# Load environment variables from .env
load_dotenv("backend/.env")

# Read values
api_key = os.getenv("CHROMA_API_KEY") 
tenant = os.getenv("CHROMA_TENANT")
database = os.getenv("CHROMA_DATABASE")

client = chromadb.CloudClient(
  api_key=api_key,
  tenant=tenant,
  database=database
)
collection = client.get_or_create_collection(
    name="rewindyou_memory"
)
collection.add(
    documents=[
        "RewindYou stores personal and read blah blah web memories",
        "Chroma is a vector database for AI applications and storing of vectors",
        "Semantic search helps retrieve past relevant memories"
    ],
    ids=["doc4", "doc5", "doc6"]
)
query_texts=["AI memory system"]
results = collection.query(
    query_texts=query_texts,
    n_results=2
)
print("Query:",query_texts)
print("\n🔎 Query Results:")
for i, doc in enumerate(results["documents"][0], start=4):
    print(f"{i}. {doc}")