"""The prototype class for a team."""

# pylint: disable=duplicate-code
import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from .coach_model import VERSION as COACH_VERSION
from .coach_model import CoachModel
from .delimiter import DELIMITER
from .field_type import FFILL_KEY, TYPE_KEY, FieldType
from .news_model import NewsModel
from .odds_model import OddsModel
from .player_model import VERSION as PLAYER_VERSION
from .player_model import PlayerModel
from .social_model import SocialModel

TEAM_POINTS_COLUMN: Literal["points"] = "points"
TEAM_IDENTIFIER_COLUMN: Literal["identifier"] = "identifier"
PLAYER_COLUMN_PREFIX: Literal["players"] = "players"
NAME_COLUMN: Literal["name"] = "name"
FIELD_GOALS_COLUMN: Literal["field_goals"] = "field_goals"
FIELD_GOALS_ATTEMPTED_COLUMN: Literal["field_goals_attempted"] = "field_goals_attempted"
OFFENSIVE_REBOUNDS_COLUMN: Literal["offensive_rebounds"] = "offensive_rebounds"
ASSISTS_COLUMN: Literal["assists"] = "assists"
TURNOVERS_COLUMN: Literal["turnovers"] = "turnovers"
KICKS_COLUMN: Literal["kicks"] = "kicks"
TEAM_ODDS_COLUMN: Literal["odds"] = "odds"
TEAM_MARKS_COLUMN: Literal["marks"] = "marks"
TEAM_HANDBALLS_COLUMN: Literal["handballs"] = "handballs"
TEAM_DISPOSALS_COLUMN: Literal["disposals"] = "disposals"
TEAM_GOALS_COLUMN: Literal["goals"] = "goals"
TEAM_BEHINDS_COLUMN: Literal["behinds"] = "behinds"
TEAM_HIT_OUTS_COLUMN: Literal["hit_outs"] = "hit_outs"
TEAM_TACKLES_COLUMN: Literal["tackles"] = "tackles"
TEAM_REBOUNDS_COLUMN: Literal["rebounds"] = "rebounds"
TEAM_INSIDES_COLUMN: Literal["insides"] = "insides"
TEAM_CLEARANCES_COLUMN: Literal["clearances"] = "clearances"
TEAM_CLANGERS_COLUMN: Literal["clangers"] = "clangers"
TEAM_FREE_KICKS_FOR_COLUMN: Literal["free_kicks_for"] = "free_kicks_for"
TEAM_FREE_KICKS_AGAINST_COLUMN: Literal["free_kicks_against"] = "free_kicks_against"
TEAM_BROWNLOW_VOTES_COLUMN: Literal["brownlow_votes"] = "brownlow_votes"
TEAM_CONTESTED_POSSESSIONS_COLUMN: Literal["contested_possessions"] = (
    "contested_possessions"
)
TEAM_UNCONTESTED_POSSESSIONS_COLUMN: Literal["uncontested_possessions"] = (
    "uncontested_possessions"
)
TEAM_CONTESTED_MARKS_COLUMN: Literal["contested_marks"] = "contested_marks"
TEAM_MARKS_INSIDE_COLUMN: Literal["marks_inside"] = "marks_inside"
TEAM_ONE_PERCENTERS_COLUMN: Literal["one_percenters"] = "one_percenters"
TEAM_BOUNCES_COLUMN: Literal["bounces"] = "bounces"
TEAM_GOAL_ASSISTS_COLUMN: Literal["goal_assists"] = "goal_assists"
TEAM_NEWS_COLUMN: Literal["news"] = "news"
TEAM_COACHES_COLUMN: Literal["coaches"] = "coaches"
TEAM_LENGTH_BEHIND_WINNER_COLUMN: Literal["lbw"] = "lbw"
TEAM_END_DT_COLUMN: Literal["end_dt"] = "end_dt"
TEAM_FIELD_GOALS_PERCENTAGE_COLUMN: Literal["field_goals_percentage"] = (
    "field_goals_percentage"
)
TEAM_THREE_POINT_FIELD_GOALS_COLUMN: Literal["three_point_field_goals"] = (
    "three_point_field_goals"
)
TEAM_THREE_POINT_FIELD_GOALS_ATTEMPTED_COLUMN: Literal[
    "three_point_field_goals_attempted"
] = "three_point_field_goals_attempted"
TEAM_THREE_POINT_FIELD_GOALS_PERCENTAGE_COLUMN: Literal[
    "three_point_field_goals_percentage"
] = "three_point_field_goals_percentage"
TEAM_FREE_THROWS_COLUMN: Literal["free_throws"] = "free_throws"
TEAM_FREE_THROWS_ATTEMPTED_COLUMN: Literal["free_throws_attempted"] = (
    "free_throws_attempted"
)
TEAM_FREE_THROWS_PERCENTAGE_COLUMN: Literal["free_throws_percentage"] = (
    "free_throws_percentage"
)
TEAM_DEFENSIVE_REBOUNDS_COLUMN: Literal["defensive_rebounds"] = "defensive_rebounds"
TEAM_TOTAL_REBOUNDS_COLUMN: Literal["total_rebounds"] = "total_rebounds"
TEAM_STEALS_COLUMN: Literal["steals"] = "steals"
TEAM_BLOCKS_COLUMN: Literal["blocks"] = "blocks"
TEAM_PERSONAL_FOULS_COLUMN: Literal["personal_fouls"] = "personal_fouls"
TEAM_FORCED_FUMBLES_COLUMN: Literal["forced_fumbles"] = "forced_fumbles"
TEAM_FUMBLES_RECOVERED_COLUMN: Literal["fumbles_recovered"] = "fumbles_recovered"
TEAM_FUMBLES_TOUCHDOWNS_COLUMN: Literal["fumbles_touchdowns"] = "fumbles_touchdowns"
TEAM_RUNS_COLUMN: Literal["runs"] = "runs"
TEAM_WICKETS_COLUMN: Literal["wickets"] = "wickets"
TEAM_OVERS_COLUMN: Literal["overs"] = "overs"
TEAM_BALLS_COLUMN: Literal["balls"] = "balls"
TEAM_BYES_COLUMN: Literal["byes"] = "byes"
TEAM_LEG_BYES_COLUMN: Literal["leg_byes"] = "leg_byes"
TEAM_WIDES_COLUMN: Literal["wides"] = "wides"
TEAM_NO_BALLS_COLUMN: Literal["no_balls"] = "no_balls"
TEAM_PENALTIES_COLUMN: Literal["penalties"] = "penalties"
TEAM_BALLS_PER_OVER_COLUMN: Literal["balls_per_over"] = "balls_per_over"
TEAM_FOURS_COLUMN: Literal["fours"] = "fours"
TEAM_SIXES_COLUMN: Literal["sixes"] = "sixes"
TEAM_CATCHES_COLUMN: Literal["catches"] = "catches"
TEAM_CATCHES_DROPPED_COLUMN: Literal["catches_dropped"] = "catches_dropped"
VERSION = DELIMITER.join(["0.0.3", PLAYER_VERSION, COACH_VERSION])


def _calculate_kicks(data: dict[str, Any]) -> int | None:
    kicks = 0
    found_kicks = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_kicks = player.kicks
        if player_kicks is None:
            continue
        found_kicks = True
        kicks += player_kicks
    if not found_kicks:
        return None
    return kicks


def _calculate_field_goals(data: dict[str, Any]) -> int | None:
    field_goals = 0
    found_field_goals = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_field_goals = player.field_goals
        if player_field_goals is None:
            continue
        found_field_goals = True
        field_goals += player_field_goals
    if not found_field_goals:
        return None
    return field_goals


def _calculate_field_goals_attempted(data: dict[str, Any]) -> int | None:
    field_goals_attempted = 0
    found_field_goals_attempted = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_field_goals_attempted = player.field_goals_attempted
        if player_field_goals_attempted is None:
            continue
        found_field_goals_attempted = True
        field_goals_attempted += player_field_goals_attempted
    if not found_field_goals_attempted:
        return None
    return field_goals_attempted


def _calculate_offensive_rebounds(data: dict[str, Any]) -> int | None:
    offensive_rebounds = 0
    found_offensive_rebounds = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_offensive_rebounds = player.offensive_rebounds
        if player_offensive_rebounds is None:
            continue
        found_offensive_rebounds = True
        offensive_rebounds += player_offensive_rebounds
    if not found_offensive_rebounds:
        return None
    return offensive_rebounds


def _calculate_assists(data: dict[str, Any]) -> int | None:
    assists = 0
    found_assists = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_assists = player.assists
        if player_assists is None:
            continue
        found_assists = True
        assists += player_assists
    if not found_assists:
        return None
    return assists


def _calculate_turnovers(data: dict[str, Any]) -> int | None:
    turnovers = 0
    found_turnovers = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_turnovers = player.turnovers
        if player_turnovers is None:
            continue
        found_turnovers = True
        turnovers += player_turnovers
    if not found_turnovers:
        return None
    return turnovers


def _calculate_marks(data: dict[str, Any]) -> int | None:
    marks = 0
    found_marks = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_marks = player.marks
        if player_marks is None:
            continue
        found_marks = True
        marks += player_marks
    if not found_marks:
        return None
    return marks


def _calculate_handballs(data: dict[str, Any]) -> int | None:
    handballs = 0
    found_handballs = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_handballs = player.handballs
        if player_handballs is None:
            continue
        found_handballs = True
        handballs += player_handballs
    if not found_handballs:
        return None
    return handballs


def _calculate_disposals(data: dict[str, Any]) -> int | None:
    disposals = 0
    found_disposals = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_disposals = player.disposals
        if player_disposals is None:
            continue
        found_disposals = True
        disposals += player_disposals
    if not found_disposals:
        return None
    return disposals


def _calculate_goals(data: dict[str, Any]) -> int | None:
    goals = 0
    found_goals = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_goals = player.goals
        if player_goals is None:
            continue
        found_goals = True
        goals += player_goals
    if not found_goals:
        return None
    return goals


def _calculate_behinds(data: dict[str, Any]) -> int | None:
    behinds = 0
    found_behinds = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_behinds = player.behinds
        if player_behinds is None:
            continue
        found_behinds = True
        behinds += player_behinds
    if not found_behinds:
        return None
    return behinds


def _calculate_hit_outs(data: dict[str, Any]) -> int | None:
    hit_outs = 0
    found_hit_outs = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_hit_outs = player.hit_outs
        if player_hit_outs is None:
            continue
        found_hit_outs = True
        hit_outs += player_hit_outs
    if not found_hit_outs:
        return None
    return hit_outs


def _calculate_tackles(data: dict[str, Any]) -> int | None:
    tackles = 0
    found_tackles = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_tackles = player.tackles
        if player_tackles is None:
            continue
        found_tackles = True
        tackles += player_tackles
    if not found_tackles:
        return None
    return tackles


def _calculate_rebounds(data: dict[str, Any]) -> int | None:
    rebounds = 0
    found_rebounds = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_rebounds = player.rebounds
        if player_rebounds is None:
            continue
        found_rebounds = True
        rebounds += player_rebounds
    if not found_rebounds:
        return None
    return rebounds


def _calculate_insides(data: dict[str, Any]) -> int | None:
    insides = 0
    found_insides = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_insides = player.insides
        if player_insides is None:
            continue
        found_insides = True
        insides += player_insides
    if not found_insides:
        return None
    return insides


def _calculate_clearances(data: dict[str, Any]) -> int | None:
    clearances = 0
    found_clearances = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_clearances = player.clearances
        if player_clearances is None:
            continue
        found_clearances = True
        clearances += player_clearances
    if not found_clearances:
        return None
    return clearances


def _calculate_clangers(data: dict[str, Any]) -> int | None:
    clangers = 0
    found_clangers = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_clangers = player.clangers
        if player_clangers is None:
            continue
        found_clangers = True
        clangers += player_clangers
    if not found_clangers:
        return None
    return clangers


def _calculate_free_kicks_for(data: dict[str, Any]) -> int | None:
    free_kicks_for = 0
    found_free_kicks_for = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_free_kicks_for = player.free_kicks_for
        if player_free_kicks_for is None:
            continue
        found_free_kicks_for = True
        free_kicks_for += player_free_kicks_for
    if not found_free_kicks_for:
        return None
    return free_kicks_for


def _calculate_free_kicks_against(data: dict[str, Any]) -> int | None:
    free_kicks_against = 0
    found_free_kicks_against = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_free_kicks_against = player.free_kicks_against
        if player_free_kicks_against is None:
            continue
        found_free_kicks_against = True
        free_kicks_against += player_free_kicks_against
    if not found_free_kicks_against:
        return None
    return free_kicks_against


def _calculate_brownlow_votes(data: dict[str, Any]) -> int | None:
    brownlow_votes = 0
    found_brownlow_votes = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_brownlow_votes = player.brownlow_votes
        if player_brownlow_votes is None:
            continue
        found_brownlow_votes = True
        brownlow_votes += player_brownlow_votes
    if not found_brownlow_votes:
        return None
    return brownlow_votes


def _calculate_contested_possessions(data: dict[str, Any]) -> int | None:
    contested_possessions = 0
    found_contested_possessions = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_contested_possessions = player.contested_possessions
        if player_contested_possessions is None:
            continue
        found_contested_possessions = True
        contested_possessions += player_contested_possessions
    if not found_contested_possessions:
        return None
    return contested_possessions


def _calculate_uncontested_possessions(data: dict[str, Any]) -> int | None:
    uncontested_possessions = 0
    found_uncontested_possessions = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_uncontested_possessions = player.uncontested_possessions
        if player_uncontested_possessions is None:
            continue
        found_uncontested_possessions = True
        uncontested_possessions += player_uncontested_possessions
    if not found_uncontested_possessions:
        return None
    return uncontested_possessions


def _calculate_contested_marks(data: dict[str, Any]) -> int | None:
    contested_marks = 0
    found_contested_marks = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_contested_marks = player.contested_marks
        if player_contested_marks is None:
            continue
        found_contested_marks = True
        contested_marks += player_contested_marks
    if not found_contested_marks:
        return None
    return contested_marks


def _calculate_marks_inside(data: dict[str, Any]) -> int | None:
    marks_inside = 0
    found_marks_inside = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_marks_inside = player.marks_inside
        if player_marks_inside is None:
            continue
        found_marks_inside = True
        marks_inside += player_marks_inside
    if not found_marks_inside:
        return None
    return marks_inside


def _calculate_one_percenters(data: dict[str, Any]) -> int | None:
    one_percenters = 0
    found_one_percenters = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_one_percenters = player.one_percenters
        if player_one_percenters is None:
            continue
        found_one_percenters = True
        one_percenters += player_one_percenters
    if not found_one_percenters:
        return None
    return one_percenters


def _calculate_bounces(data: dict[str, Any]) -> int | None:
    bounces = 0
    found_bounces = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_bounces = player.bounces
        if player_bounces is None:
            continue
        found_bounces = True
        bounces += player_bounces
    if not found_bounces:
        return None
    return bounces


def _calculate_goal_assists(data: dict[str, Any]) -> int | None:
    goal_assists = 0
    found_goal_assists = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_goal_assists = player.goal_assists
        if player_goal_assists is None:
            continue
        found_goal_assists = True
        goal_assists += player_goal_assists
    if not found_goal_assists:
        return None
    return goal_assists


def _calcualte_field_goals_percentage(data: dict[str, Any]) -> float | None:
    field_goals = data.get(FIELD_GOALS_COLUMN)
    if field_goals is None:
        return None
    field_goals_attempted = data.get(FIELD_GOALS_ATTEMPTED_COLUMN)
    if field_goals_attempted is None:
        return None
    if field_goals_attempted == 0:
        return 0.0
    return float(field_goals) / float(field_goals_attempted)  # type: ignore


def _calculate_three_point_field_goals(data: dict[str, Any]) -> int | None:
    three_point_field_goals = 0
    found_three_point_field_goals = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_three_point_field_goals = player.three_point_field_goals
        if player_three_point_field_goals is None:
            continue
        found_three_point_field_goals = True
        three_point_field_goals += player_three_point_field_goals
    if not found_three_point_field_goals:
        return None
    return three_point_field_goals


def _calculate_three_point_field_goals_attempted(data: dict[str, Any]) -> int | None:
    three_point_field_goals_attempted = 0
    found_three_point_field_goals_attempted = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_three_point_field_goals_attempted = (
            player.three_point_field_goals_attempted
        )
        if player_three_point_field_goals_attempted is None:
            continue
        found_three_point_field_goals_attempted = True
        three_point_field_goals_attempted += player_three_point_field_goals_attempted
    if not found_three_point_field_goals_attempted:
        return None
    return three_point_field_goals_attempted


def _calculate_three_point_field_goals_percentage(data: dict[str, Any]) -> float | None:
    three_point_field_goals = data.get(TEAM_THREE_POINT_FIELD_GOALS_COLUMN)
    if three_point_field_goals is None:
        return None
    three_point_field_goals_attempted = data.get(
        TEAM_THREE_POINT_FIELD_GOALS_ATTEMPTED_COLUMN
    )
    if three_point_field_goals_attempted is None:
        return None
    if three_point_field_goals_attempted == 0:
        return 0.0
    return float(three_point_field_goals) / float(three_point_field_goals_attempted)  # type: ignore


def _calculate_free_throws(data: dict[str, Any]) -> int | None:
    free_throws = 0
    found_free_throws = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_free_throws = player.free_throws
        if player_free_throws is None:
            continue
        found_free_throws = True
        free_throws += player_free_throws
    if not found_free_throws:
        return None
    return free_throws


def _calculate_free_throws_attempted(data: dict[str, Any]) -> int | None:
    free_throws_attempted = 0
    found_free_throws_attempted = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_free_throws_attempted = player.free_throws_attempted
        if player_free_throws_attempted is None:
            continue
        found_free_throws_attempted = True
        free_throws_attempted += player_free_throws_attempted
    if not found_free_throws_attempted:
        return None
    return free_throws_attempted


def _calculate_free_throws_percentage(data: dict[str, Any]) -> float | None:
    free_throws = data.get(TEAM_FREE_THROWS_COLUMN)
    if free_throws is None:
        return None
    free_throws_attempted = data.get(TEAM_FREE_THROWS_ATTEMPTED_COLUMN)
    if free_throws_attempted is None:
        return None
    if free_throws_attempted == 0:
        return 0.0
    return float(free_throws) / float(free_throws_attempted)  # type: ignore


def _calculate_defensive_rebounds(data: dict[str, Any]) -> int | None:
    defensive_rebounds = 0
    found_defensive_rebounds = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_defensive_rebounds = player.defensive_rebounds
        if player_defensive_rebounds is None:
            continue
        found_defensive_rebounds = True
        defensive_rebounds += player_defensive_rebounds
    if not found_defensive_rebounds:
        return None
    return defensive_rebounds


def _calculate_total_rebounds(data: dict[str, Any]) -> int | None:
    offensive_rebounds = data.get(OFFENSIVE_REBOUNDS_COLUMN)
    if offensive_rebounds is None:
        return None
    defensive_rebounds = data.get(TEAM_DEFENSIVE_REBOUNDS_COLUMN)
    if defensive_rebounds is None:
        return None
    return offensive_rebounds + defensive_rebounds


def _calculate_steals(data: dict[str, Any]) -> int | None:
    steals = 0
    found_steals = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_steals = player.steals
        if player_steals is None:
            continue
        found_steals = True
        steals += player_steals
    if not found_steals:
        return None
    return steals


def _calculate_blocks(data: dict[str, Any]) -> int | None:
    blocks = 0
    found_blocks = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_blocks = player.blocks
        if player_blocks is None:
            continue
        found_blocks = True
        blocks += player_blocks
    if not found_blocks:
        return None
    return blocks


def _calculate_personal_fouls(data: dict[str, Any]) -> int | None:
    personal_fouls = 0
    found_personal_fouls = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_personal_fouls = player.personal_fouls
        if player_personal_fouls is None:
            continue
        found_personal_fouls = True
        personal_fouls += player_personal_fouls
    if not found_personal_fouls:
        return None
    return personal_fouls


def _calculate_forced_fumbles(data: dict[str, Any]) -> float | None:
    forced_fumbles = 0.0
    found_forced_fumbles = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_forced_fumbles = player.forced_fumbles
        if player_forced_fumbles is None:
            continue
        found_forced_fumbles = True
        forced_fumbles += player_forced_fumbles
    if not found_forced_fumbles:
        return None
    return forced_fumbles


def _calculate_fumbles_recovered(data: dict[str, Any]) -> float | None:
    fumbles_recovered = 0.0
    found_fumbles_recovered = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_fumbles_recovered = player.fumbles_recovered
        if player_fumbles_recovered is None:
            continue
        found_fumbles_recovered = True
        fumbles_recovered += player_fumbles_recovered
    if not found_fumbles_recovered:
        return None
    return fumbles_recovered


def _calculate_fumbles_touchdowns(data: dict[str, Any]) -> float | None:
    fumbles_touchdowns = 0.0
    found_fumbles_touchdowns = False
    for player in data.get(PLAYER_COLUMN_PREFIX, []):
        player_fumbles_touchdowns = player.fumbles_touchdowns
        if player_fumbles_touchdowns is None:
            continue
        found_fumbles_touchdowns = True
        fumbles_touchdowns += player_fumbles_touchdowns
    if not found_fumbles_touchdowns:
        return None
    return fumbles_touchdowns


class TeamModel(BaseModel):
    """The serialisable team class."""

    identifier: str = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL},
        alias=TEAM_IDENTIFIER_COLUMN,
    )
    name: str = Field(
        ..., json_schema_extra={TYPE_KEY: FieldType.TEXT}, alias=NAME_COLUMN
    )
    location: str | None = Field(
        ..., json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL}
    )
    players: list[PlayerModel] = Field(..., alias=PLAYER_COLUMN_PREFIX)
    odds: list[OddsModel] = Field(..., alias=TEAM_ODDS_COLUMN)
    points: float | None = Field(
        ..., json_schema_extra={TYPE_KEY: FieldType.POINTS}, alias=TEAM_POINTS_COLUMN
    )
    ladder_rank: int | None
    kicks: int | None = Field(
        default_factory=_calculate_kicks,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=KICKS_COLUMN,
    )
    news: list[NewsModel] = Field(..., alias=TEAM_NEWS_COLUMN)
    social: list[SocialModel]
    field_goals: int | None = Field(
        default_factory=_calculate_field_goals,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=FIELD_GOALS_COLUMN,
    )
    field_goals_attempted: int | None = Field(
        default_factory=_calculate_field_goals_attempted,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=FIELD_GOALS_ATTEMPTED_COLUMN,
    )
    offensive_rebounds: int | None = Field(
        default_factory=_calculate_offensive_rebounds,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=OFFENSIVE_REBOUNDS_COLUMN,
    )
    assists: int | None = Field(
        default_factory=_calculate_assists,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=ASSISTS_COLUMN,
    )
    turnovers: int | None = Field(
        default_factory=_calculate_turnovers,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TURNOVERS_COLUMN,
    )
    marks: int | None = Field(
        default_factory=_calculate_marks,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_MARKS_COLUMN,
    )
    handballs: int | None = Field(
        default_factory=_calculate_handballs,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_HANDBALLS_COLUMN,
    )
    disposals: int | None = Field(
        default_factory=_calculate_disposals,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_DISPOSALS_COLUMN,
    )
    goals: int | None = Field(
        default_factory=_calculate_goals,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_GOALS_COLUMN,
    )
    behinds: int | None = Field(
        default_factory=_calculate_behinds,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_BEHINDS_COLUMN,
    )
    hit_outs: int | None = Field(
        default_factory=_calculate_hit_outs,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_HIT_OUTS_COLUMN,
    )
    tackles: int | None = Field(
        default_factory=_calculate_tackles,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_TACKLES_COLUMN,
    )
    rebounds: int | None = Field(
        default_factory=_calculate_rebounds,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_REBOUNDS_COLUMN,
    )
    insides: int | None = Field(
        default_factory=_calculate_insides,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_INSIDES_COLUMN,
    )
    clearances: int | None = Field(
        default_factory=_calculate_clearances,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_CLEARANCES_COLUMN,
    )
    clangers: int | None = Field(
        default_factory=_calculate_clangers,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_CLANGERS_COLUMN,
    )
    free_kicks_for: int | None = Field(
        default_factory=_calculate_free_kicks_for,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FREE_KICKS_FOR_COLUMN,
    )
    free_kicks_against: int | None = Field(
        default_factory=_calculate_free_kicks_against,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FREE_KICKS_AGAINST_COLUMN,
    )
    brownlow_votes: int | None = Field(
        default_factory=_calculate_brownlow_votes,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_BROWNLOW_VOTES_COLUMN,
    )
    contested_possessions: int | None = Field(
        default_factory=_calculate_contested_possessions,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_CONTESTED_POSSESSIONS_COLUMN,
    )
    uncontested_possessions: int | None = Field(
        default_factory=_calculate_uncontested_possessions,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_UNCONTESTED_POSSESSIONS_COLUMN,
    )
    contested_marks: int | None = Field(
        default_factory=_calculate_contested_marks,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_CONTESTED_MARKS_COLUMN,
    )
    marks_inside: int | None = Field(
        default_factory=_calculate_marks_inside,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_MARKS_INSIDE_COLUMN,
    )
    one_percenters: int | None = Field(
        default_factory=_calculate_one_percenters,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_ONE_PERCENTERS_COLUMN,
    )
    bounces: int | None = Field(
        default_factory=_calculate_bounces,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_BOUNCES_COLUMN,
    )
    goal_assists: int | None = Field(
        default_factory=_calculate_goal_assists,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_GOAL_ASSISTS_COLUMN,
    )
    coaches: list[CoachModel] = Field(
        ..., json_schema_extra={FFILL_KEY: True}, alias=TEAM_COACHES_COLUMN
    )
    lbw: float | None = Field(
        ...,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_LENGTH_BEHIND_WINNER_COLUMN,
    )
    end_dt: datetime.datetime | None = Field(
        ..., json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD}, alias=TEAM_END_DT_COLUMN
    )
    field_goals_percentage: float | None = Field(
        default_factory=_calcualte_field_goals_percentage,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FIELD_GOALS_PERCENTAGE_COLUMN,
    )
    three_point_field_goals: int | None = Field(
        default_factory=_calculate_three_point_field_goals,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_THREE_POINT_FIELD_GOALS_COLUMN,
    )
    three_point_field_goals_attempted: int | None = Field(
        default_factory=_calculate_three_point_field_goals_attempted,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_THREE_POINT_FIELD_GOALS_ATTEMPTED_COLUMN,
    )
    three_point_field_goals_percentage: float | None = Field(
        default_factory=_calculate_three_point_field_goals_percentage,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_THREE_POINT_FIELD_GOALS_PERCENTAGE_COLUMN,
    )
    free_throws: int | None = Field(
        default_factory=_calculate_free_throws,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FREE_THROWS_COLUMN,
    )
    free_throws_attempted: int | None = Field(
        default_factory=_calculate_free_throws_attempted,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FREE_THROWS_ATTEMPTED_COLUMN,
    )
    free_throws_percentage: float | None = Field(
        default_factory=_calculate_free_throws_percentage,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FREE_THROWS_PERCENTAGE_COLUMN,
    )
    defensive_rebounds: int | None = Field(
        default_factory=_calculate_defensive_rebounds,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_DEFENSIVE_REBOUNDS_COLUMN,
    )
    total_rebounds: int | None = Field(
        default_factory=_calculate_total_rebounds,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_TOTAL_REBOUNDS_COLUMN,
    )
    steals: int | None = Field(
        default_factory=_calculate_steals,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_STEALS_COLUMN,
    )
    blocks: int | None = Field(
        default_factory=_calculate_blocks,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_BLOCKS_COLUMN,
    )
    personal_fouls: int | None = Field(
        default_factory=_calculate_personal_fouls,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_PERSONAL_FOULS_COLUMN,
    )
    forced_fumbles: float | None = Field(
        default_factory=_calculate_forced_fumbles,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FORCED_FUMBLES_COLUMN,
    )
    fumbles_recovered: float | None = Field(
        default_factory=_calculate_fumbles_recovered,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FUMBLES_RECOVERED_COLUMN,
    )
    fumbles_touchdowns: float | None = Field(
        default_factory=_calculate_fumbles_touchdowns,
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FUMBLES_TOUCHDOWNS_COLUMN,
    )
    runs: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_RUNS_COLUMN,
    )
    wickets: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_WICKETS_COLUMN,
    )
    overs: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_OVERS_COLUMN,
    )
    balls: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_BALLS_COLUMN,
    )
    byes: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_BYES_COLUMN,
    )
    leg_byes: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_LEG_BYES_COLUMN,
    )
    wides: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_WIDES_COLUMN,
    )
    no_balls: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_NO_BALLS_COLUMN,
    )
    penalties: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_PENALTIES_COLUMN,
    )
    balls_per_over: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_BALLS_PER_OVER_COLUMN,
    )
    fours: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_FOURS_COLUMN,
    )
    sixes: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_SIXES_COLUMN,
    )
    catches: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_CATCHES_COLUMN,
    )
    catches_dropped: int | None = Field(
        json_schema_extra={TYPE_KEY: FieldType.LOOKAHEAD},
        alias=TEAM_CATCHES_DROPPED_COLUMN,
    )
    version: str = Field(..., json_schema_extra={TYPE_KEY: FieldType.CATEGORICAL})
