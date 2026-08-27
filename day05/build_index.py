import os
import requests

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# 1. OpenRouter Embeddings
# ============================================================

class OpenRouterEmbeddings(Embeddings):

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = "liquid/lfm-2.5-embedding-350m:free"
        self.url = "https://openrouter.ai/api/v1/embeddings"

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is missing from your .env file"
            )

    def embed_documents(self, texts):

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": texts,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return [
            item["embedding"]
            for item in data["data"]
        ]

    def embed_query(self, text):

        response = requests.post(
            self.url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": [text],
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data["data"][0]["embedding"]


# ============================================================
# 2. Load Day 5 Knowledge Base
# ============================================================

docs = DirectoryLoader(
    "kb",
    glob="*.txt",
    loader_cls=TextLoader
).load()

print(f"Loaded {len(docs)} documents.")


# ============================================================
# 3. Split Documents into Chunks
# ============================================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(docs)

print(f"Created {len(chunks)} chunks.")


# ============================================================
# 4. Create OpenRouter Embeddings
# ============================================================

embeddings = OpenRouterEmbeddings()


# ============================================================
# 5. Store Chunks + Embeddings in Day 5 ChromaDB
# ============================================================

db = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory="chroma_db"
)


# ============================================================
# 6. Final Summary
# ============================================================

print(
    f"Indexed {len(chunks)} chunks "
    f"from {len(docs)} documents."
)

print("ChromaDB created successfully in day05/chroma_db")
