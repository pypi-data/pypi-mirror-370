"""NFL SportsDB team model."""

# pylint: disable=too-many-arguments,duplicate-code
import datetime

import pytest_is_running
import requests_cache

from ...cache import MEMORY
from ..google.google_news_model import create_google_news_models
from ..league import League
from ..team_model import VERSION, TeamModel
from ..x.x_social_model import create_x_social_model


def _create_sportsdb_team_model(
    team_id: str,
    name: str,
    points: float,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    league: League,
    version: str,
) -> TeamModel:
    return TeamModel(
        identifier=team_id,
        name=name,
        points=points,
        players=[],
        odds=[],
        ladder_rank=None,
        location=None,
        news=create_google_news_models(name, session, dt, league),
        social=create_x_social_model(team_id, session, dt),
        field_goals=None,
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
def _cached_create_sportsdb_team_model(
    team_id: str,
    name: str,
    points: float,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    league: League,
    version: str,
) -> TeamModel:
    return _create_sportsdb_team_model(
        team_id=team_id,
        name=name,
        points=points,
        session=session,
        dt=dt,
        league=league,
        version=version,
    )


def create_sportsdb_team_model(
    team_id: str,
    name: str,
    points: float,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    league: League,
) -> TeamModel:
    """Create a team model based off the sportsdb NFL response."""
    if not pytest_is_running.is_running() and dt < datetime.datetime.now().replace(
        tzinfo=dt.tzinfo
    ) - datetime.timedelta(days=7):
        return _cached_create_sportsdb_team_model(
            team_id=team_id,
            name=name,
            points=points,
            session=session,
            dt=dt,
            league=league,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_sportsdb_team_model(
            team_id=team_id,
            name=name,
            points=points,
            session=session,
            dt=dt,
            league=league,
            version=VERSION,
        )
