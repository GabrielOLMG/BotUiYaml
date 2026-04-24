from pydantic import BaseModel, Field, model_validator

class OCRPayload(BaseModel):
    debug: bool = Field(
        default=False,
    )
    
class OCRResult(BaseModel):
    name: str = Field(
        ...,
        description="Step Identifier",
    )


class TemplateMatchPayload(BaseModel):
    debug: bool = Field(
        default=False,
    )
    
class TemplateMatchResult(BaseModel):
    name: str = Field(
        ...,
    )