import os
import json


class ChunkMetadataMerger:
    """
    Merges document-level metadata into chunk JSON files
    """

    def __init__(self):
        # Hard-wired paths (as requested: just run it)
        self.root_dir = r"C:\Mahin\HR-Bot"
        self.chunks_folder = os.path.join(self.root_dir, "chunks")
        self.metadata_folder = os.path.join(self.root_dir, "metadata")
        self.output_folder = os.path.join(self.root_dir, "chunks+metadata")

        os.makedirs(self.output_folder, exist_ok=True)

    def _load_metadata(self, doc_name):
        """
        Resolve metadata file from doc_name
        Example: Leave Policy -> Leave-Policy.json
        """
        metadata_filename = doc_name.replace(" ", "-") + ".json"
        metadata_path = os.path.join(self.metadata_folder, metadata_filename)

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(
                f"Metadata file not found for document: {doc_name}"
            )

        with open(metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def merge(self):
        processed = 0

        for filename in os.listdir(self.chunks_folder):
            if not filename.endswith(".json"):
                continue

            chunk_path = os.path.join(self.chunks_folder, filename)

            with open(chunk_path, "r", encoding="utf-8") as f:
                chunk_data = json.load(f)

            doc_name = chunk_data.get("doc_name")
            if not doc_name:
                print(f"Skipping {filename}: missing doc_name")
                continue

            metadata = self._load_metadata(doc_name)

            enriched_chunk = {
                **chunk_data,
                "document_metadata": metadata
            }

            output_path = os.path.join(self.output_folder, filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(enriched_chunk, f, indent=4)

            processed += 1

        print(f"✅ Successfully created {processed} enriched chunk files.")

    def run(self):
        self.merge()


# -------------------- RUN --------------------
if __name__ == "__main__":
    ChunkMetadataMerger().run()
