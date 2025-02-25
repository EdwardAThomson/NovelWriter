# rag_helper.py
import chromadb
# from chromadb.config import Settings
from openai import OpenAI
import uuid

working_directory = "current_work/"
client = chromadb.PersistentClient(path=working_directory+"db")  # Use PersistentClient for disk storage

client_oai = OpenAI()

# client = chromadb.Client(Settings(
#     chroma_db_impl="duckdb+parquet",
#     persist_directory="db"  # or any folder path
# ))

lore_collection = client.get_or_create_collection("lore_collection")

def chunk_text(text, max_tokens=300, overlap=50):
    tokens = text.split()  # Simple whitespace tokenization
    chunks = []
    for i in range(0, len(tokens), max_tokens - overlap):  # Sliding window approach
        chunk = tokens[i : i + max_tokens]
        chunks.append(" ".join(chunk))
    return chunks



def embed_text(text):
    # response = openai.Embedding.create(
    response = client_oai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding #  response["data"][0]["embedding"]


def upsert_lore_text(doc_id, text, metadata=None):
    if metadata is None:
        metadata = {}

    # First, delete previous lore data
    lore_collection.delete(where={"source": doc_id})  # Delete all old entries for this piece of lore

    chunks = chunk_text(text, max_tokens=300)
    for c in chunks:
        c_embedding = embed_text(c)
        chunk_id = str(uuid.uuid4())
        lore_collection.upsert(
            documents=[c],
            embeddings=[c_embedding],
            ids=[chunk_id],
            metadatas=[metadata]
        )

def retrieve_relevant_lore(query, k=5):
    query_embedding = embed_text(query)
    results = lore_collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    # Flatten the top results
    relevant_texts = results["documents"][0] if "documents" in results else []
    return relevant_texts


# Example if we are retrieving from multiple collections
# def retrieve_relevant_context(user_query, k=5):
#     query_embedding = embed_text(user_query)
#
#     # Retrieve from each collection
#     lore_results = lore_collection.query(query_embeddings=[query_embedding], n_results=k)
#     structure_results = structure_collection.query(query_embeddings=[query_embedding], n_results=k)
#     story_results = story_collection.query(query_embeddings=[query_embedding], n_results=k)
#
#     # Combine the results
#     relevant_lore = lore_results["documents"][0] if "documents" in lore_results else []
#     relevant_structure = structure_results["documents"][0] if "documents" in structure_results else []
#     relevant_story = story_results["documents"][0] if "documents" in story_results else []
#
#     # Merge them into a single prompt context
#     retrieved_text = "\n\n".join(relevant_lore + relevant_structure + relevant_story)
#
#     return retrieved_text