import json
from loguru import logger


class BatchManager:
    def __init__(self, batch_size_kb=15000):
        # Set the batch size in KBs
        self.batch_size_kb = batch_size_kb
        # Calculate the batch size in bytes
        self.batch_size_bytes = batch_size_kb * 1024

        self.current_batch = []
        self.current_batch_size = 0

    def add_to_batch(self, document):
        # logger.debug("Adding document to batch")
        self.current_batch.append(document)
        self.current_batch_size += len(json.dumps(document).encode("utf-8"))

    def batch_has_docs(self):
        return len(self.current_batch) > 0

    def get_batch(self):
        return self.current_batch

    def reset_batch(self):
        self.current_batch = []
        self.current_batch_size = 0

    def is_document_too_large(self, document):
        doc_size_bytes = len(json.dumps(document).encode("utf-8"))

        if self.current_batch_size + doc_size_bytes > self.batch_size_bytes:
            logger.debug("Document exceeds batch size")
            return True
        else:
            # logger.debug("Document does not exceed batch size")
            return False
