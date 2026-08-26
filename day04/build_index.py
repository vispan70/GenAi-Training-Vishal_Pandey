import os
import requests

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()


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

        return [item["embedding"] for item in data["data"]]

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


load_dotenv()


# 1. Load documents
docs = DirectoryLoader(
    "kb",
    glob="*.txt",
    loader_cls=TextLoader
).load()


# 2. Split documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=50
)

chunks = splitter.split_documents(docs)


# 3. Create OpenRouter embeddings
embeddings = OpenRouterEmbeddings()


# 4. Store embeddings in ChromaDB
db = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory="chroma_db"
)


print(f"Indexed {len(chunks)} chunks from {len(docs)} documents.")
