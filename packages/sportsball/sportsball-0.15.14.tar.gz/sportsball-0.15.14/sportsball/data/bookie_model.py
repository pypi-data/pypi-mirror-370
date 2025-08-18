"""The prototype class for a bookie."""

from typing import Literal

from pydantic import BaseModel, Field

from .field_type import TYPE_KEY, FieldType

BOOKIE_IDENTIFIER_COLUMN: Literal["identifier"] = "identifier"


class BookieModel(BaseModel):
    """The serialisable bookie class."""

    identifier: str = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL},
        alias=BOOKIE_IDENTIFIER_COLUMN,
    )
    name: str = Field(..., json_schema_extra={TYPE_KEY: FieldType.TEXT})
