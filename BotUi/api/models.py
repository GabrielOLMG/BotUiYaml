from pydantic import BaseModel, Field

class DebugDecision(BaseModel):
    action: str = Field(
        defauld="stop", 
        description="resume or stop"
    )  