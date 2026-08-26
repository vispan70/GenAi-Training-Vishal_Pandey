import os
import requests

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

load_dotenv()

# Get model from .env
MODEL = os.getenv("MODEL")


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


# ============================================================
# 2. OpenRouter LLM
# ============================================================

def ask_llm(prompt):

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing from your .env file"
        )

    url = "https://openrouter.ai/api/v1/chat/completions"

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


# ============================================================
# 3. Load persisted Chroma database
# ============================================================

embeddings = OpenRouterEmbeddings()

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)


# ============================================================
# 4. Create retriever
# ============================================================

retriever = db.as_retriever(
    search_kwargs={"k": 3}
)


# ============================================================
# 5. Grounded RAG function
# ============================================================

def answer_question(question):

    # Retrieve top 3 relevant chunks
    docs = retriever.invoke(question)

    print("\n" + "=" * 70)
    print("RETRIEVED SOURCES")
    print("=" * 70)

    for i, doc in enumerate(docs, start=1):

        source = doc.metadata.get("source", "unknown")

        # Only show filename instead of complete path
        source = os.path.basename(source)

        print(f"{i}. {source}")

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context_parts = []

    for doc in docs:

        source = doc.metadata.get("source", "unknown")
        source = os.path.basename(source)

        context_parts.append(
            f"[Source: {source}]\n{doc.page_content}"
        )

    context = "\n\n".join(context_parts)

    # --------------------------------------------------------
    # Grounded prompt
    # --------------------------------------------------------

    prompt = f"""
You are a banking knowledge-base assistant.

Answer the user's question ONLY using the provided context.

Rules:

1. Use ONLY the information contained in the context.
2. Do NOT use outside knowledge.
3. Do NOT guess or invent information.
4. Every factual statement must include the source filename
   in square brackets after the statement.
5. If the context does not contain the answer, reply EXACTLY:

I don't have that information in my knowledge base — let me connect you to a human agent.

CONTEXT:

{context}

USER QUESTION:

{question}
"""

    # --------------------------------------------------------
    # Generate answer
    # --------------------------------------------------------

    answer = ask_llm(prompt)

    print("\n" + "=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)
    print(answer)

    return answer


# ============================================================
# 6. Interactive question loop
# ============================================================

print("\nRAG Knowledge Base Assistant")
print("Type 'exit' to stop.\n")

while True:

    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if not question:
        continue

    answer_question(question)
