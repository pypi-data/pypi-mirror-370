"""ESPNCricInfo team model."""

# pylint: disable=too-many-arguments,too-many-locals
import datetime
from typing import Any

import pytest_is_running
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ....cache import MEMORY
from ...google.google_news_model import create_google_news_models
from ...league import League
from ...team_model import VERSION, TeamModel
from ...x.x_social_model import create_x_social_model
from .ipl_espncricinfo_player_model import create_espncricinfo_player_model


def _create_espncricinfo_team_model(
    session: ScrapeSession,
    dt: datetime.datetime,
    league: League,
    team: dict[str, Any],
    innings: list[dict[str, Any]],
    teams_players: list[dict[str, Any]],
    positions_validator: dict[str, str],
    url: str,
    version: str,
) -> TeamModel:
    name = team["longName"]
    points = sum(int(x.strip()) for x in team["score"].split("&"))
    identifier = team["id"]
    players = []
    for team_players in teams_players:
        if identifier != team_players["team"]["id"]:
            continue
        for player in team_players["players"]:
            players.append(
                create_espncricinfo_player_model(
                    player=player["player"],
                    player_role_type=player["playerRoleType"],
                    innings=innings,
                    positions_validator=positions_validator,
                    dt=dt,
                    url=url,
                )
            )
        break
    runs = 0
    wickets = 0
    overs = 0
    balls = 0
    byes = 0
    legbyes = 0
    wides = 0
    no_balls = 0
    penalties = 0
    balls_per_over = 0
    fours = 0
    sixes = 0
    catches = 0
    catches_dropped = 0
    for inning in innings:
        # The team ID in the inning is the batting team
        if identifier != inning["team"]["id"]:
            wickets += inning["wickets"]
            overs += inning["overs"]
            balls += inning["balls"]
            wides += inning["wides"]
            no_balls += inning["noballs"]
            balls_per_over += inning["ballsPerOver"]
            catches += inning["catches"] if inning["catches"] is not None else 0
            catches_dropped += (
                inning["catchesDropped"] if inning["catchesDropped"] is not None else 0
            )
        else:
            runs += inning["runs"]
            byes += inning["byes"]
            legbyes += inning["legbyes"]
            penalties += inning["penalties"]
            fours += inning["fours"] if inning["fours"] is not None else 0
            sixes += inning["sixes"] if inning["sixes"] is not None else 0
    return TeamModel(
        identifier=str(identifier),
        name=name,
        players=players,
        odds=[],
        points=points,
        ladder_rank=None,
        location=None,
        news=create_google_news_models(name, session, dt, league),
        social=create_x_social_model(name, session, dt),
        coaches=[],
        lbw=None,
        end_dt=None,
        runs=runs,
        wickets=wickets,
        overs=overs,
        balls=balls,
        byes=byes,
        leg_byes=legbyes,
        wides=wides,
        no_balls=no_balls,
        penalties=penalties,
        balls_per_over=balls_per_over,
        fours=fours,
        sixes=sixes,
        catches=catches,
        catches_dropped=catches_dropped,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_espncricinfo_team_model(
    session: ScrapeSession,
    dt: datetime.datetime,
    league: League,
    team: dict[str, Any],
    positions_validator: dict[str, str],
    teams_players: list[dict[str, Any]],
    innings: list[dict[str, Any]],
    url: str,
    version: str,
) -> TeamModel:
    return _create_espncricinfo_team_model(
        session=session,
        dt=dt,
        league=league,
        team=team,
        positions_validator=positions_validator,
        teams_players=teams_players,
        innings=innings,
        url=url,
        version=version,
    )


def create_espncricinfo_team_model(
    session: ScrapeSession,
    dt: datetime.datetime,
    league: League,
    team: dict[str, Any],
    positions_validator: dict[str, str],
    teams_players: list[dict[str, Any]],
    innings: list[dict[str, Any]],
    url: str,
) -> TeamModel:
    """Create a team model from Sports Reference."""
    if not pytest_is_running.is_running():
        return _cached_create_espncricinfo_team_model(
            session=session,
            dt=dt,
            league=league,
            team=team,
            positions_validator=positions_validator,
            teams_players=teams_players,
            innings=innings,
            url=url,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_espncricinfo_team_model(
            session=session,
            dt=dt,
            league=league,
            team=team,
            positions_validator=positions_validator,
            teams_players=teams_players,
            innings=innings,
            url=url,
            version=VERSION,
        )
