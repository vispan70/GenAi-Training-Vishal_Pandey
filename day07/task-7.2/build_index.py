import os
import requests

from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma


# ============================================================
# 1. Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent

KB_DIR = BASE_DIR / "kb"
CHROMA_DIR = BASE_DIR / "chroma_db"
ENV_PATH = ROOT_DIR / ".env"


# ============================================================
# 2. Load Environment Variables
# ============================================================

load_dotenv(ENV_PATH)


# ============================================================
# 3. OpenRouter Embeddings
# ============================================================

class OpenRouterEmbeddings(Embeddings):

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = "liquid/lfm-2.5-embedding-350m:free"
        self.url = "https://openrouter.ai/api/v1/embeddings"

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is missing from your root .env file"
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
# 4. Load Knowledge Base
# ============================================================

docs = DirectoryLoader(
    str(KB_DIR),
    glob="*.txt",
    loader_cls=TextLoader
).load()

print(f"Loaded {len(docs)} documents.")


# ============================================================
# 5. Split Documents
# ============================================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(docs)

print(f"Created {len(chunks)} chunks.")


# ============================================================
# 6. Create ChromaDB
# ============================================================

embeddings = OpenRouterEmbeddings()

db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(CHROMA_DIR)
)


# ============================================================
# 7. Summary
# ============================================================

print(
    f"Indexed {len(chunks)} chunks "
    f"from {len(docs)} documents."
)

print(f"ChromaDB created successfully at: {CHROMA_DIR}")
