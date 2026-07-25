import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FOLDER = "data"
CHROMA_DB_PATH = "chroma_db"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"
TOP_K = 3
SIMILARITY_THRESHOLD = 0.5

RAG_PROMPT = ChatPromptTemplate.from_template("""
You are DocMind AI, a helpful assistant that answers questions ONLY using the
provided context from the user's documents.

Rules:
- If the context contains the answer, respond clearly.
- If the context does NOT contain relevant information, say exactly:
  "I couldn't find information about this in the knowledge base."
- Never make up information not present in the context.

Context:
{context}

Question: {question}

Answer:
""")

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="DocMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CACHED RESOURCES
# ============================================================================

@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=f"sentence-transformers/{EMBEDDING_MODEL}")

@st.cache_resource
def get_llm():
    return ChatGroq(
        model=LLM_MODEL,
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

@st.cache_resource
def get_vectorstore(_embeddings):
    if not Path(CHROMA_DB_PATH).exists():
        return None
    return Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=_embeddings)

# ============================================================================
# INGEST NEW UPLOADED FILES
# ============================================================================

def ingest_uploaded_files(uploaded_files, embeddings):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    new_docs = []

    for file in uploaded_files:
        save_path = os.path.join(DATA_FOLDER, file.name)
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())

        if file.name.lower().endswith(".txt"):
            loader = TextLoader(save_path, encoding="utf-8")
        elif file.name.lower().endswith(".pdf"):
            loader = PyPDFLoader(save_path)
        else:
            continue

        new_docs.extend(loader.load())

    if not new_docs:
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(new_docs)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    return vectorstore

# ============================================================================
# RAG PIPELINE
# ============================================================================

def rag_pipeline(question, vectorstore, llm):
    results = vectorstore.similarity_search_with_relevance_scores(question, k=TOP_K)

    if not results or results[0][1] < SIMILARITY_THRESHOLD:
        return (
            "I couldn't find information about this in the knowledge base. "
            "Please check your documents or ask something else.",
            None
        )

    context_parts = []
    sources = set()
    for doc, score in results:
        context_parts.append(doc.page_content)
        sources.add(os.path.basename(doc.metadata.get("source", "Unknown")))

    context = "\n\n---\n\n".join(context_parts)
    prompt = RAG_PROMPT.format(context=context, question=question)
    response = llm.invoke(prompt)

    return (response.content, ", ".join(sources))

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🧠 DocMind AI")
    st.subheader("📚 Knowledge Base")

    existing_files = list(Path(DATA_FOLDER).glob("*.txt")) + list(Path(DATA_FOLDER).glob("*.pdf")) if Path(DATA_FOLDER).exists() else []

    if existing_files:
        st.success(f"✅ {len(existing_files)} document(s) loaded")
        for f in existing_files:
            st.write(f"- 📄 {f.name}")
    else:
        st.info("No documents yet. Upload below.")

    uploaded_files = st.file_uploader(
        "Upload PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files:
        with st.spinner("Processing new documents..."):
            embeddings = get_embeddings()
            ingest_uploaded_files(uploaded_files, embeddings)
            st.cache_resource.clear()
        st.success(f"✅ Added {len(uploaded_files)} new file(s)! Refresh to see updated list.")
        st.rerun()

    st.divider()
    st.caption("💡 Tip: Upload PDFs or TXT files, then ask questions in the chat.")

# ============================================================================
# MAIN CHAT AREA
# ============================================================================

st.title("💬 Chat with Your Documents")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("source"):
            st.success(f"📄 Source: {message['source']}")
        elif message["role"] == "assistant" and message.get("source") is None and "couldn't find" in message["content"]:
            st.warning("⚠️ Not found in knowledge base")

user_input = st.chat_input("Ask a question about your documents...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        embeddings = get_embeddings()
        vectorstore = get_vectorstore(embeddings)
        llm = get_llm()

        if vectorstore is None:
            answer = "⚠️ No knowledge base found. Please upload documents first."
            source = None
        else:
            with st.spinner("🔍 Searching knowledge base..."):
                answer, source = rag_pipeline(user_input, vectorstore, llm)

        st.write(answer)
        if source:
            st.success(f"📄 Source: {source}")
        elif "couldn't find" in answer:
            st.warning("⚠️ Not found in knowledge base")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "source": source
    })