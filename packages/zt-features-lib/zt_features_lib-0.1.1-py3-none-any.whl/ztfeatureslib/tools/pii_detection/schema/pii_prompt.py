from pydantic import BaseModel

class PIIPromptRequest(BaseModel):
    prompt: str
