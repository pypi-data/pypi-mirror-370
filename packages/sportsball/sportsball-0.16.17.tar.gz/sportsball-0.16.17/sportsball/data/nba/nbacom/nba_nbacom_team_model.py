"""NBA NBA.com team model."""

# pylint: disable=duplicate-code,too-many-arguments
import datetime
from typing import Any

import requests_cache

from ...google.google_news_model import create_google_news_models
from ...league import League
from ...team_model import TeamModel
from .nba_nbacom_player_model import create_nba_nbacom_player_model


def create_nba_nbacom_team_model(
    team: dict[str, Any],
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    version: str,
) -> TeamModel:
    """Create a team model from AFL AFL."""
    team_name = team["teamAbbreviation"]
    return TeamModel(
        identifier=str(team["teamId"]),
        name=team_name,
        location=None,
        players=[create_nba_nbacom_player_model(x) for x in team["players"]],
        odds=[],
        points=None,
        ladder_rank=None,
        kicks=None,
        news=create_google_news_models(team_name, session, dt, League.NBA),
        social=[],
        field_goals=None,
        field_goals_attempted=None,
        offensive_rebounds=None,
        assists=None,
        turnovers=None,
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
