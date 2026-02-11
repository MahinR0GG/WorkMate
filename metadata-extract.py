import os
import json
from datetime import datetime

class DocumentMetadataExtractor:
    """
    Extracts technical metadata from documents (DOCX / PDF)
    and stores metadata separately for each document
    """

    SUPPORTED_EXTENSIONS = (".docx", ".pdf")

    def __init__(self, folder_path, metadata_folder="metadata"):
        self.folder_path = folder_path
        self.metadata_folder = os.path.join(folder_path, metadata_folder)

        # Create metadata folder if not exists
        os.makedirs(self.metadata_folder, exist_ok=True)

    def extract_file_metadata(self, file_path):
        """
        Extract metadata for a single file
        """
        return {
            "filename": os.path.basename(file_path),
            "file_location": os.path.dirname(os.path.abspath(file_path)),
            "file_type": os.path.splitext(file_path)[1].lower(),
            "file_size_kb": round(os.path.getsize(file_path) / 1024, 2),
            "last_modified_date": datetime.fromtimestamp(
                os.path.getmtime(file_path)
            ).strftime("%Y-%m-%d %H:%M:%S")
        }

    def save_metadata_file(self, metadata):
        """
        Save metadata for a single document as JSON
        """
        base_name = os.path.splitext(metadata["filename"])[0]
        base_name = base_name.lower()                      # lowercase
        output_name = f"{base_name}-metadata.json"         # append suffix

        output_path = os.path.join(self.metadata_folder, output_name)

        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(metadata, json_file, indent=4)

    def process_documents(self):
        """
        Process all supported documents in the folder
        """
        count = 0

        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)

            if (
                os.path.isfile(file_path)
                and filename.lower().endswith(self.SUPPORTED_EXTENSIONS)
            ):
                metadata = self.extract_file_metadata(file_path)
                self.save_metadata_file(metadata)
                count += 1

        print(f"Metadata extracted for {count} files successfully.")

    def run(self):
        """
        Execute full metadata extraction pipeline
        """
        self.process_documents()


# -------------------- Usage --------------------
if __name__ == "__main__":
    extractor = DocumentMetadataExtractor(
        folder_path=r"C:\Users\Cymonic\Desktop\Cymonic\HR_BOT\WorkMate"   # root directory
    )
    extractor.run()
