
from pathlib import PurePath
from typing import List
import pandas as pd
from langchain.docstore.document import Document
from .abstract import AbstractLoader


class QAFileLoader(AbstractLoader):
    """
    Question and Answers File based on Excel, coverted to Langchain Documents.
    """
    _extension = ['.xlsx']
    chunk_size = 768

    def __init__(
        self,
        columns: list = ['Question', 'Answer'],
        **kwargs
    ):
        super().__init__(**kwargs)
        self._columns = columns

    def _load_document(self, path: PurePath) -> list:
        df = pd.read_excel(path)
        q = self._columns[0]
        a = self._columns[1]
        docs = []
        for idx, row in df.iterrows():
            # Question Document
            document_meta = {
                "question": row[q],
                "answer": row[a],
            }
            metadata = self.create_metadata(
                path=path,
                doctype=self.doctype,
                source_type=self._source_type,
                summary=f"Question: {row[q]}?: **{row[a]}**",
                doc_metadata=document_meta,
                type="QA",
                question=row[q],
                answer=row[a],
            )
            doc = Document(
                page_content=f"**Question:** {row[q]}: **Answer:** {row[a]}",
                metadata=metadata,
            )
            docs.append(doc)
        return docs

    async def load(self, path: PurePath) -> List[Document]:
        """Load data from a source and return it as a Langchain Document.

        Args:
            path (Path): The source of the data.

        Returns:
            List[Document]: A list of Langchain Documents.
        """
        self.logger.info(
            f"Loading Excel FAQ file: {path}"
        )
        docs = []
        if path.exists():
            docs = self._load_document(path)
        return docs
