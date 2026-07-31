"""Modelos del endpoint de resumenes para redes sociales."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

TWITTER_MAX = 280

Platform = Literal["twitter", "linkedin", "instagram", "facebook"]


class SocialRequest(BaseModel):
    article_title: str = Field(min_length=2)
    article_content: str = Field(min_length=50)
    target_platforms: list[Platform] = Field(
        default_factory=lambda: ["twitter", "linkedin", "instagram", "facebook"]
    )


class TwitterContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    hashtags: list[str]

    @model_validator(mode="after")
    def _enforce_limit(self) -> "TwitterContent":
        self.text = self.text.strip()[:TWITTER_MAX]
        return self


class LinkedInContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    hashtags: list[str]


class InstagramContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    caption: str
    hashtags: list[str]


class FacebookContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    hashtags: list[str]


class SocialResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    twitter: TwitterContent | None = None
    linkedin: LinkedInContent | None = None
    instagram: InstagramContent | None = None
    facebook: FacebookContent | None = None
