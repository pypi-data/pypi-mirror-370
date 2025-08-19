from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from .abstract import AbstractLoader
from pathlib import Path, PurePath
from markdownify import markdownify as md
from datetime import datetime


class HTMLLoader(AbstractLoader):
    """
    Loader for HTML files to convert into Langchain Documents.

    Processes HTML files, extracts relevant content, converts to Markdown,
    and associates metadata with each document.
    """

    _extension = ['.html', '.htm']

    def __init__(self, **kwargs):
        """Initialize the HTMLLoader."""
        self.elements: list = kwargs.pop('elements', [])
        super().__init__(**kwargs)

    async def _load_document(self, path: PurePath) -> list[Document]:
        """
        Load an HTML file and convert its content into Langchain documents.

        Args:
            path (PurePath): Path to the HTML file.

        Returns:
            list[Document]: A list of Langchain documents with content and metadata.
        """
        documents = []

        # Check if the file exists and is valid
        if not self._check_path(path):
            raise ValueError(f"File {path} does not exist or is not a valid HTML file.")

        # Read and parse the HTML file
        with open(path, 'r', encoding=self.encoding) as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract the entire <body> content or
        # Determine the top-level element to process
        top_element = soup.body or soup
        if not top_element:
            raise ValueError(
                "The HTML file does not contain a <body> or Top element tag."
            )

        extracted_elements = []

        if self.elements:
            # Extract content from specific elements
            for element in self.elements:
                for tag, selector in element.items():
                    extracted_elements.extend(top_element.find_all(tag, class_=selector.lstrip('.')))

        if not extracted_elements:
            extracted_elements = [top_element]

        # Process each extracted element
        for elem in extracted_elements:
            # Get the plain text content
            text = elem.get_text(separator="\n", strip=True)

            # Generate a summary for the extracted text
            try:
                summary = self.get_summary_from_text(text, use_gpu=True)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error generating summary: {e}")
                summary = "Summary not available."

            # Create document-level context
            document_context = f"File Name: {path.name}\n"
            document_context += f"Document Type: {self.doctype}\n"
            document_context += f"Source Type: {self._source_type}\n"
            document_context += f"Element: {elem.name}\n"
            document_context += f"Summary: {summary}\n\n"

            # Convert the entire <body> to Markdown for better structure
            markdown_content = md(str(elem))

            # Metadata preparation
            document_meta = self.create_metadata(
                path=path,
                doctype=self.doctype,
                source_type=self._source_type,
                summary=summary,
                doc_metadata={
                    "type": "html",
                    "category": self.category,
                }
            )

            # Create a single Langchain Document with the full body content
            document = Document(
                page_content=document_context + markdown_content,
                metadata=document_meta
            )
            documents.append(document)

            # splitting the content:
            for chunk in self.markdown_splitter.split_text(text):
                _idx = {
                    **document_meta
                }
                # Create a Langchain Document
                documents.append(
                    Document(
                        page_content=document_context + chunk,
                        metadata=_idx
                    )
                )
        return documents
