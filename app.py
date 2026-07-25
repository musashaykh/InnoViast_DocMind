import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="DocMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🧠 DocMind AI")
st.subheader("Retrieval-Augmented Knowledge Assistant")

# Sidebar
with st.sidebar:
    st.write("### 📚 Knowledge Base")
    st.info("Upload documents and ask questions!")
    
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) loaded")
        for file in uploaded_files:
            st.write(f"- 📄 {file.name}")

# Main area
st.write("### Chat Interface")
user_input = st.chat_input("Ask a question about your documents...")

if user_input:
    st.info(f"You asked: {user_input}")
    st.warning("⏳ RAG pipeline coming in Phase 5...")