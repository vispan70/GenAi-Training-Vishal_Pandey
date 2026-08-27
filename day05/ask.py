# import os
# import json
# import requests

# from dotenv import load_dotenv
# from langchain_chroma import Chroma
# from langchain_core.embeddings import Embeddings

# load_dotenv()

# # Get model from .env
# MODEL = os.getenv("MODEL")


# # ============================================================
# # 1. OpenRouter Embeddings
# # ============================================================

# class OpenRouterEmbeddings(Embeddings):

#     def __init__(self):
#         self.api_key = os.getenv("OPENROUTER_API_KEY")
#         self.model = "liquid/lfm-2.5-embedding-350m:free"
#         self.url = "https://openrouter.ai/api/v1/embeddings"

#         if not self.api_key:
#             raise ValueError(
#                 "OPENROUTER_API_KEY is missing from your .env file"
#             )

#     def embed_documents(self, texts):
#         response = requests.post(
#             self.url,
#             headers={
#                 "Authorization": f"Bearer {self.api_key}",
#                 "Content-Type": "application/json",
#             },
#             json={
#                 "model": self.model,
#                 "input": texts,
#             },
#             timeout=120,
#         )

#         response.raise_for_status()

#         data = response.json()

#         return [item["embedding"] for item in data["data"]]

#     def embed_query(self, text):
#         response = requests.post(
#             self.url,
#             headers={
#                 "Authorization": f"Bearer {self.api_key}",
#                 "Content-Type": "application/json",
#             },
#             json={
#                 "model": self.model,
#                 "input": [text],
#             },
#             timeout=120,
#         )

#         response.raise_for_status()

#         data = response.json()

#         return data["data"][0]["embedding"]


# # ============================================================
# # 2. OpenRouter LLM
# # ============================================================

# def ask_llm(prompt):

#     api_key = os.getenv("OPENROUTER_API_KEY")

#     if not api_key:
#         raise ValueError(
#             "OPENROUTER_API_KEY is missing from your .env file"
#         )

#     url = "https://openrouter.ai/api/v1/chat/completions"

#     response = requests.post(
#         url,
#         headers={
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json",
#         },
#         json={
#             "model": MODEL,
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 }
#             ],
#             "temperature": 0,
#         },
#         timeout=120,
#     )

#     response.raise_for_status()

#     data = response.json()

#     return data["choices"][0]["message"]["content"]


# # ============================================================
# # 3. Load persisted Chroma database
# # ============================================================

# embeddings = OpenRouterEmbeddings()

# db = Chroma(
#     persist_directory="chroma_db",
#     embedding_function=embeddings
# )


# # ============================================================
# # 4. Multi-Query Generation
# # ============================================================

# def generate_queries(question):

#     prompt = f"""
# You are a query-generation component for a banking knowledge-base
# retrieval system.

# Generate exactly THREE differently-worded versions of the user's
# question.

# The purpose is to improve document retrieval.

# Do NOT answer the question.

# Return ONLY valid JSON in this exact format:

# [
#   "query 1",
#   "query 2",
#   "query 3"
# ]

# Rules:

# 1. Return exactly 3 queries.
# 2. Each query must have the same meaning as the original question.
# 3. Use different wording for each query.
# 4. Do not add information that is not present in the original question.
# 5. Do not answer the question.
# 6. Return JSON only.
# 7. Do not use Markdown code fences.

# USER QUESTION:

# {question}
# """

#     raw_response = ask_llm(prompt).strip()

#     # Handle accidental Markdown code fences
#     if raw_response.startswith("```"):
#         raw_response = raw_response.replace("```json", "")
#         raw_response = raw_response.replace("```", "")
#         raw_response = raw_response.strip()

#     try:
#         queries = json.loads(raw_response)
#     except json.JSONDecodeError as e:
#         raise ValueError(
#             f"LLM did not return valid JSON for query generation.\n"
#             f"Raw response:\n{raw_response}"
#         ) from e

#     if not isinstance(queries, list):
#         raise ValueError("Query generation response is not a JSON list.")

#     if len(queries) != 3:
#         raise ValueError(
#             f"Expected exactly 3 queries, but received {len(queries)}."
#         )

#     if not all(isinstance(q, str) and q.strip() for q in queries):
#         raise ValueError("All generated queries must be non-empty strings.")

#     return [q.strip() for q in queries]


# # ============================================================
# # 5. Multi-Query Retrieval
# # ============================================================

# def retrieve_multi_query(question):

#     # --------------------------------------------------------
#     # Generate 3 alternative queries
#     # --------------------------------------------------------

#     queries = generate_queries(question)

#     print("\n" + "=" * 70)
#     print("GENERATED QUERIES")
#     print("=" * 70)

#     for i, query in enumerate(queries, start=1):
#         print(f"{i}. {query}")

#     # --------------------------------------------------------
#     # Retrieve top 3 chunks for EACH query
#     # --------------------------------------------------------

#     all_docs = []

#     for query in queries:

#         docs = db.similarity_search(
#             query,
#             k=3
#         )

#         all_docs.extend(docs)

#     print("\n" + "=" * 70)
#     print("RETRIEVAL SUMMARY")
#     print("=" * 70)

#     print(f"Queries generated: {len(queries)}")
#     print("Chunks retrieved per query: 3")
#     print(f"Total chunks before deduplication: {len(all_docs)}")

#     # --------------------------------------------------------
#     # Deduplicate chunks by content
#     # --------------------------------------------------------

#     unique_docs = []
#     seen_contents = set()

#     for doc in all_docs:

#         content = doc.page_content.strip()

#         if content not in seen_contents:
#             seen_contents.add(content)
#             unique_docs.append(doc)

#     print(f"Unique chunks after deduplication: {len(unique_docs)}")

#     return unique_docs, queries


# # ============================================================
# # 6. Grounded RAG function
# # ============================================================

# def answer_question(question):

#     # --------------------------------------------------------
#     # Multi-query retrieval
#     # --------------------------------------------------------

#     docs, queries = retrieve_multi_query(question)

#     # --------------------------------------------------------
#     # Show retrieved sources
#     # --------------------------------------------------------

#     print("\n" + "=" * 70)
#     print("RETRIEVED SOURCES")
#     print("=" * 70)

#     for i, doc in enumerate(docs, start=1):

#         source = doc.metadata.get(
#             "source",
#             "unknown"
#         )

#         source = os.path.basename(source)

#         print(f"{i}. {source}")

#     # --------------------------------------------------------
#     # Build context
#     # --------------------------------------------------------

#     context_parts = []

#     for doc in docs:

#         source = doc.metadata.get(
#             "source",
#             "unknown"
#         )

#         source = os.path.basename(source)

#         context_parts.append(
#             f"[Source: {source}]\n{doc.page_content}"
#         )

#     context = "\n\n".join(context_parts)

#     # --------------------------------------------------------
#     # Grounded prompt
#     # --------------------------------------------------------

#     prompt = f"""
# You are a banking knowledge-base assistant.

# Answer the user's question ONLY using the provided context.

# Rules:

# 1. Use ONLY the information contained in the context.
# 2. Do NOT use outside knowledge.
# 3. Do NOT guess or invent information.
# 4. Every factual statement must include the source filename
#    in square brackets after the statement.
# 5. If the context does not contain the answer, reply EXACTLY:

# I don't have that information in my knowledge base — let me connect you to a human agent.

# IMPORTANT:
# The retrieved context may contain multiple documents and chunks.
# Only use information that directly supports the user's question.

# CONTEXT:

# {context}

# USER QUESTION:

# {question}
# """

#     # --------------------------------------------------------
#     # Generate final answer
#     # --------------------------------------------------------

#     answer = ask_llm(prompt)

#     print("\n" + "=" * 70)
#     print("FINAL ANSWER")
#     print("=" * 70)

#     print(answer)

#     return answer


# # ============================================================
# # 7. Interactive question loop
# # ============================================================

# print("\nMulti-Query RAG Knowledge Base Assistant")
# print("Type 'exit' to stop.\n")

# while True:

#     question = input("You: ").strip()

#     if question.lower() == "exit":
#         print("Goodbye!")
#         break

#     if not question:
#         continue

#     try:
#         answer_question(question)

#     except Exception as e:
#         print("\nERROR:")
#         print(e)


# new code for the day 5
import os
import json
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

    if not MODEL:
        raise ValueError(
            "MODEL is missing from your .env file"
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
# 3. Load Day 5 Chroma database
# ============================================================

embeddings = OpenRouterEmbeddings()

db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)


# ============================================================
# 4. Generate 3 alternative queries
# ============================================================

def generate_queries(question):

    prompt = f"""
You are a query-generation component for a banking knowledge-base
retrieval system.

Generate exactly THREE differently-worded versions of the user's
question.

The purpose is to improve document retrieval.

Do NOT answer the question.

Return ONLY valid JSON in this exact format:

[
  "query 1",
  "query 2",
  "query 3"
]

Rules:

1. Return exactly 3 queries.
2. Each query must have the same meaning as the original question.
3. Use different wording for each query.
4. Do not add information that is not present in the original question.
5. Do not answer the question.
6. Return JSON only.
7. Do not use Markdown code fences.

USER QUESTION:

{question}
"""

    raw_response = ask_llm(prompt).strip()

    # Handle accidental Markdown code fences
    if raw_response.startswith("```"):
        raw_response = raw_response.replace("```json", "")
        raw_response = raw_response.replace("```", "")
        raw_response = raw_response.strip()

    try:
        queries = json.loads(raw_response)

    except json.JSONDecodeError as e:
        raise ValueError(
            "LLM did not return valid JSON for query generation.\n"
            f"Raw response:\n{raw_response}"
        ) from e

    # Validate that response is a list
    if not isinstance(queries, list):
        raise ValueError(
            "Query generation response is not a JSON list."
        )

    # Validate exactly 3 queries
    if len(queries) != 3:
        raise ValueError(
            f"Expected exactly 3 queries, but received {len(queries)}."
        )

    # Validate query contents
    if not all(
        isinstance(q, str) and q.strip()
        for q in queries
    ):
        raise ValueError(
            "All generated queries must be non-empty strings."
        )

    return [q.strip() for q in queries]


# ============================================================
# 5. Multi-Query Retrieval
# ============================================================

def retrieve_multi_query(question):

    # --------------------------------------------------------
    # Generate 3 alternative queries
    # --------------------------------------------------------

    queries = generate_queries(question)

    print("\n" + "=" * 70)
    print("GENERATED QUERIES")
    print("=" * 70)

    for i, query in enumerate(queries, start=1):
        print(f"{i}. {query}")

    # --------------------------------------------------------
    # Retrieve k=3 for EACH query
    # --------------------------------------------------------

    all_docs = []

    for query in queries:

        docs = db.similarity_search(
            query,
            k=3
        )

        all_docs.extend(docs)

    # --------------------------------------------------------
    # Retrieval statistics
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("RETRIEVAL SUMMARY")
    print("=" * 70)

    print(f"Queries generated: {len(queries)}")
    print("Chunks retrieved per query: 3")
    print(
        f"Total chunks before deduplication: {len(all_docs)}"
    )

    # --------------------------------------------------------
    # Deduplicate by chunk CONTENT
    # --------------------------------------------------------

    unique_docs = []
    seen_contents = set()

    for doc in all_docs:

        content = doc.page_content.strip()

        if content not in seen_contents:

            seen_contents.add(content)
            unique_docs.append(doc)

    print(
        f"Unique chunks after deduplication: "
        f"{len(unique_docs)}"
    )

    return unique_docs, queries


# ============================================================
# 6. Grounded RAG Answer
# ============================================================

def answer_question(question):

    # --------------------------------------------------------
    # Multi-query retrieval
    # --------------------------------------------------------

    docs, queries = retrieve_multi_query(question)

    # --------------------------------------------------------
    # Show retrieved sources
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("RETRIEVED SOURCES")
    print("=" * 70)

    if not docs:
        print("No documents were retrieved.")

    for i, doc in enumerate(docs, start=1):

        source = doc.metadata.get(
            "source",
            "unknown"
        )

        source = os.path.basename(source)

        print(f"{i}. {source}")

    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context_parts = []

    for doc in docs:

        source = doc.metadata.get(
            "source",
            "unknown"
        )

        source = os.path.basename(source)

        context_parts.append(
            f"[Source: {source}]\n"
            f"{doc.page_content}"
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

IMPORTANT:

The retrieved context may contain multiple documents and chunks.

Only use information that directly supports the user's question.

Do not assume that because a retrieved chunk is related to the
question, it necessarily contains the answer.

CONTEXT:

{context}

USER QUESTION:

{question}
"""

    # --------------------------------------------------------
    # Generate final answer
    # --------------------------------------------------------

    answer = ask_llm(prompt)

    print("\n" + "=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)

    print(answer)

    return answer


# ============================================================
# 7. Interactive Question Loop
# ============================================================

print("\nMulti-Query RAG Knowledge Base Assistant")
print("Type 'exit' to stop.\n")

while True:

    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Goodbye!")
        break

    if not question:
        continue

    try:

        answer_question(question)

    except Exception as e:

        print("\nERROR:")
        print(e)
