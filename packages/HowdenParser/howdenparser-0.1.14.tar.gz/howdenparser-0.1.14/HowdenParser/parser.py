from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os
from pathlib import Path
import logging
from PyPDF2 import PdfReader

load_dotenv()

class BaseParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> dict:
        pass


class MistralOCRParser(BaseParser):
    def __init__(self, model: str) -> None:
        from mistralai import Mistral
        self.model = model
        self.current_cost: float = 0.0
        self.total_cost_euro: float = 0.0

        name = "MISTRAL-OCR-API-TOKEN"
        api_key = os.getenv(name)
        if not api_key:
            raise EnvironmentError(f"Missing {name} in .env file.")

        self.client = Mistral(api_key=api_key)

    def parse(self, file_path: Path) -> str:
        def upload_pdf(filename):
            uploaded_pdf = self.client.files.upload(
            file={
            "file_name": filename,
                "content": open(filename, "rb"),
            },
            purpose="ocr"
            )
            signed_url = self.client.files.get_signed_url(file_id=uploaded_pdf.id)
            return signed_url.url

        ocr_response = self.client.ocr.process(
            model=self.model,
            document={
            "type": "document_url",
            "document_url": upload_pdf(file_path),
            },
            include_image_base64=True,
            )

        self.current_cost = 1/1000 * self._count_pages(file_path)
        self.total_cost_euro += self.current_cost

        return "\n".join(doc.markdown for doc in ocr_response.pages)

    @staticmethod
    def _count_pages(file_path: Path) -> int:
        reader = PdfReader(str(file_path))
        return len(reader.pages)



class LangChainParser(BaseParser):
    def __init__(self, model: str):
        from langchain.llms import OpenAI
        self.model_name = model
        self.model = OpenAI(model_name=model)

    def parse(self, text: str) -> dict:
        response = self.model(text)
        return {"source": "LangChain", "output": response}


class LlamaParser(BaseParser):
    def __init__(self, result_type: str, mode: bool) -> None:
        logging.info("Initializing LlamaParser...")
        logging.info("Loading LlamaParse package...")

        from llama_parse import LlamaParse, ResultType

        if result_type.lower() == "md" or result_type.lower() == "markdown":
            self.result_type = ResultType.MD

        name = "LLAMA-PARSER-API-TOKEN"
        api_key = os.getenv(name)
        if not api_key:
            raise EnvironmentError(f"Missing {name} in .env file.")

        logging.info("Initializing LlamaParse parser...")
        self.parser = LlamaParse(
            api_key=api_key,
            result_type=self.result_type,
            premium_mode=mode
        )
        logging.info("LlamaParser initialized successfully.")

    def parse(self, file_path: Path) -> str:
        logging.info(f"Parsing file: {file_path}")
        documents = self.parser.load_data(str(file_path))
        text = "\n".join(doc.text for doc in documents)
        logging.info(f"Parsing completed. Extracted {len(documents)} documents.")
        return text

class HuggingFaceParser(BaseParser):
    def __init__(self, model: str, result_type: str) -> None:
        from transformers import pipeline

        if result_type.lower() in ("md", "markdown"):
            self.result_type = "markdown"
        else:
            self.result_type = "text"

        name = "HF-API-TOKEN"
        self.api_key = os.getenv(name)
        if not self.api_key:
            raise EnvironmentError(f"Missing {name} in .env file.")

        # Example model: microsoft/layoutlmv3-base-finetuned-docvqa
        self.parser = pipeline(
            task="document-question-answering",
            model=model,
            use_auth_token=self.api_key
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

        if self.result_type == "markdown":
            return "\n\n".join(output_parts)
        else:
            return " ".join(output_parts)

# === Step 3: Dynamic factory using string input ===
class ParserFactory:
    @staticmethod
    def get_parser(provider_model: str, **kwargs) -> BaseParser:
        provider = provider_model.partition(":")[0].lower()
        model = provider_model.partition(":")[2]
        if provider == "langchain":
            return LangChainParser(model=model)
        elif provider == "llamaparser":
            return LlamaParser(kwargs["result_type"], kwargs["mode"])
        elif provider == "huggingface":
            return HuggingFaceParser(model=model, **kwargs)
        elif provider == "mistralocr":
            return MistralOCRParser(model)
        else:
            raise ValueError(f"Unknown parser type: {provider_model}")

