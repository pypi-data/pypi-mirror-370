from pydantic import BaseModel

class RedactionRule(BaseModel):
    pattern: str  # Regex pattern
    replacement: str  # Replacement text
    description: str 