"""The prototype class for a dividend."""

from typing import Literal

from pydantic import BaseModel, Field

from .field_type import TYPE_KEY, FieldType

DIVIDEND_POOL_COLUMN: Literal["pool"] = "pool"
DIVIDEND_COMBINATION_COLUMN: Literal["combination"] = "combination"
DIVIDEND_DIVIDEND_COLUMN: Literal["dividend"] = "dividend"


class DividendModel(BaseModel):
    """The serialisable dividend class."""

    pool: str = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL},
        alias=DIVIDEND_POOL_COLUMN,
    )
    combination: list[str] = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=DIVIDEND_COMBINATION_COLUMN,
    )
    dividend: float = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=DIVIDEND_DIVIDEND_COLUMN,
    )
