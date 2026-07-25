# 🧠 DocMind AI

**Retrieval-Augmented Knowledge Assistant (RAG Chatbot)**

Track 03 — AI Solutions Engineering | InnoViast Internship | Week 4

## 📝 Overview

DocMind is a RAG-based chatbot that answers questions from your uploaded documents. Instead of guessing or hallucinating, it retrieves relevant information from your knowledge base and provides grounded, source-cited answers.

## ✨ Features

- 📄 Upload PDF and TXT documents
- 🔍 Vector search with semantic understanding
- 🎯 Grounded responses with source citations
- ⚠️ Clear fallback when answers aren't found
- 🚀 Deploy in minutes with Streamlit

## 🛠 Tech Stack

| Component | Tool |
|-----------|------|
| **Backend** | Python 3.10+ |
| **Frontend** | Streamlit |
| **RAG Framework** | LangChain |
| **Vector DB** | Chroma DB |
| **Embeddings** | sentence-transformers |
| **LLM** | Groq API (Llama) |
| **Deployment** | Streamlit Community Cloud |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Groq API key (free from https://console.groq.com)

### Installation

```bash
# Clone or download repository
cd DocMind-InnoViast

# Create virtual environment
python -m venv venv

# Windows: Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file and add:
GROQ_API_KEY=your_key_here

# Run app
streamlit run app.py
```

Visit: http://localhost:8501

## 📚 Knowledge Base

Place your documents in the `/data` folder:
- `data/sample_1.pdf`
- `data/sample_2.txt`
- etc.

## 🔄 Project Phases

- [x] Phase 1: Environment Setup
- [ ] Phase 2: Knowledge Base Selection
- [ ] Phase 3: Document Ingestion & Chunking
- [ ] Phase 4: Embeddings & Vector Store
- [ ] Phase 5: Retrieval & LLM Chain
- [ ] Phase 6: Streamlit UI
- [ ] Phase 7: Testing
- [ ] Phase 8: Deployment
- [ ] Phase 9: Documentation
- [ ] Phase 10: Presentation

## 📊 Evaluation Criteria

| Criteria | Weight |
|----------|--------|
| Functionality | 30% |
| UI/UX | 20% |
| Code Structure | 15% |
| GitHub Management | 10% |
| Creativity | 10% |
| Presentation | 10% |
| Deadline Discipline | 5% |

## 🔗 Links

- **Deployment:** (Coming soon)
- **Repository:** (Add GitHub link)
- **Demo Video:** (Coming soon)

## 📖 Learning Outcomes

- RAG architecture & vector search
- LangChain orchestration
- Streamlit full-stack development
- LLM integration (Groq API)
- Prompt engineering for grounding

---

**Last Updated:** Phase 1 ✅