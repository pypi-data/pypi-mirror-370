import asyncio
from typing import List
from collections.abc import Callable
import importlib
from pathlib import Path, PurePath
from parrot.loaders import AbstractLoader, Document
from parrot.llms.vertex import VertexLLM
from ..flow import FlowComponent
from ...exceptions import ConfigError, ComponentError
from ...conf import (
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TEMPERATURE
)

class LangchainLoader(FlowComponent):
    """LangchainLoader.

    Overview:

    Getting a list of documents and convert into Langchain Documents.


        Example:

        ```yaml
        LangchainLoader:
            path: /home/ubuntu/symbits/lg/bot/products_positive
            source_type: Product-Top-Reviews
            loader: HTMLLoader
            chunk_size: 2048
            elements:
            - div: .product
        ```

    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        self.extensions: list = kwargs.pop('extensions', [])
        self.encoding: str = kwargs.get('encoding', 'utf-8')
        self.path: str = kwargs.pop('path', None)
        self.skip_directories: List[str] = kwargs.pop('skip_directories', [])
        self._chunk_size = kwargs.get('chunk_size', 2048)
        self._embed_size: int = kwargs.pop('embed_size', 768)
        self.source_type: str = kwargs.pop('source_type', 'document')
        self.doctype: str = kwargs.pop('doctype', 'document')
        # LLM (if required)
        self._llm = kwargs.pop('llm', None)
        super().__init__(
            loop=loop, job=job, stat=stat, **kwargs
        )
        self._device: str = kwargs.get('device', 'cpu')
        self._cuda_number: int = kwargs.get('cuda_device', 0)
        # Use caching to avoid instanciate several times same loader
        self._caching_loaders: dict = {}

    async def close(self):
        # Destroy effectively all Models.
        pass

    def get_default_llm(self):
        """Return a VertexLLM instance."""
        return VertexLLM(
            model=DEFAULT_LLM_MODEL,
            temperature=DEFAULT_LLM_TEMPERATURE,
            top_k=30,
            top_p=0.5,
        )

    async def start(self, **kwargs):
        await super().start(**kwargs)
        if self.path:
            if isinstance(self.path, str):
                self.path = self.mask_replacement_recursively(self.path)
                self.path = Path(self.path).resolve()
                if not self.path.exists():
                    raise ComponentError(
                        f"Langchain: {self.path} doesn't exists."
                    )
        else:
            raise ConfigError(
                "Provide at least one directory or filename in *path* attribute."
            )

    def _get_loader(self, suffix: str, **kwargs):
        """
        Get a Document Loader based on Prefix.
        TODO: a more automated way using importlib.
        """
        # Common Arguments
        args = {
            "markdown_splitter": self._md_splitter,
            "summarization_model": self.summarization_model,
            "device": self._device,
            "cuda_number": self._cuda_number,
            "source_type": self.source_type,
            "encoding": self.encoding,
            "llm": self._llm
        }

    def _load_loader(self, name: str, **kwargs) -> AbstractLoader:
        """Dynamically imports a loader class from the loaders module.

        Args:
            loader_name: The name of the loader class to import (e.g., 'QALoader').

        Returns:
            The imported loader class.
        """
        try:
            module_path = "parrot.loaders"
            module = importlib.import_module(module_path, package=__package__)
            cls = getattr(module, name)
            if cls:
                args = {
                    "device": self._device,
                    "cuda_number": self._cuda_number,
                    "source_type": self.source_type,
                    "encoding": self.encoding,
                    "llm": self._llm,
                    **kwargs
                }
                loader = cls(**args)
                print(':: LOADING LOADER > ', loader)
                self._caching_loaders[name] = loader
            return loader
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(
                f"Unable to load the loader '{name}': {e}"
            ) from e

    async def _load_document(self, path: PurePath) -> List[Document]:
        documents = []
        suffix = path.suffix
        if suffix in self._caching_loaders:
            loader = self._caching_loaders[suffix]
        else:
            loader = self._get_loader(suffix)
            self._caching_loaders[suffix] = loader
        async with loader as ld:
            documents = await ld.load(path)
        # split or not split?
        return documents

    async def run(self):
        documents = []
        if hasattr(self, 'loader'):
            loader = self._load_loader(self.loader, **self._attrs)
            async with loader as ld:
                ext = loader.supported_extensions()
                if self.path.is_dir():
                    if self.extensions:
                        # iterate over the files in the directory
                        for ext in self.extensions:
                            for item in self.path.glob(f'*{ext}'):
                                if item.is_file() and set(item.parts).isdisjoint(self.skip_directories):
                                    documents.extend(await ld.load(item))
                    else:
                        for item in self.path.glob('*.*'):
                            if item.is_file() and set(item.parts).isdisjoint(self.skip_directories):
                                documents.extend(await ld.load(item))
                else:
                    documents = await ld.load(self.path)
        else:
            if self.path.is_dir():
                # iterate over the files in the directory
                if self.extensions:
                    for ext in self.extensions:
                        for item in self.path.glob(f'*{ext}'):
                            if item.is_file() and set(item.parts).isdisjoint(self.skip_directories):
                                documents.extend(await self._load_document(item))
                else:
                    for item in self.path.glob('*.*'):
                        if item.is_file() and set(item.parts).isdisjoint(self.skip_directories):
                            documents.extend(await self._load_document(item))
            elif self.path.is_file():
                if self.path.suffix in self.extensions:
                    if set(self.path.parts).isdisjoint(self.skip_directories):
                        documents = await self._load_document(self.path)
            else:
                raise ValueError(
                    f"Langchain Loader: Invalid path: {self.path}"
                )
        self._result = documents
        self.add_metric('NUM_DOCUMENTS', len(documents))
        # return self._result
        return True
