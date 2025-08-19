from typing import List
from pathlib import PurePath
from langchain.docstore.document import Document
from .abstract import AbstractLoader


class TXTLoader(AbstractLoader):
    """
    Loader for PDF files.
    """
    _extension = ['.txt']

    def _load_document(self, path: PurePath) -> List[Document]:
        """
        Load a TXT file.

        Args:
            path (Path): The path to the TXT file.

        Returns:
            list: A list of Langchain Documents.
        """
        docs = []
        if self._check_path(path):
            self.logger.info(f"Loading TXT file: {path}")
            with open(path, 'r') as file:
                text = file.read()
            try:
                summary = self.get_summary_from_text(text, use_gpu=True)
            except Exception:
                summary = ''
            metadata = self.create_metadata(
                path=path,
                doctype=self.doctype,
                source_type=self._source_type,
                summary=summary,
                doc_metadata={}
            )
            # Create document-level context
            document_context = f"File Name: {path.name}\n"
            document_context += f"Document Type: {self.doctype}\n"
            document_context += f"Source Type: {self._source_type}\n"
            document_context += f"Summary: {summary}\n\n"
            # splitting the content:
            for chunk in self.markdown_splitter.split_text(text):
                _idx = {
                    **metadata
                }
                docs.append(
                    Document(
                        page_content=document_context + chunk,
                        metadata=_idx
                    )
                )
        return docs
