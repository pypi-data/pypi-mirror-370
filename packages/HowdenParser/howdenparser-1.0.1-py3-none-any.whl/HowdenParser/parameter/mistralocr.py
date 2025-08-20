from typing import Literal
from pydantic import BaseModel

class Parameter(BaseModel):
    provider_and_model: Literal["mistralocr:mistral-ocr-latest"] = "mistralocr:mistral-ocr-latest"