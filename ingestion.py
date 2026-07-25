"""
Phase 3: Document Ingestion & Chunking
This script loads documents from /data folder and splits them into chunks.
"""

import os
from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FOLDER = "data"
CHUNK_SIZE = 800  # Characters per chunk
CHUNK_OVERLAP = 150  # Characters overlap between chunks

# ============================================================================
# DOCUMENT LOADER FUNCTION
# ============================================================================

def load_documents(folder_path: str) -> list:
    """
    Load all PDF and TXT files from a folder.
    
    Args:
        folder_path: Path to folder containing documents
    
    Returns:
        List of loaded documents
    """
    documents = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Error: Folder '{folder_path}' not found!")
        return documents
    
    files = list(folder.glob("*.txt")) + list(folder.glob("*.pdf"))
    
    if not files:
        print(f"⚠️ No PDF or TXT files found in '{folder_path}'")
        return documents
    
    print(f"\n📂 Found {len(files)} file(s) in '{folder_path}'\n")
    
    for file_path in files:
        try:
            print(f"📖 Loading: {file_path.name}...", end=" ")
            
            if file_path.suffix.lower() == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
                docs = loader.load()
            elif file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()
            else:
                print(f"⏭️ Skipped (unsupported format)")
                continue
            
            documents.extend(docs)
            print(f"✅ Loaded {len(docs)} page(s)")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    return documents

# ============================================================================
# TEXT SPLITTER FUNCTION
# ============================================================================

def chunk_documents(documents: list, chunk_size: int = CHUNK_SIZE, 
                    chunk_overlap: int = CHUNK_OVERLAP) -> list:
    """
    Split documents into chunks using RecursiveCharacterTextSplitter.
    
    Args:
        documents: List of documents from loader
        chunk_size: Size of each chunk (characters)
        chunk_overlap: Overlap between chunks (characters)
    
    Returns:
        List of document chunks
    """
    
    print(f"\n✂️ Splitting documents into chunks...")
    print(f"   - Chunk size: {chunk_size} characters")
    print(f"   - Overlap: {chunk_overlap} characters\n")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]  # Split by paragraphs first
    )
    
    chunks = splitter.split_documents(documents)
    
    return chunks

# ============================================================================
# DISPLAY CHUNKS FUNCTION
# ============================================================================

def display_chunks(chunks: list, max_display: int = 5):
    """
    Display sample chunks for verification.
    
    Args:
        chunks: List of document chunks
        max_display: Number of chunks to display
    """
    
    print(f"\n📊 CHUNKING RESULTS")
    print("=" * 80)
    print(f"Total chunks created: {len(chunks)}")
    print("=" * 80)
    
    for i, chunk in enumerate(chunks[:max_display]):
        print(f"\n{'─' * 80}")
        print(f"CHUNK {i+1}")
        print(f"{'─' * 80}")
        print(f"Source: {chunk.metadata.get('source', 'Unknown')}")
        print(f"Length: {len(chunk.page_content)} characters")
        print(f"\nContent:\n{chunk.page_content[:300]}...")  # Show first 300 chars
        print()
    
    if len(chunks) > max_display:
        print(f"\n... and {len(chunks) - max_display} more chunks")
        print(f"\n💡 Tip: Total {len(chunks)} chunks created successfully!")

# ============================================================================
# STATISTICS FUNCTION
# ============================================================================

def print_statistics(chunks: list):
    """
    Print statistics about the chunks.
    """
    
    if not chunks:
        print("⚠️ No chunks to analyze")
        return
    
    lengths = [len(chunk.page_content) for chunk in chunks]
    
    print(f"\n📈 CHUNK STATISTICS")
    print("=" * 80)
    print(f"Total chunks: {len(chunks)}")
    print(f"Average chunk size: {sum(lengths) / len(lengths):.0f} characters")
    print(f"Smallest chunk: {min(lengths)} characters")
    print(f"Largest chunk: {max(lengths)} characters")
    print(f"Total content: {sum(lengths):,} characters")
    print("=" * 80)

# ============================================================================
# SAVE CHUNKS TO FILE (OPTIONAL)
# ============================================================================

def save_chunks_info(chunks: list, output_file: str = "chunk_info.txt"):
    """
    Save chunk information to file for reference.
    """
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("DOCMIND AI - CHUNK INFORMATION\n")
        f.write("=" * 80 + "\n\n")
        
        for i, chunk in enumerate(chunks):
            f.write(f"CHUNK {i+1}\n")
            f.write(f"Source: {chunk.metadata.get('source', 'Unknown')}\n")
            f.write(f"Length: {len(chunk.page_content)} characters\n")
            f.write(f"Content:\n{chunk.page_content}\n")
            f.write("\n" + "─" * 80 + "\n\n")
    
    print(f"\n✅ Chunk information saved to '{output_file}'")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main function to orchestrate document loading and chunking.
    """
    
    print("\n" + "=" * 80)
    print("🧠 DOCMIND AI - PHASE 3: DOCUMENT INGESTION & CHUNKING")
    print("=" * 80)
    
    # Step 1: Load documents
    documents = load_documents(DATA_FOLDER)
    
    if not documents:
        print("❌ No documents loaded. Exiting.")
        return
    
    print(f"\n✅ Total documents loaded: {len(documents)}")
    
    # Step 2: Chunk documents
    chunks = chunk_documents(documents)
    
    if not chunks:
        print("❌ No chunks created. Exiting.")
        return
    
    # Step 3: Display results
    display_chunks(chunks)
    
    # Step 4: Print statistics
    print_statistics(chunks)
    
    # Step 5: Save chunk info (optional)
    save_chunks_info(chunks)
    
    print("\n✅ Phase 3 Complete!")
    print(f"📌 Next: Phase 4 - Embeddings & Vector Store\n")

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()