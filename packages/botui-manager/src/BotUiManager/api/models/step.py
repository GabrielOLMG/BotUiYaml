
from pydantic import BaseModel, Field, model_validator

class StepPayload(BaseModel):
    name: str = Field(
        ...,
        description="Step Identifier",
    )
    parameters: dict = Field(
        ...,
        description="Step Identifier",
        example={
            "text": "FIXED TEXT FIND",
        }
    )
    debug: bool = Field(
        ...,
        description="If enabled, the step will pause if any errors occur, allowing for possible parameter modifications.",
    )
    