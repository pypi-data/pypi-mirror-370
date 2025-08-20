from abc import ABC, abstractmethod
import os
import logging
from pathlib import Path
from PyPDF2 import PdfReader
import dotenv
import logging
from inspect import signature

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


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
    def available_parsers(cls) -> None:
        """Print registered parsers and their init arguments."""
        import inspect
        result = {}
        for name, parser_cls in BaseParser._registry.items():
            sig = inspect.signature(parser_cls.__init__)
            result[name] = [p for p in sig.parameters if p != "self"]
        result.pop('', None)
        for key, values in result.items():
            print(f"{key} with parameters: {values}")

    @classmethod
    def create(cls, config_or_dict: "Parameter | dict", **kwargs) -> BaseParser:
        """
        Dynamically create parser instances from a config object or dict.
        Only passes arguments accepted by the parser constructor.
        """
        # Convert Parameter -> dict if needed
        if hasattr(config_or_dict, "model_dump"):
            config_dict = config_or_dict.model_dump()
        elif isinstance(config_or_dict, dict):
            config_dict = config_or_dict
        else:
            raise TypeError("Expected Parameter instance or dict for config_or_dict")

        if "provider_and_model" not in kwargs and "provider_and_model" not in config_dict:
            raise ValueError("provider_and_model must be specified")

        # Merge dict + kwargs (kwargs take precedence)
        merged_args = {**config_dict, **kwargs}

        # Extract provider/model info
        provider_and_model = merged_args.get("provider_and_model")
        provider, model = provider_and_model.split(":")
        provider = provider.lower()
        model = model.lower()

        if provider not in BaseParser._registry:
            raise ValueError(f"Unknown parser '{provider}'. Available: {list(BaseParser._registry)}")

        parser_cls = BaseParser._registry[provider]

        # Inspect constructor and only pass valid arguments
        sig = signature(parser_cls.__init__)
        valid_args = {k: v for k, v in merged_args.items() if k in sig.parameters and k != "self"}

        # Auto-insert 'model' if required
        if "model" in sig.parameters and "model" not in valid_args:
            valid_args["model"] = model

        # Auto-insert 'provider_and_model' if required
        if "provider_and_model" in sig.parameters and "provider_and_model" not in valid_args:
            valid_args["provider_and_model"] = provider_and_model

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
    def __init__(self, provider_and_model: str):
        from langchain.llms import OpenAI
        self.model = provider_and_model.split(":")[1]
        self.model = OpenAI(model_name=self.model)

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
    def __init__(self, provider_and_model: str) -> None:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel

        api_key = os.getenv("HF-API-TOKEN")
        if not api_key:
            raise EnvironmentError("Missing HF-API-TOKEN in .env file.")

        model_name = provider_and_model.split(":")[1]
        logger.info(f"Loading Hugging Face OCR model: {model_name}")

        self.processor = TrOCRProcessor.from_pretrained(model_name, token=api_key)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name, token=api_key)

        logger.info("Model and processor loaded successfully.")

    def parse(self, file_path: Path) -> str:
        from pdf2image import convert_from_path
        logger.info(f"Converting PDF to images: {file_path}")
        pages = convert_from_path(file_path, dpi=300)
        logger.info(f"PDF conversion complete. Total pages: {len(pages)}")

        all_text = ""
        for i, page in enumerate(pages, start=1):
            logger.info(f"Running OCR on page {i}/{len(pages)}")
            pixel_values = self.processor(page, return_tensors="pt").pixel_values
            generated_ids = self.model.generate(pixel_values)
            text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            all_text += text + "\n"
            logger.debug(f"OCR text (page {i}): {text[:100]}...")  # preview first 100 chars

        logger.info("OCR completed for all pages.")
        return all_text


