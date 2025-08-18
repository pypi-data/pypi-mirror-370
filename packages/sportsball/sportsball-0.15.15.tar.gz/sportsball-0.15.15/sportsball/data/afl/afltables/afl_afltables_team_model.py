"""AFL AFLTables team model."""

# pylint: disable=too-many-arguments,too-many-locals,duplicate-code,line-too-long
import datetime
import os
import urllib.parse
from urllib.parse import urlparse

import pytest_is_running
import requests_cache
from bs4 import BeautifulSoup

from ....cache import MEMORY
from ...google.google_news_model import create_google_news_models
from ...league import League
from ...team_model import VERSION, TeamModel
from ...x.x_social_model import create_x_social_model
from .afl_afltables_coach_model import create_afl_afltables_coach_model
from .afl_afltables_player_model import create_afl_afltables_player_model

_TEAM_NAME_MAP = {
    "Melbourne": ["ME"],
    "Geelong": ["GE"],
    "Fitzroy": ["FI"],
    "Collingwood": ["CW"],
    "Essendon": ["ES"],
    "South Melbourne": ["SM"],
    "St Kilda": ["SK"],
    "Carlton": ["CA"],
    "Sydney": ["SM", "SY"],
    "University": ["UN"],
    "Richmond": ["RI"],
    "North Melbourne": ["NM"],
    "Western Bulldogs": ["WB", "FO"],
    "Hawthorn": ["HW"],
    "Brisbane Bears": ["BB"],
    "West Coast": ["WC"],
    "Adelaide": ["AD"],
    "Fremantle": ["FR"],
    "Brisbane Lions": ["BL"],
    "Port Adelaide": ["PA"],
    "Gold Coast": ["GC"],
    "Greater Western Sydney": ["GW"],
}


def _create_afl_afltables_team_model(
    team_url: str,
    players: list[
        tuple[
            str,
            str,
            int | None,
            str,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            float | None,
        ]
    ],
    points: float,
    session: requests_cache.CachedSession,
    last_ladder_ranks: dict[str, int] | None,
    dt: datetime.datetime,
    league: League,
    version: str,
) -> TeamModel:
    response = session.get(team_url)
    soup = BeautifulSoup(response.text, "lxml")
    o = urlparse(team_url)
    last_component = o.path.split("/")[-1]
    identifier, _ = os.path.splitext(last_component)
    h1 = soup.find("h1")
    if h1 is None:
        raise ValueError("h1 is null.")
    name = h1.get_text()
    last_ladder_rank = None
    if last_ladder_ranks is not None and last_ladder_ranks:
        short_names = _TEAM_NAME_MAP[name]
        for short_name in short_names:
            if short_name in last_ladder_ranks:
                last_ladder_rank = last_ladder_ranks[short_name]
                break
    coaches_url = None
    for a in soup.find_all("a", href=True):
        a_text = a.get_text()
        if a_text == "Coaches":
            coaches_url = urllib.parse.urljoin(team_url, a.get("href"))
            break
    if coaches_url is None:
        raise ValueError("coaches_url is null")

    coach_model = create_afl_afltables_coach_model(
        url=coaches_url, session=session, year=dt.year, dt=dt
    )

    return TeamModel(
        identifier=identifier,
        name=name,
        players=[  # pyright: ignore
            create_afl_afltables_player_model(
                player_url=player_url,
                jersey=jersey,
                kicks=kicks,
                session=session,
                name=name,
                marks=marks,
                handballs=handballs,
                disposals=disposals,
                goals=goals,
                behinds=behinds,
                hit_outs=hit_outs,
                tackles=tackles,
                rebounds=rebounds,
                insides=insides,
                clearances=clearances,
                clangers=clangers,
                free_kicks_for=free_kicks_for,
                free_kicks_against=free_kicks_against,
                brownlow_votes=brownlow_votes,
                contested_possessions=contested_possessions,
                uncontested_possessions=uncontested_possessions,
                contested_marks=contested_marks,
                marks_inside=marks_inside,
                one_percenters=one_percenters,
                bounces=bounces,
                goal_assists=goal_assists,
                percentage_played=percentage_played,
                dt=dt,
            )
            for player_url, jersey, kicks, name, marks, handballs, disposals, goals, behinds, hit_outs, tackles, rebounds, insides, clearances, clangers, free_kicks_for, free_kicks_against, brownlow_votes, contested_possessions, uncontested_possessions, contested_marks, marks_inside, one_percenters, bounces, goal_assists, percentage_played in players
        ],
        odds=[],
        points=points,
        ladder_rank=last_ladder_rank,
        location=None,
        news=create_google_news_models(name, session, dt, league),
        social=create_x_social_model(identifier, session, dt),
        field_goals=None,
        coaches=[coach_model] if coach_model is not None else [],
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
def _cached_create_afl_afltables_team_model(
    team_url: str,
    players: list[
        tuple[
            str,
            str,
            int | None,
            str,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            float | None,
        ]
    ],
    points: float,
    session: requests_cache.CachedSession,
    last_ladder_ranks: dict[str, int] | None,
    dt: datetime.datetime,
    league: League,
    version: str,
) -> TeamModel:
    return _create_afl_afltables_team_model(
        team_url=team_url,
        players=players,
        points=points,
        session=session,
        last_ladder_ranks=last_ladder_ranks,
        dt=dt,
        league=league,
        version=version,
    )


def create_afl_afltables_team_model(
    team_url: str,
    players: list[
        tuple[
            str,
            str,
            int | None,
            str,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            int | None,
            float | None,
        ]
    ],
    points: float,
    session: requests_cache.CachedSession,
    last_ladder_ranks: dict[str, int] | None,
    dt: datetime.datetime,
    league: League,
) -> TeamModel:
    """Create a team model from AFL Tables."""
    if not pytest_is_running.is_running():
        return _cached_create_afl_afltables_team_model(
            team_url=team_url,
            players=players,
            points=points,
            session=session,
            last_ladder_ranks=last_ladder_ranks,
            dt=dt,
            league=league,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_afl_afltables_team_model(
            team_url=team_url,
            players=players,
            points=points,
            session=session,
            last_ladder_ranks=last_ladder_ranks,
            dt=dt,
            league=league,
            version=VERSION,
        )
