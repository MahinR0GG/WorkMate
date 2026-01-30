import os
import json
from datetime import datetime

class DocumentMetadataExtractor:
    """
    Extracts technical metadata from FAQ documents (DOCX / PDF)
    """

    SUPPORTED_EXTENSIONS = (".docx", ".pdf")

    def __init__(self, folder_path, output_file="metadata12.json"):
        self.folder_path = folder_path
        self.output_file = output_file

    def extract_file_metadata(self, file_path):
        """
        Extract metadata for a single file
        """
        metadata = {
            "filename": os.path.basename(file_path),
            "file_location": os.path.dirname(os.path.abspath(file_path)),
            "file_type": os.path.splitext(file_path)[1].lower(),
            "last_modified_date": datetime.fromtimestamp(
                os.path.getmtime(file_path)
            ).strftime("%Y-%m-%d %H:%M:%S")
        }
        return metadata

    def process_documents(self):
        """
        Process all supported documents in the folder
        """
        all_metadata = []

        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)

            if (
                os.path.isfile(file_path)
                and filename.lower().endswith(self.SUPPORTED_EXTENSIONS)
            ):
                metadata = self.extract_file_metadata(file_path)
                all_metadata.append(metadata)

        return all_metadata

    def save_to_json(self, metadata_list):
        """
        Save extracted metadata to JSON file
        """
        with open(self.output_file, "w", encoding="utf-8") as json_file:
            json.dump(metadata_list, json_file, indent=4)

    def run(self):
        """
        Execute full metadata extraction pipeline
        """
        metadata = self.process_documents()
        self.save_to_json(metadata)
        print(f"Metadata extracted for {len(metadata)} files successfully.")


# -------------------- Usage --------------------
if __name__ == "__main__":
    extractor = DocumentMetadataExtractor(
        folder_path=r"C:\Users\Cymonic\Desktop\Cymonic\HR_BOT\WorkMate",          # folder containing FAQ documents
        output_file="metadata12.json"     # output JSON file
    )
    extractor.run()
