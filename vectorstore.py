
import os
from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FOLDER = "data"
CHROMA_DB_PATH = "chroma_db"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, lightweight, good quality

# ============================================================================
# LOAD & CHUNK (same as Phase 3)
# ============================================================================

def load_and_chunk_documents(folder_path: str) -> list:
    documents = []
    folder = Path(folder_path)
    files = list(folder.glob("*.txt")) + list(folder.glob("*.pdf"))

    print(f"\n📂 Found {len(files)} file(s) in '{folder_path}'\n")

    for file_path in files:
        try:
            print(f"📖 Loading: {file_path.name}...", end=" ")
            if file_path.suffix.lower() == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
            elif file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
            else:
                continue
            docs = loader.load()
            documents.extend(docs)
            print(f"✅ Loaded {len(docs)} page(s)")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    print(f"\n✂️ Splitting into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} chunks")

    return chunks

# ============================================================================
# CREATE EMBEDDINGS & VECTOR STORE
# ============================================================================

import shutil

def create_vectorstore(chunks: list):
    """
    Convert chunks to embeddings and store in ChromaDB.
    Always rebuilds fresh to avoid duplicate entries.
    """
    # Clean up any existing DB first to prevent duplicates
    if os.path.exists(CHROMA_DB_PATH):
        print(f"\n🗑️  Removing existing vector store to prevent duplicates...")
        shutil.rmtree(CHROMA_DB_PATH)

    print(f"\n🧠 Loading embedding model: {EMBEDDING_MODEL}...")
    print("   (First time will download the model, ~90MB, may take a minute)")

    embeddings = HuggingFaceEmbeddings(model_name=f"sentence-transformers/{EMBEDDING_MODEL}")

    print(f"\n💾 Creating vector store at '{CHROMA_DB_PATH}'...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )

    print(f"✅ Vector store created with {len(chunks)} embedded chunks")
    print(f"📁 Saved to disk at: {CHROMA_DB_PATH}/")

    return vectorstore

# ============================================================================
# TEST RETRIEVAL
# ============================================================================

def test_retrieval(vectorstore, test_query: str = "What is a variable in Python?"):
    """
    Run a test query to confirm retrieval works.
    """
    print(f"\n🔍 Testing retrieval with query: '{test_query}'")
    print("=" * 80)

    results = vectorstore.similarity_search(test_query, k=3)

    for i, doc in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Content: {doc.page_content[:200]}...")

    print("\n" + "=" * 80)
    print(f"✅ Retrieved {len(results)} relevant chunks successfully!")

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "=" * 80)
    print("🧠 DOCMIND AI - PHASE 4: EMBEDDINGS & VECTOR STORE")
    print("=" * 80)

    chunks = load_and_chunk_documents(DATA_FOLDER)

    if not chunks:
        print("❌ No chunks to process. Exiting.")
        return

    vectorstore = create_vectorstore(chunks)

    test_retrieval(vectorstore)

    print("\n✅ Phase 4 Complete!")
    print("📌 Next: Phase 5 - Retrieval & LLM Chain (connecting Groq API)\n")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()