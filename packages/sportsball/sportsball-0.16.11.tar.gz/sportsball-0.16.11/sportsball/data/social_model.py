"""The prototype class for social."""

import datetime

from pydantic import BaseModel, Field

from .field_type import TYPE_KEY, FieldType


class SocialModel(BaseModel):
    """The serialisable social class."""

    network: str = Field(..., json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL})
    post: str = Field(..., json_schema_extra={TYPE_KEY: FieldType.TEXT})
    comments: int
    reposts: int
    likes: int
    views: int | None
    published: datetime.datetime
