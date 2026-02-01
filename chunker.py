from docx import Document
import re
import os
import json


# -----------------------------
# 1. Load DOCX paragraphs
# -----------------------------
def load_docx_paragraphs(file_path):
    """
    Reads a DOCX file and returns a list of non-empty paragraphs
    """
    doc = Document(file_path)
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]


# -----------------------------
# 2. Detect question headers
# -----------------------------
SECTION_PATTERN = re.compile(r"^\d+\.\s")

def is_section_header(text):
    """
    Returns True if the text is a numbered question (e.g., '1. What is...')
    """
    return bool(SECTION_PATTERN.match(text))


# -----------------------------
# 3. Chunking logic
#    (1 question = 1 chunk)
# -----------------------------
def chunk_by_question(paragraphs, doc_name):
    chunks = []
    current_question = None
    current_answer = []

    for para in paragraphs:
        if is_section_header(para):
            if current_question:
                chunks.append({
                    "doc_name": doc_name,
                    "question": current_question,
                    "answer": " ".join(current_answer)
                })
            current_question = para
            current_answer = []
        else:
            current_answer.append(para)

    # Save last question
    if current_question:
        chunks.append({
            "doc_name": doc_name,
            "question": current_question,
            "answer": " ".join(current_answer)
        })

    return chunks


# -----------------------------
# 4. Add chunk IDs
# -----------------------------
def add_chunk_ids(chunks):
    for i, chunk in enumerate(chunks):
        doc_slug = chunk["doc_name"].lower().replace(" ", "_")
        chunk["chunk_id"] = f"{doc_slug}_{i}"
    return chunks


# -----------------------------
# 5. Save chunks individually
# -----------------------------
def save_chunks_individually(chunks, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for chunk in chunks:
        file_path = os.path.join(output_dir, f"{chunk['chunk_id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)


# -----------------------------
# 6. Main entry function
# -----------------------------
def process_documents(docx_files, output_dir="chunks"):
    """
    docx_files: list of .docx file paths
    output_dir: directory where JSON chunks will be saved
    """
    all_chunks = []

    for file_path in docx_files:
        doc_name = os.path.splitext(os.path.basename(file_path))[0]
        doc_name = doc_name.replace("-", " ").replace("_", " ")

        paragraphs = load_docx_paragraphs(file_path)
        chunks = chunk_by_question(paragraphs, doc_name)
        all_chunks.extend(chunks)

    all_chunks = add_chunk_ids(all_chunks)
    save_chunks_individually(all_chunks, output_dir)

    return all_chunks

# ============================================================
# 7. Self-run entry point (ONLY runs when file is executed)
# ============================================================
if __name__ == "__main__":

    # List of DOCX files to process
    DOCX_FILES = [
        "Leave-Policy.docx",
        "Reimbursement-Policy.docx"
    ]

    # Output directory for individual chunk JSON files
    OUTPUT_DIR = "chunks2"

    print("Starting DOCX chunking process...")
    print("Input files:", DOCX_FILES)
    print("Output directory:", OUTPUT_DIR)

    process_documents(
        docx_files=DOCX_FILES,
        output_dir=OUTPUT_DIR
    )

    print("Chunking completed successfully.")
