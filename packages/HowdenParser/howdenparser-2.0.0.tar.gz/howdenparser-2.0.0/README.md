# OCR & LLM Parser

A powerful Python package for parsing and processing documents using multiple providers:
- **Mistral OCR** — Extracts text from PDFs and images with high accuracy.
- **LangChain** — Processes or summarizes text using LLMs.
- **Llama Parser** — Advanced parsing with Markdown or text output.
- **HuggingFace** — OCR and document question answering with transformer models.

The package provides a **unified interface** so you can switch between providers easily using a **factory pattern**.

---

## 🚀 Features
- Extract text from PDFs or images
- Summarize or process text using LLMs
- Support for **Markdown** or **plain text** output
- Plug-and-play factory to switch providers without changing much code
- Handles environment variable loading for API keys automatically

---

# 🔑 Tokens

Create a .env file in your project root and add the API keys for the services you want to use.

### Mistral OCR
MISTRAL-OCR-API-TOKEN=your_mistral_api_key

### Llama Parser
LLAMA-PARSER-API-TOKEN=your_llama_parser_api_key

### HuggingFace
HF-API-TOKEN=your_huggingface_api_key

Only include the keys for the providers you plan to use.

---

# 🛠️ Usage

from HowdenParser import ParserFactory

from pathlib import Path

parser = ParserFactory.get_parser("mistralocr:", result_type="md")
text = parser.parse(Path("document.pdf"))
print(text)

if HowdenConfig package being used

config: Config = Config(parameter=Parameter())

parser = Parser.create(config.parameter)

text = parser.parse(Path("document.pdf"))

