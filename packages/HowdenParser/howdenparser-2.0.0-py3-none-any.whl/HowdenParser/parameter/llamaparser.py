
from typing import Literal
from pydantic import BaseModel

class Parameter(BaseModel):
    provider_and_model: str = "llamaparser:"
    result_type: Literal["md"] = "md"
    mode: bool = False