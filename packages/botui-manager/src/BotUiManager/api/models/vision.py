from typing import Optional
from pydantic import BaseModel, Field, model_validator

class OCRPayload(BaseModel):
    image_path: str = Field(
        ...,
        description="absolute path to image"
    )

    text_target: Optional[str] = Field(
        None, 
        description="Text to try to locate in the image"
    )

    # side: str = Field(
    #     description=""
    # )
    
    # position: str = Field(
    #     defult=0,
    #     description=""
    # )
class OCRResult(BaseModel):
    name: str = Field(
        ...,
        description="Step Identifier",
    )


class TemplateMatchPayload(BaseModel):
    image_path: bool = Field(
        ...,
        description="absolute path to image"

    )
    
class TemplateMatchResult(BaseModel):
    name: str = Field(
        ...,
    )