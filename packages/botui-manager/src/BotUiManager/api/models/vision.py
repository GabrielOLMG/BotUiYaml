from typing import Optional, Union
from pydantic import BaseModel, Field, model_validator


class SearchAreaPayload(BaseModel):
    row: Optional[Union[int, None]] = Field(None, description="The specific grid row to search within")
    column: Optional[Union[int, None]] = Field(None, description="The specific grid column to search within")
    grid_rows: Optional[int] = Field(3, description="How many horizontal slices the screen is divided into")
    grid_cols: Optional[int] = Field(3, description="How many vertical slices the screen is divided into")


class OCRPayload(BaseModel):
    image_path: str = Field(
        ...,
        description="absolute path to image"
    )

    text_target: Optional[str] = Field(
        None, 
        description="Text to try to locate in the image"
    )

    search_area: Optional[SearchAreaPayload] = Field(
        default_factory=SearchAreaPayload,
        description="Grid-based search area configuration"
    )


class TemplateMatchPayload(BaseModel):
    source_image: str = Field(
        ...,
        description="absolute path to image",
        example= "/Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/_debug/template_matching/source.png"
    )

    template_image: Optional[str] = Field(
        None, 
        example="/Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/_debug/template_matching/template.png",
        description="Image to try to locate in the image"
    )

    search_area: Optional[SearchAreaPayload] = Field(
        default_factory=SearchAreaPayload,
        description="Grid-based search area configuration"
    )
