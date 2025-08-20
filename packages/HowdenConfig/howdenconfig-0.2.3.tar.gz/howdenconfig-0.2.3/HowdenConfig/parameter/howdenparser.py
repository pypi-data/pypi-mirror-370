from pydantic import BaseModel


class Parameter(BaseModel):
    pdf_path: str = "hest"
    split: bool = True
    llama_premium_mode: bool = True
