from abc import ABC, abstractmethod
from typing import Union, List, Optional
from collections.abc import Callable
from datetime import datetime
from pathlib import Path, PurePath
import torch
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import (
    TokenTextSplitter
)
from langchain_huggingface import HuggingFacePipeline
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    pipeline
)
from langchain_core.prompts import PromptTemplate
from navconfig.logging import logging
from navigator.libs.json import JSONContent  # pylint: disable=E0611
from parrot.llms.vertex import VertexLLM
from ....conf import (
    EMBEDDING_DEVICE,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TEMPERATURE,
)

class AbstractLoader(ABC):
    """
    Abstract class for Document loaders.
    """
    _extension: List[str] = []

    def __init__(
        self,
        tokenizer: Union[str, Callable] = None,
        text_splitter: Union[str, Callable] = None,
        summarizer: Union[str, Callable] = None,
        markdown_splitter: Union[str, Callable] = None,
        source_type: str = 'file',
        doctype: Optional[str] = 'document',
        device: str = None,
        cuda_number: int = 0,
        llm: Callable = None,
        **kwargs
    ):
        self.tokenizer = tokenizer
        self._summary_model = summarizer
        self.text_splitter = text_splitter
        self.markdown_splitter = markdown_splitter
        self.doctype = doctype
        self.logger = logging.getLogger(
            f"Loader.{self.__class__.__name__}"
        )
        self.path = kwargs.pop('path', None)
        self._source_type = source_type
        # LLM (if required)
        self._llm = llm
        # JSON encoder:
        self._encoder = JSONContent()
        self.device_name = device
        self.cuda_number = cuda_number
        self._device = None
        self.encoding: str = kwargs.get('encoding', 'utf-8')
        self.summarization_model = kwargs.get(
            'summarization_model',
            "facebook/bart-large-cnn"
        )
        self._no_summarization = kwargs.get('no_summarization', False)
        self._translation = kwargs.get('translation', False)
        self.category: str = kwargs.get('category', 'document')

    async def __aenter__(self):
        # Cuda Device:
        self._device = self._get_device(
            self.device_name,
            self.cuda_number
        )
        return self

    def supported_extensions(self):
        return self._extension

    async def __aexit__(self, *exc_info):
        self.post_load()

    def post_load(self):
        self.tokenizer = None  # Reset the tokenizer
        self.text_splitter = None  # Reset the text splitter
        torch.cuda.synchronize()  # Wait for all kernels to finish
        torch.cuda.empty_cache()  # Clear unused memory

    def _get_device(self, device_type: str = None, cuda_number: int = 0):
        """Get Default device for Torch and transformers.

        """
        if device_type == 'cpu':
            return torch.device('cpu')
        elif device_type == 'cuda':
            return torch.device(f'cuda:{cuda_number}')
        else:
            if torch.cuda.is_available():
                # Use CUDA GPU if available
                return torch.device(f'cuda:{cuda_number}')
            if torch.backends.mps.is_available():
                # Use CUDA Multi-Processing Service if available
                return torch.device("mps")
            if EMBEDDING_DEVICE == 'cuda':
                return torch.device(f'cuda:{cuda_number}')
            else:
                return torch.device(EMBEDDING_DEVICE)

    def _check_path(
        self,
        path: PurePath,
        suffix: Optional[List[str]] = None
    ) -> bool:
        """Check if the file path exists.
        Args:
            path (PurePath): The path to the file.
        Returns:
            bool: True if the file exists, False otherwise.
        """
        if isinstance(path, str):
            path = Path(path).resolve()
        if not suffix:
            suffix = self._extension
        return path.exists() and path.is_file() and path.suffix in suffix

    def create_metadata(
        self,
        path: Union[str, PurePath],
        doctype: str = 'document',
        source_type: str = 'source',
        doc_metadata: Optional[dict] = None,
        summary: Optional[str] = '',
        **kwargs
    ):
        if not doc_metadata:
            doc_metadata = {}
        if isinstance(path, PurePath):
            origin = path.name
            url = f'file://{path.name}'
            filename = path
        else:
            origin = path
            url = path
            filename = f'file://{path}'
        metadata = {
            "url": url,
            "source": origin,
            "filename": str(filename),
            "type": doctype,
            "question": '',
            "answer": '',
            "summary": summary,
            "source_type": source_type,
            "created_at": datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
            "category": self.category,
            "document_meta": {
                **doc_metadata
            },
            **kwargs
        }
        return metadata

    def get_default_llm(self):
        """Return a VertexLLM instance."""
        return VertexLLM(
            model=DEFAULT_LLM_MODEL,
            temperature=DEFAULT_LLM_TEMPERATURE,
            top_k=30,
            top_p=0.5,
        )

    def get_summary_from_text(self, text: str, use_gpu: bool = False) -> str:
        """
        Get a summary of a text.
        """
        if not text:
            # NO data to be summarized
            return ''
        # splitter = TokenTextSplitter(
        #     chunk_size=2048,
        #     chunk_overlap=100,
        # )
        prompt_template = """Write a summary of the following, please also identify the main theme:
        {text}
        SUMMARY:"""
        prompt = PromptTemplate.from_template(prompt_template)
        refine_template = (
            "Your job is to produce a final summary\n"
            "We have provided an existing summary up to a certain point: {existing_answer}\n"
            "We have the opportunity to refine the existing summary"
            "(only if needed) with some more context below.\n"
            "------------\n"
            "{text}\n"
            "------------\n"
            "Given the new context, refine the original summary adding more explanation."
            "If the context isn't useful, return the original summary."
        )
        refine_prompt = PromptTemplate.from_template(refine_template)
        # if self._llm:
        #     llm = self._llm
        # else:
        #     llm = self.get_summarization_model(
        #         self.summarization_model,
        #         use_gpu=use_gpu
        #     )
        # if not llm:
        #     return ''
        llm = self.get_default_llm()
        llm = llm.get_llm()
        summarize_chain = load_summarize_chain(
            llm=llm,
            chain_type="refine",
            question_prompt=prompt,
            refine_prompt=refine_prompt,
            return_intermediate_steps=False,
            input_key="input_documents",
            output_key="output_text",
        )
        doc = Document(page_content=text)
        try:
            summary = summarize_chain.invoke(
                {"input_documents": [doc]}, return_only_outputs=True
            )
            return summary.get('output_text', '')
        except Exception as e:
            print('ERROR in get_summary_from_text:', e)
            return ""

    def get_translator(self, model_name: str = 'Helsinki-NLP/opus-mt-en-es'):
        if not self._translation:
            return None
        trans_model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            # device_map="auto",
            # torch_dtype=torch.bfloat16,
            trust_remote_code=True
        )
        trans_tokenizer = AutoTokenizer.from_pretrained(model_name)
        translator = pipeline(
            "translation",
            model=trans_model,
            tokenizer=trans_tokenizer,
            batch_size=True,
            max_new_tokens=500,
            min_new_tokens=300,
            use_fast=True
        )
        return translator

    def get_summarization_model(
        self,
        model_name: str = 'facebook/bart-large-cnn',
        use_gpu: bool = False
    ):
        if self._no_summarization is True:
            return None
        if not self._summary_model:
            summarize_model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                # torch_dtype=torch.float32,
                torch_dtype=torch.bfloat16,
                trust_remote_code=True
            )
            if use_gpu:
                # summarize_model.to(0)
                summarize_model.cuda()
            summarize_tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                padding_side="left"
            )
            pipe_summary = pipeline(
                "summarization",
                model=summarize_model,
                tokenizer=summarize_tokenizer,
                # device='cuda:0',
                # batch_size=True,
                max_new_tokens=256,
                # min_new_tokens=300,
                use_fast=True
            )
            self._summary_model = HuggingFacePipeline(
                model_id=model_name,
                pipeline=pipe_summary,
                verbose=True
            )
        return self._summary_model

    def resolve_paths(self, path: Union[str, PurePath, List[PurePath]]) -> List[Path]:
        """
        Resolve the input path into a list of file paths.
        Handles lists, directories, glob patterns, and single file paths.

        Args:
            path (Union[str, PurePath, List[PurePath]]): Input path(s).

        Returns:
            List[Path]: A list of resolved file paths.
        """
        resolved_paths = []

        if isinstance(path, str):
            if "*" in path:
                # Glob pattern
                resolved_paths = list(Path().glob(path))
            else:
                # Single path as string
                resolved_paths = [Path(path)]
        elif isinstance(path, PurePath):
            # Single Path
            resolved_paths = [Path(path)]
        elif isinstance(path, list):
            # List of paths
            resolved_paths = [Path(p) for p in path]

        final_paths = []
        for p in resolved_paths:
            if p.is_dir():
                # Add all matching files in the directory
                if self._extension:
                    for ext in self._extension:
                        final_paths.extend(p.glob(f"*{ext}"))
                else:
                    final_paths.extend(p.glob("*"))
            elif p.is_file():
                final_paths.append(p)

        return final_paths

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
                docs.extend(await self._load_document(p))
        return docs

    async def _load_document(self, path: Path) -> List:
        """
        Abstract method for loading a document.

        Args:
            path (Path): The path to the file.

        Returns:
            List: A list of Langchain documents.
        """
        pass
