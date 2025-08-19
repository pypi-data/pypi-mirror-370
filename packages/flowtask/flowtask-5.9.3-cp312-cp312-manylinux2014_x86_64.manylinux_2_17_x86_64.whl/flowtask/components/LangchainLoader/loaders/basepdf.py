from abc import abstractmethod
from typing import List, Union
from pathlib import Path, PurePath
from markdownify import markdownify as md
from langchain.docstore.document import Document
from .abstract import AbstractLoader


class BasePDF(AbstractLoader):
    """
    Base Abstract loader for all PDF-file Loaders.
    """
    _extension = ['.pdf']
    chunk_size = 768

    def __init__(self, **kwargs):
        self._lang = 'eng'
        super().__init__(**kwargs)

    @abstractmethod
    def _load_pdf(self, path: Path) -> list:
        """
        Load a PDF file using Fitz.

        Args:
            path (Path): The path to the PDF file.

        Returns:
            list: A list of Langchain Documents.
        """
        pass

    async def load(self, path: Union[str, PurePath, List[PurePath]]) -> List[Document]:
        """Load data from a source and return it as a Langchain Document.

        Args:
            path (Union[str, PurePath, List[PurePath]]): The source of the data.

        Returns:
            List[Document]: A list of Langchain Documents.
        """
        self.logger.info(
            f"Loading file: {path}"
        )
        paths = self.resolve_paths(path)
        docs = []
        for p in paths:
            if p.exists():
                docs.extend(self._load_pdf(p))
        return docs
