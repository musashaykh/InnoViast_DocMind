"""
Debug script: check what similarity scores Chroma is actually returning.
"""

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_DB_PATH = "chroma_db"

embeddings = HuggingFaceEmbeddings(model_name=f"sentence-transformers/{EMBEDDING_MODEL}")
vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)

question = "what is python"

print(f"\n🔍 Query: {question}\n")
results = vectorstore.similarity_search_with_relevance_scores(question, k=8)

for i, (doc, score) in enumerate(results):
    print(f"--- Result {i+1} ---")
    print(f"Score: {score}")
    print(f"Source: {doc.metadata.get('source')}")
    print(f"Content preview: {doc.page_content[:100]}...")
    print()