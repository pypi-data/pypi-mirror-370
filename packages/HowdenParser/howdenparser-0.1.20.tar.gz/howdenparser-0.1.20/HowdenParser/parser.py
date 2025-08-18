from abc import ABC, abstractmethod
import os
import logging
from pathlib import Path
from PyPDF2 import PdfReader
import dotenv

dotenv.load_dotenv()


class BaseParser(ABC):
    _registry: dict[str, type["BaseParser"]] = {}

    def __init_subclass__(cls, name: str | None = None, **kwargs):
        """Automatically register subclasses under a key."""
        super().__init_subclass__(**kwargs)
        key = name or cls.__name__.lower().replace("parser", "")
        BaseParser._registry[key] = cls
        BaseParser._registry.pop("", None)

    @abstractmethod
    def parse(self, text: str):
        pass


class Parser(BaseParser):
    """Factory + registry interface for all parsers."""

    @classmethod
    def available_parsers(cls) -> dict[str, list[str]]:
        """Return registered parsers and their init arguments."""
        import inspect
        result = {}
        for name, parser_cls in BaseParser._registry.items():
            sig = inspect.signature(parser_cls.__init__)
            result[name] = [p for p in sig.parameters if p != "self"]
        result.pop('', None)
        return result

    @classmethod
    def create(cls, config: dict | None = None, **kwargs) -> BaseParser:
        provider = kwargs["provider_and_model"].split(":")[0].lower()
        model = kwargs["provider_and_model"].split(":")[1].lower()
        if provider not in BaseParser._registry:
            raise ValueError(f"Unknown parser '{provider}'. "
                             f"Available: {cls.available_parsers()}")

        parser_cls = BaseParser._registry[provider]
        import inspect
        merged_args = {**(config or {}), **kwargs}
        if "model" in inspect.signature(parser_cls.__init__).parameters:
            merged_args["model"] = model

        # Remove keys not in constructor
        sig = inspect.signature(parser_cls.__init__)
        valid_args = {k: v for k, v in merged_args.items() if k in sig.parameters and k != "self"}

        return parser_cls(**valid_args)




    @abstractmethod
    def parse(self, text: str):
        pass


# --- Parsers ---
class MistralOCRParser(BaseParser, name="mistralocr"):
    def __init__(self,provider_and_model:str) -> None:
        from mistralai import Mistral

        self.model = provider_and_model.split(":")[1]
        self.current_cost: float = 0.0
        self.total_cost_euro: float = 0.0

        api_key = os.getenv("MISTRAL-OCR-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing MISTRAL-OCR-API-TOKEN in .env file.")

        self.client = Mistral(api_key=api_key)

    def parse(self, file_path: Path) -> str:
        def upload_pdf(filename):
            uploaded_pdf = self.client.files.upload(
                file={"file_name": filename, "content": open(filename, "rb")},
                purpose="ocr"
            )
            signed_url = self.client.files.get_signed_url(file_id=uploaded_pdf.id)
            return signed_url.url

        ocr_response = self.client.ocr.process(
            model=self.model,
            document={"type": "document_url", "document_url": upload_pdf(file_path)},
            include_image_base64=True,
        )

        self.current_cost = 1 / 1000 * self._count_pages(file_path)
        self.total_cost_euro += self.current_cost

        return "\n".join(doc.markdown for doc in ocr_response.pages)

    @staticmethod
    def _count_pages(file_path: Path) -> int:
        reader = PdfReader(str(file_path))
        return len(reader.pages)


class LangChainParser(BaseParser, name="langchain"):
    def __init__(self, model: str):
        from langchain.llms import OpenAI
        self.model_name = model
        self.model = OpenAI(model_name=model)

    def parse(self, text: str) -> dict:
        response = self.model(text)
        return {"source": "LangChain", "output": response}


class LlamaParser(BaseParser, name="llamaparser"):
    def __init__(self, result_type: str, mode: bool) -> None:
        logging.info("Initializing LlamaParser...")

        from llama_parse import LlamaParse, ResultType

        if result_type.lower() in ("md", "markdown"):
            self.result_type = ResultType.MD

        api_key = os.getenv("LLAMA-PARSER-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing LLAMA-PARSER-API-TOKEN in .env file.")

        self.parser = LlamaParse(api_key=api_key, result_type=self.result_type, premium_mode=mode)

    def parse(self, file_path: Path) -> str:
        documents = self.parser.load_data(str(file_path))
        return "\n".join(doc.text for doc in documents)


class HuggingFaceParser(BaseParser, name="huggingface"):
    def __init__(self, model: str, result_type: str) -> None:
        from transformers import pipeline

        if result_type.lower() in ("md", "markdown"):
            self.result_type = "markdown"
        else:
            self.result_type = "text"

        api_key = os.getenv("HF-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing HF-API-TOKEN in .env file.")

        self.parser = pipeline(
            task="document-question-answering",
            model=model,
            use_auth_token=api_key
        )

    def parse(self, file_path: Path) -> str:
        import fitz
        pdf_doc = fitz.open(file_path)
        output_parts = []

        for page in pdf_doc:
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            response = self.parser(img_bytes, question="Extract all text")
            if response and "answer" in response[0]:
                output_parts.append(response[0]["answer"])

        return "\n\n".join(output_parts) if self.result_type == "markdown" else " ".join(output_parts)


