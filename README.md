# HR Bot - Internal HR Assistant 🤖

> **Status**: 🚧 Under Active Development - More features coming soon!

An intelligent internal HR chatbot that assists employees by answering queries related to **Leave Policies** and **Reimbursement Policies** using Retrieval-Augmented Generation (RAG) architecture.

## 📋 Overview

This HR Bot leverages RAG (Retrieval-Augmented Generation) to provide accurate, context-aware responses to employee queries about company policies. The system processes policy documents, chunks them into manageable pieces, enriches them with metadata, and stores them in a vector database for optimized semantic search and retrieval.

## ✨ Key Features

- **Policy Coverage**: Leave policies and reimbursement policies
- **RAG Architecture**: Combines document retrieval with generative AI for accurate responses
- **Optimized Search**: Vector database integration for fast, semantic search
- **Document Processing**: Automated chunking of policy documents (DOCX/PDF)
- **Metadata Enrichment**: Each chunk includes document metadata for better context
- **Structured Q&A Format**: Documents are chunked by question-answer pairs for precise retrieval

## 🛠️ Tech Stack

| Layer                  | Technology                                               |
| ---------------------- | -------------------------------------------------------- |
| **LLM**                | Ollama (`llama3`) — local, runs entirely on your machine |
| **Orchestration**      | LangChain (RAG pipeline + token-aware STM)               |
| **Embeddings**         | `sentence-transformers/all-MiniLM-L6-v2`                 |
| **Vector Store**       | FAISS                                                    |
| **Backend**            | FastAPI + Uvicorn                                        |
| **Session Memory**     | SQLite (per-session short-term memory)                   |
| **React Frontend**     | Vite + React (`frontend/react-app/`)                     |
| **Streamlit Frontend** | Streamlit — backup UI (`frontend/streamlit_app.py`)      |

## 🏗️ Project Structure

```
HR-Bot/
├── chunker.py                  # Main document chunking logic
├── metadata-extract.py         # Document metadata extraction
├── chunk-metadata-merger.py    # Merges chunks with metadata
├── run_chunker.py             # Entry point for chunking process
├── chunks/                    # Raw document chunks (JSON)
├── chunks2/                   # Alternative chunk output
├── metadata/                  # Document metadata files
├── chunks+metadata/           # Enriched chunks with metadata
├── Leave-Policy.docx          # Source: Leave policy document
├── Leave-Policy.pdf           # Source: Leave policy (PDF)
├── Reimbursement-Policy.docx  # Source: Reimbursement policy
├── Reimbursement-Policy.pdf   # Source: Reimbursement policy (PDF)
└── WFH_*.docx                 # Work from home policies
```

## 🔄 Workflow

### 1. **Document Ingestion**

- Policy documents (DOCX/PDF) are stored in the project root
- Supported formats: `.docx`, `.pdf`

### 2. **Metadata Extraction** (`metadata-extract.py`)

- Extracts technical metadata from each document:
  - Filename
  - File location
  - File type
  - File size (KB)
  - Last modified date
- Saves metadata as individual JSON files in `metadata/` folder

### 3. **Document Chunking** (`chunker.py`)

- Loads DOCX paragraphs
- Detects question headers using regex patterns (e.g., "1. What is...")
- Creates chunks where **1 question = 1 chunk**
- Each chunk contains:
  - `doc_name`: Source document name
  - `question`: The question text
  - `answer`: The corresponding answer
  - `chunk_id`: Unique identifier (e.g., `leave_policy_5`)
- Saves chunks as individual JSON files in `chunks/` folder

### 4. **Chunk-Metadata Merging** (`chunk-metadata-merger.py`)

- Combines document chunks with their corresponding metadata
- Creates enriched chunks with full context
- Output saved in `chunks+metadata/` folder
- Final structure:
  ```json
  {
    "doc_name": "Reimbursement Policy",
    "question": "9. How should employees submit reimbursement claims?",
    "answer": "• Claims must be submitted through...",
    "chunk_id": "reimbursement_policy_28",
    "document_metadata": {
      "filename": "Reimbursement-Policy.pdf",
      "file_location": "C:\\Mahin\\HR-Bot",
      "file_type": ".pdf",
      "file_size_kb": 53.23,
      "last_modified_date": "2026-01-29 21:30:15"
    }
  }
  ```

### 5. **Vector Database Storage** (In Progress)

- Enriched chunks will be embedded and stored in a vector database
- Enables semantic search for relevant policy information
- Optimized retrieval for RAG pipeline

### 6. **RAG Query Processing** (Planned)

- User query → Vector search → Retrieve relevant chunks
- Retrieved context + Query → LLM → Generate accurate response

## 🚀 Getting Started (First-Time Setup)

### Prerequisites

| Tool             | Why            | Install                          |
| ---------------- | -------------- | -------------------------------- |
| **Python 3.10+** | Backend        | [python.org](https://python.org) |
| **Node.js 18+**  | React frontend | [nodejs.org](https://nodejs.org) |
| **Ollama**       | Local LLM      | [ollama.com](https://ollama.com) |

### 1 — Clone the repo

```bash
git clone https://github.com/MahinR0GG/WorkMate.git
cd WorkMate
```

### 2 — Pull the LLM model

```bash
ollama pull llama3
```

### 3 — Python environment & dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4 — Environment variables

```bash
# Windows
copy .env.example .env
# Mac/Linux
cp .env.example .env
```

> Defaults work out of the box for a local Ollama setup — no edits needed.

### 5 — Build the vector embeddings

> ⚠️ `data/raw/` policy documents are gitignored (sensitive). Ask the repo owner for these files and place them in `data/raw/` before running this step.

```bash
python scripts/embed-chunks.py
```

### 6 — Start the backend

```bash
python run.py
```

> API runs at **http://localhost:8000** — keep this terminal open.

### 7 — Run a frontend (new terminal)

**Option A — React (recommended)**

```bash
cd frontend/react-app
npm install
npm run dev
```

Open **http://localhost:5173**

**Option B — Streamlit (backup)**

```bash
cd frontend
streamlit run streamlit_app.py
```

Open **http://localhost:8501**

---

> **TL;DR order:** `ollama pull llama3` → `pip install -r requirements.txt` → copy `.env` → embed → `python run.py` → `npm run dev`

## 🔮 Upcoming Features

- [ ] Azure OpenAI support (Phase 2 LLM provider)
- [ ] Query logging and analytics
- [ ] Multi-language support
- [ ] Additional policy documents

## 📝 Document Format Requirements

For optimal chunking, policy documents should follow this structure:

- Questions numbered sequentially (e.g., "1. What is...", "2. How do...")
- Answers follow immediately after questions
- Clear paragraph separation

## 🤝 Contributing

This project is under active development. Contributions, suggestions, and feedback are welcome!

## 📄 License

Internal use only - Company proprietary

---

**Note**: This is an internal tool designed to streamline HR policy queries and reduce the workload on HR teams by providing instant, accurate policy information to employees.
