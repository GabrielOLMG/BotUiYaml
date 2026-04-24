from pydantic import BaseModel, Field, model_validator


# =========================
# Action Find
# =========================

class FindRequest(BaseModel):
    debug: bool = Field(
        default=False,
        description="",
    )