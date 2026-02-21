from docx_chunker import process_documents

process_documents(
    [
        "Leave-Policy.docx",
        "Reimbursement-Policy.docx"
    ],
    output_dir="chunks"
)
