"""NBA API team model."""

# pylint: disable=too-many-arguments,unused-argument,duplicate-code
import datetime

import numpy as np
import pandas as pd
import pytest_is_running
import requests_cache

from ....cache import MEMORY
from ...google.google_news_model import create_google_news_models
from ...league import League
from ...team_model import VERSION, TeamModel
from ...x.x_social_model import create_x_social_model


def _create_nba_nba_team_model(
    row: pd.Series,
    home: bool,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    league: League,
    league_id: str,
    version: str,
) -> TeamModel | None:
    """Create a team model from NBA API."""
    suffix = "_A" if home else "_B"
    identifier = row["TEAM_ID" + suffix]
    if identifier is None:
        return None
    name = row["TEAM_NAME" + suffix]
    if name is None:
        return None

    offensive_rebounds = row["OREB" + suffix]
    if not np.isfinite(offensive_rebounds):
        offensive_rebounds = None

    return TeamModel(
        identifier=str(identifier),
        name=name,
        players=[],
        odds=[],
        points=float(row["PTS" + suffix]),
        ladder_rank=None,
        location=None,
        news=create_google_news_models(name, session, dt, league),
        social=create_x_social_model(str(identifier), session, dt),
        field_goals=row["FGM" + suffix],
        field_goals_attempted=row["FGA" + suffix],
        offensive_rebounds=offensive_rebounds,
        assists=row["AST" + suffix],
        turnovers=row["TOV" + suffix],
        coaches=[],
        lbw=None,
        end_dt=None,
        runs=None,
        wickets=None,
        overs=None,
        balls=None,
        byes=None,
        leg_byes=None,
        wides=None,
        no_balls=None,
        penalties=None,
        balls_per_over=None,
        fours=None,
        sixes=None,
        catches=None,
        catches_dropped=None,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_nba_nba_team_model(
    row: pd.Series,
    home: bool,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    league: League,
    league_id: str,
    version: str,
) -> TeamModel | None:
    return _create_nba_nba_team_model(
        row=row,
        home=home,
        session=session,
        dt=dt,
        league=league,
        league_id=league_id,
        version=version,
    )


def create_nba_nba_team_model(
    row: pd.Series,
    home: bool,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    league: League,
    league_id: str,
) -> TeamModel | None:
    """Create a team model from NBA API."""
    if not pytest_is_running.is_running() and dt < datetime.datetime.now().replace(
        tzinfo=dt.tzinfo
    ) - datetime.timedelta(days=7):
        return _cached_create_nba_nba_team_model(
            row=row,
            home=home,
            session=session,
            dt=dt,
            league=league,
            league_id=league_id,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_nba_nba_team_model(
            row=row,
            home=home,
            session=session,
            dt=dt,
            league=league,
            league_id=league_id,
            version=VERSION,
        )
