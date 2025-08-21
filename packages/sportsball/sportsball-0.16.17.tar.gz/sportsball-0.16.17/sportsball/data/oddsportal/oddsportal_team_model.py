"""Odds Portal team model."""

# pylint: disable=too-many-arguments,duplicate-code,line-too-long,too-many-locals
import datetime
import logging
from typing import Any

import pytest_is_running
import requests_cache

from ...cache import MEMORY
from ..google.google_news_model import create_google_news_models
from ..league import League
from ..team_model import VERSION, TeamModel
from ..x.x_social_model import create_x_social_model
from .oddsportal_odds_model import create_oddsportal_odds_model


def _create_oddsportal_team_model(
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    team_name: str,
    league: League,
    points: float | None,
    default_bet_id: str,
    default_scope_id: str,
    bookie_names: dict[str, str],
    team_idx: int,
    parsed_data: dict[str, Any],
    version: str,
) -> TeamModel:
    back = parsed_data["d"]["oddsdata"]["back"]
    odds_models = []

    if not isinstance(back, list):
        try:
            odds_data = back[f"E-{default_bet_id}-{default_scope_id}-0-0-0"]
        except KeyError:
            back = parsed_data["d"]["oddsdata"]["back"]
            odds_data = back[sorted(list(back.keys()))[0]]
        except TypeError as exc:
            logging.error("Failed to parse the following odds")
            raise exc
        try:
            outcome_id = odds_data["outcomeId"][team_idx]
        except KeyError:
            outcome_id = odds_data["outcomeId"][str(team_idx)]
        history = odds_data["history"][outcome_id]

        for bookie_id, bookie_name in bookie_names.items():
            if bookie_name is None:
                continue
            for odds, _, timestamp in history.get(bookie_id, []):
                odds_models.append(
                    create_oddsportal_odds_model(
                        odds,
                        datetime.datetime.fromtimestamp(timestamp),
                        bookie_name,
                        bookie_id,  # type: ignore
                    )
                )

    return TeamModel(
        identifier=team_name,
        name=team_name,
        points=points,
        players=[],
        odds=odds_models,
        ladder_rank=None,
        location=None,
        news=create_google_news_models(team_name, session, dt, league),
        social=create_x_social_model(team_name, session, dt),
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
def _cached_create_oddsportal_team_model(
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    team_name: str,
    league: League,
    points: float | None,
    default_bet_id: str,
    default_scope_id: str,
    bookie_names: dict[str, str],
    team_idx: int,
    parsed_data: dict[str, Any],
    version: str,
) -> TeamModel:
    return _create_oddsportal_team_model(
        session=session,
        dt=dt,
        team_name=team_name,
        league=league,
        points=points,
        default_bet_id=default_bet_id,
        default_scope_id=default_scope_id,
        bookie_names=bookie_names,
        team_idx=team_idx,
        parsed_data=parsed_data,
        version=version,
    )


def create_oddsportal_team_model(
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    team_name: str,
    league: League,
    points: float | None,
    default_bet_id: str,
    default_scope_id: str,
    bookie_names: dict[str, str],
    team_idx: int,
    parsed_data: dict[str, Any],
) -> TeamModel:
    """Create a team model based off the odds portal response."""
    if not pytest_is_running.is_running() and dt < datetime.datetime.now().replace(
        tzinfo=dt.tzinfo
    ) - datetime.timedelta(days=7):
        return _cached_create_oddsportal_team_model(
            session=session,
            dt=dt,
            team_name=team_name,
            league=league,
            points=points,
            default_bet_id=default_bet_id,
            default_scope_id=default_scope_id,
            bookie_names=bookie_names,
            team_idx=team_idx,
            parsed_data=parsed_data,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_oddsportal_team_model(
            session=session,
            dt=dt,
            team_name=team_name,
            league=league,
            points=points,
            default_bet_id=default_bet_id,
            default_scope_id=default_scope_id,
            bookie_names=bookie_names,
            team_idx=team_idx,
            parsed_data=parsed_data,
            version=VERSION,
        )
