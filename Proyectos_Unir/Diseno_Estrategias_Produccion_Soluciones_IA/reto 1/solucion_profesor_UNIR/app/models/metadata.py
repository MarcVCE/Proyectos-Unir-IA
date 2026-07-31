"""Modelos del endpoint de metadatos SEO (meta titles y meta descriptions)."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

META_TITLE_MAX = 60
META_DESCRIPTION_MAX = 160


class MetadataRequest(BaseModel):
    article_title: str = Field(min_length=2)
    main_keyword: str = Field(min_length=2)
    article_excerpt: str = Field(default="", description="Extracto del articulo")


class MetaTitle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    char_count: int

    @model_validator(mode="after")
    def _enforce_limit(self) -> "MetaTitle":
        # Garantia dura del limite SEO aunque el modelo se pase.
        self.text = self.text.strip()[:META_TITLE_MAX]
        self.char_count = len(self.text)
        return self


class MetaDescription(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    char_count: int

    @model_validator(mode="after")
    def _enforce_limit(self) -> "MetaDescription":
        self.text = self.text.strip()[:META_DESCRIPTION_MAX]
        self.char_count = len(self.text)
        return self


class MetadataResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta_titles: list[MetaTitle] = Field(description="3 a 5 variantes de meta title")
    meta_descriptions: list[MetaDescription] = Field(
        description="3 a 5 variantes de meta description"
    )
