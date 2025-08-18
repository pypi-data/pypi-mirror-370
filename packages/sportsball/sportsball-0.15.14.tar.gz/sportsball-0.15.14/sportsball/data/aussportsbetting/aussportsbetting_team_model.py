"""Aussportsbetting team model."""

# pylint: disable=too-many-arguments
import datetime

import requests_cache

from ...cache import MEMORY
from ..google.google_news_model import create_google_news_models
from ..league import League
from ..team_model import TeamModel
from ..x.x_social_model import create_x_social_model
from .aussportsbetting_odds_model import create_aussportsbetting_odds_model


@MEMORY.cache(ignore=["session"])
def create_aussportsbetting_team_model(
    name: str,
    points: float,
    odds: float,
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    league: League,
    version: str,
) -> TeamModel:
    """Create a team model based off aus sports betting."""
    odds_model = create_aussportsbetting_odds_model(odds)
    return TeamModel(
        identifier=name,
        name=name,
        location=None,
        players=[],
        odds=[odds_model],  # pyright: ignore
        points=points,
        ladder_rank=None,
        news=create_google_news_models(name, session, dt, league),
        social=create_x_social_model(name, session, dt),
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
