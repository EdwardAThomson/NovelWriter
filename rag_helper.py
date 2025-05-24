# rag_helper.py
import chromadb
# from chromadb.config import Settings
from openai import OpenAI
import uuid

working_directory = "current_work/"
client = chromadb.PersistentClient(path=working_directory+"db")  # Use PersistentClient for disk storage
client_oai = OpenAI() # for embeddings

# lore_collection = client.get_or_create_collection("lore_collection")

# Define collections
collections = {
    "lore": client.get_or_create_collection("lore_collection"),
    "characters": client.get_or_create_collection("character_collection"),
    "world": client.get_or_create_collection("world_collection"),
}

def get_collection(name):
    """Retrieve a ChromaDB collection by name."""
    if name in collections:
        return collections[name]
    else:
        raise ValueError(f"Collection '{name}' not found.")


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

# def upsert_lore_text(doc_id, text, metadata=None):
#     if metadata is None:
#         metadata = {}
#
#     # Add source document ID to metadata (useful for retrieval)
#     metadata["source"] = doc_id
#
#     # First, delete previous lore data
#     lore_collection.delete(where={"source": doc_id})  # Delete all old entries for this piece of lore
#
#     chunks = chunk_text(text, max_tokens=300)
#     for c in chunks:
#         c_embedding = embed_text(c)
#         chunk_id = str(uuid.uuid4())
#         lore_collection.upsert(
#             documents=[c],
#             embeddings=[c_embedding],
#             ids=[chunk_id],
#             metadatas=[metadata]
#         )

# def retrieve_relevant_lore(query, k=5):
#     query_embedding = embed_text(query)
#     results = lore_collection.query(
#         query_embeddings=[query_embedding],
#         n_results=k
#     )
#     # Flatten the top results
#     relevant_texts = results["documents"][0] if "documents" in results else []
#     return relevant_texts


def upsert_text(collection_name, doc_id, text, metadata=None, chunk_size=300):
    """
    Upserts text into a given ChromaDB collection with chunking and embeddings.

    :param collection_name: The name of the ChromaDB collection.
    :param doc_id: Unique document identifier.
    :param text: The text content to be stored.
    :param metadata: Additional metadata (default is None).
    :param chunk_size: Max tokens per chunk (default is 300).
    """
    collection = get_collection(collection_name)  # Fetch the correct collection

    if metadata is None:
        metadata = {}

    metadata["source"] = doc_id
    collection.delete(where={"source": doc_id})  # Remove old data

    chunks = chunk_text(text, max_tokens=chunk_size)  # Break text into chunks
    for c in chunks:
        c_embedding = embed_text(c)  # Generate embeddings
        chunk_id = str(uuid.uuid4())  # Generate a unique ID for the chunk

        collection.upsert(
            documents=[c],
            embeddings=[c_embedding],
            ids=[chunk_id],
            metadatas=[metadata]
        )

    print(f"✅ Upserted {len(chunks)} chunks into '{collection.name}' for doc_id '{doc_id}'")




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