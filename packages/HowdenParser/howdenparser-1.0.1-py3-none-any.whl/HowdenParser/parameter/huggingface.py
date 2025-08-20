from typing import Literal
from pydantic import BaseModel

class Parameter(BaseModel):
    model: str = "huggingface:HURIDOCS/pdf-segmentation"

