"""HKJC HKJC team model."""

# pylint: disable=duplicate-code,too-many-arguments,too-many-locals
import datetime

import pytest_is_running
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ....cache import MEMORY
from ...odds_model import OddsModel
from ...team_model import VERSION, TeamModel
from ..position import Position
from .hkjc_hkjc_coach_model import create_hkjc_hkjc_coach_model
from .hkjc_hkjc_player_model import create_hkjc_hkjc_player_model


def _create_hkjc_hkjc_team_model(
    session: ScrapeSession,
    horse_url: str,
    jockey_url: str | None,
    trainer_url: str | None,
    points: float,
    jersey: str,
    handicap_weight: float | None,
    horse_weight: float | None,
    starting_position: Position | None,
    lbw: float | None,
    end_dt: datetime.datetime | None,
    odds: list[OddsModel],
    version: str,
) -> TeamModel:
    players = []
    horse_player = create_hkjc_hkjc_player_model(
        session=session,
        url=horse_url,
        jersey=jersey,
        handicap_weight=handicap_weight,
        starting_position=starting_position,
        weight=horse_weight,
    )
    if horse_player is not None:
        players.append(horse_player)
    if jockey_url is not None:
        jockey_player = create_hkjc_hkjc_player_model(
            session=session,
            url=jockey_url,
            jersey=jersey,
            handicap_weight=None,
            starting_position=starting_position,
            weight=None,
        )
        if jockey_player is not None:
            players.append(jockey_player)
    coaches = (
        [create_hkjc_hkjc_coach_model(session=session, url=trainer_url)]
        if trainer_url is not None
        else []
    )
    name = " - ".join([x.name for x in players])
    return TeamModel(
        identifier=name,
        name=name,
        location=None,
        players=players,
        odds=odds,
        points=points,
        ladder_rank=None,
        news=[],
        social=[],
        field_goals=None,
        coaches=coaches,
        lbw=lbw,
        end_dt=end_dt,
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
def _cached_create_hkjc_hkjc_team_model(
    session: ScrapeSession,
    horse_url: str,
    jockey_url: str | None,
    trainer_url: str | None,
    points: float,
    jersey: str,
    handicap_weight: float | None,
    horse_weight: float | None,
    starting_position: Position | None,
    lbw: float | None,
    end_dt: datetime.datetime | None,
    odds: list[OddsModel],
    version: str,
) -> TeamModel:
    return _create_hkjc_hkjc_team_model(
        session=session,
        horse_url=horse_url,
        jockey_url=jockey_url,
        trainer_url=trainer_url,
        points=points,
        jersey=jersey,
        handicap_weight=handicap_weight,
        horse_weight=horse_weight,
        starting_position=starting_position,
        lbw=lbw,
        end_dt=end_dt,
        odds=odds,
        version=version,
    )


def create_hkjc_hkjc_team_model(
    session: ScrapeSession,
    horse_url: str,
    jockey_url: str | None,
    trainer_url: str | None,
    points: float,
    jersey: str,
    handicap_weight: float | None,
    horse_weight: float | None,
    starting_position: Position | None,
    lbw: float | None,
    end_dt: datetime.datetime | None,
    odds: list[OddsModel],
) -> TeamModel:
    """Create team model from HKJC."""
    if not pytest_is_running.is_running():
        return _cached_create_hkjc_hkjc_team_model(
            session=session,
            horse_url=horse_url,
            jockey_url=jockey_url,
            trainer_url=trainer_url,
            points=points,
            jersey=jersey,
            handicap_weight=handicap_weight,
            horse_weight=horse_weight,
            starting_position=starting_position,
            lbw=lbw,
            end_dt=end_dt,
            odds=odds,
            version=VERSION,
        )
    return _create_hkjc_hkjc_team_model(
        session=session,
        horse_url=horse_url,
        jockey_url=jockey_url,
        trainer_url=trainer_url,
        points=points,
        jersey=jersey,
        handicap_weight=handicap_weight,
        horse_weight=horse_weight,
        starting_position=starting_position,
        lbw=lbw,
        end_dt=end_dt,
        odds=odds,
        version=VERSION,
    )
