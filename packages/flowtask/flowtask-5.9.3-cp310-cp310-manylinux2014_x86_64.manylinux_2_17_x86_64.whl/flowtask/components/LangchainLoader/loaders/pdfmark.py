from pathlib import Path
import fitz
from pdf4llm import to_markdown
from langchain.docstore.document import Document
from langchain.text_splitter import MarkdownTextSplitter
from .basepdf import BasePDF


class PDFMarkdown(BasePDF):
    """
    Loader for PDF files converted content to markdown.
    """
    def __init__(
        self,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._splitter = MarkdownTextSplitter(chunk_size=2048, chunk_overlap=10)

    def _load_pdf(self, path: Path) -> list:
        """
        Load a PDF file using the PDFMiner library.

        Args:
            path (Path): The path to the PDF file.

        Returns:
            list: A list of Langchain Documents.
        """
        if self._check_path(path):
            self.logger.info(f"Loading PDF file: {path}")
            docs = []
            pdf = fitz.open(str(path))
            md_text = to_markdown(pdf)
            try:
                summary = self.get_summary_from_text(md_text, use_gpu=True)
            except Exception:
                summary = ''
            document_meta = {
                "title": pdf.metadata.get("title", ""),
                "creationDate": pdf.metadata.get("creationDate", ""),
                "author": pdf.metadata.get("author", ""),
            }
            metadata = self.create_metadata(
                path=path,
                doctype=self.doctype,
                source_type=self._source_type,
                summary=summary,
                doc_metadata=document_meta
            )

            # Prepend document-level context
            document_context = f"Document Title: {document_meta.get('title', '')}\n"
            # document_context += f"Document Author: {document_meta.get('author', '')}\n"
            document_context += f"File Path: {str(path)}\n"
            document_context += f"Summary: {summary}\n\n"

            for _, chunk in enumerate(self._splitter.split_text(md_text)):
                docs.append(
                    Document(
                        page_content=document_context + chunk,
                        metadata=metadata
                    )
                )
            # also, creating a document for summary:
            if summary:
                _info = {
                    "category": "Summary",
                    **metadata
                }
                docs.append(
                    Document(
                        page_content=f"**Summary:** {summary}",
                        metadata=_info
                    )
                )
            return docs
        else:
            return []
