"""AFL AFL team model."""

# pylint: disable=duplicate-code,too-many-arguments
import datetime

import requests_cache

from ...google.google_news_model import create_google_news_models
from ...league import League
from ...team_model import TeamModel
from ..position import Position
from .afl_afl_odds_model import create_afl_afl_odds_model
from .afl_afl_player_model import create_afl_afl_player_model


def create_afl_afl_team_model(
    team_name: str,
    players: list[tuple[str, str, str, str, Position]],
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    ladder: list[str],
    odds: float | None,
    version: str,
) -> TeamModel:
    """Create a team model from AFL AFL."""
    player_models = [
        create_afl_afl_player_model(
            identifier, player_number, " ".join([first_name, second_name]), position
        )
        for identifier, player_number, first_name, second_name, position in players
    ]
    odds_models = []
    if odds is not None:
        odds_models.append(create_afl_afl_odds_model(odds))
    if team_name not in ladder:
        raise ValueError(f"{team_name} not found in ladder")
    return TeamModel(
        identifier=team_name,
        name=team_name,
        location=None,
        players=player_models,
        odds=odds_models,
        points=None,
        ladder_rank=ladder.index(team_name) + 1,
        kicks=None,
        news=create_google_news_models(team_name, session, dt, League.AFL),
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
