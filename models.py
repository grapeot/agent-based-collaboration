from pydantic import BaseModel, Field
from typing import List, Optional

class SuggestRequest(BaseModel):
    knowledge_base: str = Field(..., description="The knowledge base content")
    text: str = Field(..., description="The user's input text")
    prompt: Optional[str] = Field(None, description="The prompt for the AI")

class ReplacementItem(BaseModel):
    task: str = Field(..., description="The identified task to be performed")
    replace_text: str = Field(..., description="The text to replace")

class SuggestResponse(BaseModel):
    status: str = Field(..., description="Status of the response: 'OK' or 'error'")
    error_message: Optional[str] = Field(None, description="Error message if status is 'error'")
    suggestion: Optional[str] = Field(None, description="AI-generated suggestion")
    replacements: Optional[List[ReplacementItem]] = Field(None, description="List of replacement items")