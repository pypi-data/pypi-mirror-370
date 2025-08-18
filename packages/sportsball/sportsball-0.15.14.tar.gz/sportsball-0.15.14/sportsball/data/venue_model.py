"""The prototype class for a venue."""

from typing import Literal

from pydantic import BaseModel, Field

from .address_model import VERSION as ADDRESS_VERSION
from .address_model import AddressModel
from .delimiter import DELIMITER
from .field_type import TYPE_KEY, FieldType

VENUE_IDENTIFIER_COLUMN: Literal["identifier"] = "identifier"
VENUE_ADDRESS_COLUMN: Literal["address"] = "address"
VENUE_IS_TURF_COLUMN: Literal["is_turf"] = "is_turf"
VENUE_IS_DIRT_COLUMN: Literal["is_dirt"] = "is_dirt"
VERSION = DELIMITER.join(["0.0.1", ADDRESS_VERSION])


class VenueModel(BaseModel):
    """The serialisable venue class."""

    identifier: str = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL},
        alias=VENUE_IDENTIFIER_COLUMN,
    )
    name: str = Field(..., json_schema_extra={TYPE_KEY: FieldType.TEXT})
    address: AddressModel | None = Field(..., alias=VENUE_ADDRESS_COLUMN)
    is_grass: bool | None
    is_indoor: bool | None
    is_turf: bool | None = Field(..., alias=VENUE_IS_TURF_COLUMN)
    is_dirt: bool | None = Field(..., alias=VENUE_IS_DIRT_COLUMN)
    version: str = Field(..., json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL})
