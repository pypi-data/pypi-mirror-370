"""The prototype class defining how to interface to the league."""

# pylint: disable=line-too-long
import datetime
import logging
import threading
from typing import Any, Iterator, get_args, get_origin

import pandas as pd
import tqdm
from flatten_json import flatten  # type: ignore
from pydantic import BaseModel
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from .address_model import ADDRESS_TIMEZONE_COLUMN
from .delimiter import DELIMITER
from .field_type import FieldType
from .game_model import GAME_DT_COLUMN, VENUE_COLUMN_PREFIX, GameModel
from .league import League
from .model import Model
from .venue_model import VENUE_ADDRESS_COLUMN

LEAGUE_COLUMN = "league"
SHUTDOWN_FLAG = threading.Event()


def _clear_column_list(df: pd.DataFrame) -> pd.DataFrame:
    def has_list(x):
        return any(isinstance(i, list) for i in x)

    mask = df.apply(has_list)
    cols = df.columns[mask].tolist()
    return df.drop(columns=cols)


def _reduce_memory_usage(df: pd.DataFrame) -> pd.DataFrame:
    logging.info(df.memory_usage(deep=True))
    for col in df.columns:
        if df[col].dtype == "int64":
            df[col] = pd.to_numeric(df[col], downcast="integer")
        elif df[col].dtype == "float64":
            df[col] = pd.to_numeric(df[col], downcast="float")
    logging.info(df.memory_usage(deep=True))
    return df


def _normalize_tz(df: pd.DataFrame) -> pd.DataFrame:
    tz_column = DELIMITER.join(
        [VENUE_COLUMN_PREFIX, VENUE_ADDRESS_COLUMN, ADDRESS_TIMEZONE_COLUMN]
    )
    if tz_column not in df.columns.values.tolist():
        return df
    df = df.dropna(subset=tz_column)

    tqdm.tqdm.pandas(desc="Timezone Conversions")

    # Check each row to see if they have the correct timezone
    dt_cols = set()

    def apply_tz(row: pd.Series) -> pd.Series:
        if tz_column not in row:
            return row
        tz = row[tz_column]
        if pd.isnull(tz):
            return row

        datetime_cols = {
            col for col, val in row.items() if isinstance(val, pd.Timestamp)
        }
        datetime_cols.add(GAME_DT_COLUMN)
        for col in datetime_cols:
            dt_cols.add(col)
            dt = row[col]  # type: ignore
            if isinstance(dt, (datetime.date, datetime.datetime)):
                dt = pd.to_datetime(dt)
            if dt.tz is None:
                row[col] = dt.tz_localize(
                    tz, ambiguous=True, nonexistent="shift_forward"
                )
            elif str(dt.tz) != str(tz):
                row[col] = dt.tz_convert(tz)

        return row

    for dt_col in dt_cols:
        df[dt_col] = pd.to_datetime(df[dt_col])

    return df.progress_apply(apply_tz, axis=1)  # type: ignore


def _find_nested_paths(
    field_type: str, model_class: type[BaseModel], cols: list[str]
) -> list[str]:
    def any_column_contains(substr: str) -> bool:
        for col in cols:
            if substr in col:
                return True
        return False

    nested_paths = []
    for field_name, field in model_class.model_fields.items():
        nested_field_type = (
            field.json_schema_extra.get("type")  # type: ignore
            if field.json_schema_extra
            else None
        )
        if nested_field_type == field_type:
            nested_paths.append(field_name)
        else:
            if issubclass(
                get_origin(field.annotation) or field.annotation,  # type: ignore
                BaseModel,  # type: ignore
            ):
                nested_paths.extend(
                    [
                        DELIMITER.join([field_name, x])
                        for x in _find_nested_paths(
                            field_type,
                            field.annotation,  # type: ignore
                            cols,
                        )  # type: ignore
                    ]
                )
            elif get_origin(field.annotation) == list and issubclass(
                get_args(field.annotation)[0], BaseModel
            ):
                i = 0
                while any_column_contains(DELIMITER.join([field_name, str(i)])):
                    nested_paths.extend(
                        [
                            DELIMITER.join([field_name, str(i), x])
                            for x in _find_nested_paths(
                                field_type, get_args(field.annotation)[0], cols
                            )
                        ]
                    )
                    i += 1
    return nested_paths


class LeagueModel(Model):
    """The prototype league model class."""

    _df: pd.DataFrame | None

    def __init__(
        self,
        league: League,
        session: ScrapeSession,
        position: int | None = None,
    ) -> None:
        super().__init__(session)
        self._league = league
        self._df = None
        self.position = position

    @classmethod
    def name(cls) -> str:
        """The name of the league model."""
        raise NotImplementedError("name is not implemented by parent class.")

    @property
    def games(self) -> Iterator[GameModel]:
        """Find all the games in this league."""
        raise NotImplementedError("games not implemented by LeagueModel parent class.")

    @property
    def league(self) -> League:
        """Return the league this league model represents."""
        return self._league

    def to_frame(self) -> pd.DataFrame:
        """Render the league as a dataframe."""
        df = self._df
        if df is None:
            data: dict[str, Any] = {}
            for game in tqdm.tqdm(self.games, desc="Games"):
                game_dict = flatten(game.model_dump(by_alias=True), DELIMITER)
                for k, v in game_dict.items():
                    current_v = data.get(k, [])
                    current_v.append(v)
                    data[k] = current_v

            categorical_cols = set(
                _find_nested_paths(FieldType.CATEGORICAL, GameModel, list(data.keys()))
            )

            for k in data:
                if k in categorical_cols:
                    data[k] = pd.Categorical(data[k])

            df = pd.DataFrame(data)

            df.attrs[str(FieldType.LOOKAHEAD)] = list(
                set(df.columns.values)
                & set(
                    _find_nested_paths(
                        FieldType.LOOKAHEAD, GameModel, df.columns.values.tolist()
                    )
                )
            )
            df.attrs[str(FieldType.ODDS)] = list(
                set(df.columns.values)
                & set(
                    _find_nested_paths(
                        FieldType.ODDS, GameModel, df.columns.values.tolist()
                    )
                )
            )
            df.attrs[str(FieldType.POINTS)] = list(
                set(df.columns.values)
                & set(
                    _find_nested_paths(
                        FieldType.POINTS, GameModel, df.columns.values.tolist()
                    )
                )
            )
            df.attrs[str(FieldType.TEXT)] = list(
                set(df.columns.values)
                & set(
                    _find_nested_paths(
                        FieldType.TEXT, GameModel, df.columns.values.tolist()
                    )
                )
            )
            df.attrs[str(FieldType.CATEGORICAL)] = list(
                set(df.columns.values) & categorical_cols
            )
            df.attrs[str(FieldType.LOOKAHEAD)] = list(
                set(df.attrs[str(FieldType.LOOKAHEAD)])
                | set(df.attrs[str(FieldType.POINTS)])
            )

            for categorical_column in df.attrs[str(FieldType.CATEGORICAL)]:
                df[categorical_column] = df[categorical_column].astype("category")

            df = _normalize_tz(df)

            if GAME_DT_COLUMN in df.columns.values:
                df = df.sort_values(
                    by=GAME_DT_COLUMN,
                    ascending=True,
                )
            df = _clear_column_list(df)
            df = df.reset_index()

            logging.info("Memory Usage for %s", self.name())
            df = _reduce_memory_usage(
                df[sorted(df.columns.values.tolist())].dropna(axis=1, how="all")
            )

            self._df = df
        return df
