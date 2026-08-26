# Day 04 — Task 4.1 Notes

## Knowledge Base and Indexing

I created 10 synthetic banking knowledge-base documents and indexed them using LangChain, OpenAI embeddings, and ChromaDB.

### Initial Configuration

* Number of documents: 10
* Chunk size: 500
* Chunk overlap: 50
* Number of chunks created: 20

The program output was:

`Indexed 20 chunks from 10 documents.`

### After Changing Chunk Size

I changed the chunk size from 500 to 100 while keeping the chunk overlap at 50.

* Number of documents: 10
* Chunk size: 100
* Chunk overlap: 50
* Number of chunks created: 103

The program output was:

`Indexed 103 chunks from 10 documents.`

### Observation

When the chunk size was reduced from 500 to 100, the number of chunks increased from 20 to 103.

This happened because a smaller chunk size divides the same documents into much smaller pieces. Therefore, more chunks are required to store all the document content.

With a chunk size of 500, each chunk contains more information, so fewer chunks are created. With a chunk size of 100, each chunk contains less information, so many more chunks are created.

### Why Chunk Size Is a Design Decision

Chunk size is not simply a default value because the best size depends on the type of data and the requirements of the RAG system.

Smaller chunks can provide more precise retrieval because each chunk contains a smaller and more focused piece of information. However, they can also result in a much larger number of chunks.

Larger chunks preserve more context and produce fewer chunks, but they may contain unnecessary information when retrieved for a specific question.

Therefore, chunk size should be selected based on the document structure, the amount of context required, and the desired retrieval accuracy.

### Conclusion

My experiment showed that reducing the chunk size from 500 to 100 increased the number of chunks from 20 to 103 while the number of source documents remained 10.

This demonstrates that chunk size has a direct impact on the number of chunks and is an important design decision when building a RAG knowledge base.
