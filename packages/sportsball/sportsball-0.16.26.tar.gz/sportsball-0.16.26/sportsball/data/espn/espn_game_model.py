"""ESPN game model."""

# pylint: disable=too-many-arguments,duplicate-code
import datetime
from typing import Any, Dict

import pytest_is_running
import requests_cache
from dateutil.parser import parse

from ...cache import MEMORY
from ..game_model import VERSION as GAME_VERSION
from ..game_model import GameModel, localize
from ..google.google_news_model import create_google_news_models
from ..league import League
from ..odds_model import OddsModel
from ..season_type import SeasonType
from ..team_model import VERSION as TEAM_VERSION
from ..team_model import TeamModel
from ..umpire_model import UmpireModel
from ..venue_model import VERSION as VENUE_VERSION
from ..venue_model import VenueModel
from ..x.x_social_model import create_x_social_model
from .espn_bookie_model import create_espn_bookie_model
from .espn_odds_model import MONEYLINE_KEY, create_espn_odds_model
from .espn_player_model import create_espn_player_model
from .espn_team_model import ID_KEY, create_espn_team_model
from .espn_umpire_model import create_espn_umpire_model
from .espn_venue_model import create_espn_venue_model


def _create_espn_team(
    competitor: Dict[str, Any],
    odds_dict: Dict[str, Any],
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    league: League,
    positions_validator: dict[str, str],
) -> TeamModel:
    if competitor["type"] == "athlete":
        player = create_espn_player_model(
            session=session,
            player=competitor,
            dt=dt,
            positions_validator=positions_validator,
        )
        return TeamModel(
            identifier=player.identifier,
            name=player.name,
            location=None,
            players=[player],
            odds=[],
            points=int(competitor["winner"]),
            ladder_rank=None,
            news=create_google_news_models(player.name, session, dt, league),
            social=create_x_social_model(player.identifier, session, dt),
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
            version=TEAM_VERSION,
        )

    team_response = session.get(competitor["team"]["$ref"])
    team_response.raise_for_status()
    team_dict = team_response.json()

    odds_key = competitor["homeAway"] + "TeamOdds"
    odds: list[OddsModel] = []
    if odds_dict:
        odds = [  # pyright: ignore
            create_espn_odds_model(
                x[odds_key],
                create_espn_bookie_model(x["provider"]),
            )
            for x in odds_dict["items"]
            if odds_key in x and MONEYLINE_KEY in x[odds_key]
        ]

    roster_dict = {}
    if "roster" in competitor:
        roster_response = session.get(competitor["roster"]["$ref"])
        roster_response.raise_for_status()
        roster_dict = roster_response.json()

    score_response = session.get(competitor["score"]["$ref"])
    score_response.raise_for_status()
    score_dict = score_response.json()

    return create_espn_team_model(
        session,
        team_dict,
        roster_dict,
        odds,
        score_dict,
        dt,
        league,
        positions_validator,
    )


def _create_venue(
    event: dict[str, Any],
    session: requests_cache.CachedSession,
    dt: datetime.datetime,
    version: str,
) -> VenueModel | None:
    venue = None
    if "venue" in event:
        venue = create_espn_venue_model(
            venue=event["venue"], session=session, dt=dt, version=version
        )
    if venue is None and "venues" in event:
        venues = event["venues"]
        if venues:
            venue_url = event["venues"][0]["$ref"]
            venue_response = session.get(venue_url)
            venue_response.raise_for_status()
            venue = create_espn_venue_model(
                venue=venue_response.json(), session=session, dt=dt, version=version
            )
    return venue  # pyright: ignore


def _create_teams(
    event: dict[str, Any],
    session: requests_cache.CachedSession,
    venue: VenueModel | None,
    dt: datetime.datetime,
    league: League,
    positions_validator: dict[str, str],
) -> tuple[list[TeamModel], int | None, datetime.datetime | None, list[UmpireModel]]:
    # pylint: disable=too-many-locals
    teams = []
    attendance = None
    end_dt = None
    umpires = []
    for competition in event["competitions"]:
        odds_dict = {}
        if "odds" in competition:
            odds_response = session.get(competition["odds"]["$ref"])
            odds_response.raise_for_status()
            odds_dict = odds_response.json()

        for competitor in competition["competitors"]:
            if competitor[ID_KEY] in {"-1", "-2"}:
                continue
            teams.append(
                _create_espn_team(
                    competitor, odds_dict, session, dt, league, positions_validator
                )
            )
        attendance = competition["attendance"]
        if "situation" in competition:
            situation_url = competition["situation"]["$ref"]
            situation_response = session.get(situation_url)
            situation_response.raise_for_status()
            situation = situation_response.json()
            if "lastPlay" in situation:
                last_play_response = session.get(situation["lastPlay"]["$ref"])
                last_play_response.raise_for_status()
                last_play = last_play_response.json()
                if "wallclock" in last_play:
                    end_dt = parse(last_play["wallclock"])
        if venue is not None and end_dt is not None:
            end_dt = localize(venue, end_dt)

        if "officials" in competition:
            officials_response = session.get(competition["officials"]["$ref"])
            officials_response.raise_for_status()
            officials_dict = officials_response.json()
            for official in officials_dict["items"]:
                umpires.append(
                    create_espn_umpire_model(
                        session=session, url=official["$ref"], dt=dt
                    )
                )

    return teams, attendance, end_dt, umpires


def _create_espn_game_model(
    event: dict[str, Any],
    week: int | None,
    game_number: int,
    session: requests_cache.CachedSession,
    league: League,
    year: int | None,
    season_type: SeasonType | None,
    positions_validator: dict[str, str],
    version: str,
) -> GameModel:
    dt = parse(event["date"])
    venue = _create_venue(event, session, dt, VENUE_VERSION)
    if venue is not None:
        dt = localize(venue, dt)
    teams, attendance, end_dt, umpires = _create_teams(
        event, session, venue, dt, league, positions_validator
    )
    return GameModel(
        dt=dt,
        week=week,
        game_number=game_number,
        venue=venue,
        teams=teams,
        end_dt=end_dt,
        attendance=attendance,
        league=str(league),
        year=year,
        season_type=season_type,
        postponed=None,
        play_off=None,
        distance=None,
        dividends=[],
        pot=None,
        umpires=umpires,
        version=version,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_espn_game_model(
    event: dict[str, Any],
    week: int | None,
    game_number: int,
    session: requests_cache.CachedSession,
    league: League,
    year: int | None,
    season_type: SeasonType | None,
    positions_validator: dict[str, str],
    version: str,
) -> GameModel:
    return _create_espn_game_model(
        event=event,
        week=week,
        game_number=game_number,
        session=session,
        league=league,
        year=year,
        season_type=season_type,
        positions_validator=positions_validator,
        version=version,
    )


def create_espn_game_model(
    event: dict[str, Any],
    week: int | None,
    game_number: int,
    session: requests_cache.CachedSession,
    league: League,
    year: int | None,
    season_type: SeasonType | None,
    positions_validator: dict[str, str],
) -> GameModel:
    """Creates an ESPN game model."""
    dt = parse(event["date"])
    if (
        not pytest_is_running.is_running()
        and dt.date() < datetime.datetime.now().date() - datetime.timedelta(days=7)
    ):
        return _cached_create_espn_game_model(
            event=event,
            week=week,
            game_number=game_number,
            session=session,
            league=league,
            year=year,
            season_type=season_type,
            positions_validator=positions_validator,
            version=GAME_VERSION,
        )
    with session.cache_disabled():
        return _create_espn_game_model(
            event=event,
            week=week,
            game_number=game_number,
            session=session,
            league=league,
            year=year,
            season_type=season_type,
            positions_validator=positions_validator,
            version=GAME_VERSION,
        )
