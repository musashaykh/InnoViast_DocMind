

import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

CHROMA_DB_PATH = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"   # fast + free tier friendly on Groq
TOP_K = 3                            # how many chunks to retrieve
SIMILARITY_THRESHOLD = 0.5           # below this, treat as "not found"

# ============================================================================
# LOAD VECTOR STORE (already built in Phase 4)
# ============================================================================

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=f"sentence-transformers/{EMBEDDING_MODEL}")
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings
    )
    return vectorstore

# ============================================================================
# PROMPT TEMPLATE
# ============================================================================

RAG_PROMPT = ChatPromptTemplate.from_template("""
You are DocMind AI, a helpful assistant that answers questions ONLY using the
provided context from the user's documents. 

Rules:
- If the context contains the answer, respond clearly and cite it naturally.
- If the context does NOT contain relevant information, say exactly:
  "I couldn't find information about this in the knowledge base."
- Never make up information not present in the context.

Context:
{context}

Question: {question}

Answer:
""")

# ============================================================================
# RAG PIPELINE FUNCTION
# ============================================================================

def rag_pipeline(question: str, vectorstore, llm):
    """
    Retrieve relevant chunks and generate an answer.
    Returns: (answer: str, source: str or None)
    """

    # Step 1: Retrieve with scores
    results = vectorstore.similarity_search_with_relevance_scores(question, k=TOP_K)

    if not results or results[0][1] < SIMILARITY_THRESHOLD:
        return (
            "⚠️ I couldn't find information about this in the knowledge base. "
            "Please check your documents or ask something else.",
            None
        )

    # Step 2: Build context from retrieved chunks
    context_parts = []
    sources = set()
    for doc, score in results:
        context_parts.append(doc.page_content)
        source_name = os.path.basename(doc.metadata.get("source", "Unknown"))
        sources.add(source_name)

    context = "\n\n---\n\n".join(context_parts)

    # Step 3: Generate answer with LLM
    prompt = RAG_PROMPT.format(context=context, question=question)
    response = llm.invoke(prompt)

    source_str = ", ".join(sources)

    return (response.content, source_str)

# ============================================================================
# TEST SCRIPT
# ============================================================================

def main():
    print("\n" + "=" * 80)
    print("🧠 DOCMIND AI - PHASE 5: RETRIEVAL & LLM CHAIN")
    print("=" * 80)

    print("\n📦 Loading vector store...")
    vectorstore = load_vectorstore()

    print("🤖 Connecting to Groq LLM...")
    llm = ChatGroq(
        model=LLM_MODEL,
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    test_questions = [
        "What is a variable in Python?",
        "How do I fix a NameError?",
        "What's the weather like today?"   # should trigger fallback
    ]

    for q in test_questions:
        print(f"\n{'='*80}")
        print(f"❓ Question: {q}")
        print('='*80)

        answer, source = rag_pipeline(q, vectorstore, llm)

        print(f"\n💬 Answer:\n{answer}")
        if source:
            print(f"\n📄 Source: {source}")
        else:
            print(f"\n📄 Source: None (fallback triggered)")

    print("\n✅ Phase 5 Complete!")
    print("📌 Next: Phase 6 - Streamlit UI Integration\n")

if __name__ == "__main__":
    main()