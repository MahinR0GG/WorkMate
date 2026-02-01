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

### Core Technologies
- **Python 3.x**: Primary programming language
- **RAG (Retrieval-Augmented Generation)**: Architecture pattern for intelligent responses
- **Vector Database**: For storing and retrieving document embeddings (implementation in progress)

### Libraries & Dependencies
- **python-docx**: DOCX file parsing and processing
- **JSON**: Data serialization and chunk storage
- **Regular Expressions (re)**: Pattern matching for document structure detection
- **os & datetime**: File system operations and metadata extraction

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

## 🚀 Usage

### Running the Chunking Pipeline

```bash
# Extract metadata from documents
python metadata-extract.py

# Chunk documents into Q&A pairs
python chunker.py

# Merge chunks with metadata
python chunk-metadata-merger.py
```

### Quick Start
```bash
# Run the complete chunking process
python run_chunker.py
```

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd HR-Bot

# Install dependencies
pip install -r requirements.txt
```

## 🔮 Upcoming Features

- [ ] Vector database integration (ChromaDB/Pinecone/Weaviate)
- [ ] Embedding generation for chunks
- [ ] LLM integration for response generation
- [ ] Chat interface (Web/CLI)
- [ ] Query logging and analytics
- [ ] Multi-language support
- [ ] Additional policy documents (WFH policies, etc.)

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
