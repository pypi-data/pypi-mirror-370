"""ESPN player model."""

# pylint: disable=duplicate-code,too-many-locals,too-many-branches,line-too-long,too-many-lines,too-many-statements
import datetime
import logging
from typing import Any

import pytest_is_running
import requests_cache
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from ...cache import MEMORY
from ..google.address_exception import AddressException
from ..google.google_address_model import create_google_address_model
from ..player_model import VERSION, PlayerModel
from ..sex import Sex
from ..species import Species
from ..venue_model import VERSION as VENUE_VERSION
from .espn_venue_model import create_espn_venue_model

_BAD_URLS = {
    "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/athletes/4689686?lang=en&region=us",
    "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/athletes/2333612?lang=en&region=us",
    "http://sports.core.api.espn.com/v2/sports/football/leagues/college-football/seasons/2021/athletes/4426888?lang=en&region=us",
}


def _create_espn_player_model(
    session: requests_cache.CachedSession,
    player: dict[str, Any],
    positions_validator: dict[str, str],
    dt: datetime.datetime,
    version: str,
) -> PlayerModel:
    identifier = str(player["playerId"])
    jersey = player.get("jersey")
    fumbles = None
    fumbles_lost = None
    forced_fumbles = None
    fumbles_recovered = None
    fumbles_recovered_yards = None
    fumbles_touchdowns = None
    offensive_two_point_returns = None
    offensive_fumbles_touchdowns = None
    defensive_fumbles_touchdowns = None
    average_gain = None
    completion_percentage = None
    completions = None
    espn_quarterback_rating = None
    interception_percentage = None
    interceptions = None
    long_passing = None
    misc_yards = None
    net_passing_yards = None
    net_total_yards = None
    passing_attempts = None
    passing_big_plays = None
    passing_first_downs = None
    passing_fumbles = None
    passing_fumbles_lost = None
    passing_touchdown_percentage = None
    passing_touchdowns = None
    passing_yards = None
    passing_yards_after_catch = None
    quarterback_rating = None
    sacks = None
    passing_yards_at_catch = None
    sacks_yards_lost = None
    net_passing_attempts = None
    total_offensive_plays = None
    total_points = None
    total_touchdowns = None
    total_yards = None
    total_yards_from_scrimmage = None
    two_point_pass = None
    two_point_pass_attempt = None
    yards_per_completion = None
    yards_per_pass_attempt = None
    net_yards_per_pass_attempt = None
    long_rushing = None
    rushing_attempts = None
    rushing_big_plays = None
    rushing_first_downs = None
    rushing_fumbles = None
    rushing_fumbles_lost = None
    rushing_touchdowns = None
    rushing_yards = None
    stuffs = None
    stuff_yards_lost = None
    two_point_rush = None
    two_point_rush_attempts = None
    yards_per_rush_attempt = None
    espn_widereceiver = None
    long_reception = None
    receiving_big_plays = None
    receiving_first_downs = None
    receiving_fumbles = None
    receiving_fumbles_lost = None
    receiving_targets = None
    receiving_touchdowns = None
    receiving_yards = None
    receiving_yards_after_catch = None
    receiving_yards_at_catch = None
    receptions = None
    two_point_receptions = None
    two_point_reception_attempts = None
    yards_per_reception = None
    assist_tackles = None
    average_interception_yards = None
    average_sack_yards = None
    average_stuff_yards = None
    blocked_field_goal_touchdowns = None
    blocked_punt_touchdowns = None
    defensive_touchdowns = None
    hurries = None
    kicks_blocked = None
    long_interception = None
    misc_touchdowns = None
    passes_batted_down = None
    passes_defended = None
    quarterback_hits = None
    sacks_assisted = None
    sacks_unassisted = None
    sacks_yards = None
    safeties = None
    solo_tackles = None
    stuff_yards = None
    tackles_for_loss = None
    tackles_yards_lost = None
    yards_allowed = None
    points_allowed = None
    one_point_safeties_made = None
    missed_field_goal_return_td = None
    blocked_punt_ez_rec_td = None
    interception_touchdowns = None
    interception_yards = None
    average_kickoff_return_yards = None
    average_kickoff_yards = None
    extra_point_attempts = None
    extra_point_percentage = None
    extra_point_blocked = None
    extra_points_blocked_percentage = None
    extra_points_made = None
    fair_catches = None
    fair_catch_percentage = None
    field_goal_attempts_max_19_yards = None
    field_goal_attempts_max_29_yards = None
    field_goal_attempts_max_39_yards = None
    field_goal_attempts_max_49_yards = None
    field_goal_attempts_max_59_yards = None
    field_goal_attempts_max_99_yards = None
    field_goal_attempts_above_50_yards = None
    field_goal_attempt_yards = None
    field_goals_blocked = None
    field_goals_blocked_percentage = None
    field_goals_made = None
    field_goals_made_max_19_yards = None
    field_goals_made_max_29_yards = None
    field_goals_made_max_39_yards = None
    field_goals_made_max_49_yards = None
    field_goals_made_max_59_yards = None
    field_goals_made_max_99_yards = None
    field_goals_made_above_50_yards = None
    field_goals_made_yards = None
    field_goals_missed_yards = None
    kickoff_out_of_bounds = None
    kickoff_returns = None
    kickoff_returns_touchdowns = None
    kickoff_return_yards = None
    kickoffs = None
    kickoff_yards = None
    long_field_goal_attempt = None
    long_field_goal_made = None
    long_kickoff = None
    total_kicking_points = None
    touchback_percentage = None
    touchbacks = None
    defensive_fumble_returns = None
    defensive_fumble_return_yards = None
    fumble_recoveries = None
    fumble_recovery_yards = None
    kick_return_fair_catches = None
    kick_return_fair_catch_percentage = None
    kick_return_fumbles = None
    kick_return_fumbles_lost = None
    kick_returns = None
    kick_return_touchdowns = None
    kick_return_yards = None
    long_kick_return = None
    long_punt_return = None
    misc_fumble_returns = None
    misc_fumble_return_yards = None
    opposition_fumble_recoveries = None
    opposition_fumble_recovery_yards = None
    opposition_special_team_fumble_returns = None
    opposition_special_team_fumble_return_yards = None
    punt_return_fair_catches = None
    punt_return_fair_catch_percentage = None
    punt_return_fumbles = None
    punt_return_fumbles_lost = None
    punt_returns = None
    punt_returns_started_inside_the_10 = None
    punt_returns_started_inside_the_20 = None
    punt_return_touchdowns = None
    special_team_fumble_returns = None
    yards_per_kick_return = None
    yards_per_punt_return = None
    yards_per_return = None
    average_punt_return_yards = None
    gross_average_punt_yards = None
    long_punt = None
    net_average_punt_yards = None
    punts = None
    punts_blocked = None
    punts_blocked_percentage = None
    punts_inside_10 = None
    punts_inside_10_percentage = None
    punts_inside_20 = None
    punts_inside_20_percentage = None
    punts_over_50 = None
    punt_yards = None
    defensive_points = None
    misc_points = None
    return_touchdowns = None
    total_two_point_conversions = None
    passing_touchdowns_9_yards = None
    passing_touchdowns_19_yards = None
    passing_touchdowns_29_yards = None
    passing_touchdowns_39_yards = None
    passing_touchdowns_49_yards = None
    passing_touchdowns_above_50_yards = None
    receiving_touchdowns_9_yards = None
    receiving_touchdowns_19_yards = None
    receiving_touchdowns_29_yards = None
    receiving_touchdowns_39_yards = None
    punt_return_yards = None
    receiving_touchdowns_49_yards = None
    receiving_touchdowns_above_50_yards = None
    rushing_touchdowns_9_yards = None
    rushing_touchdowns_19_yards = None
    rushing_touchdowns_29_yards = None
    rushing_touchdowns_39_yards = None
    rushing_touchdowns_49_yards = None
    rushing_touchdowns_above_50_yards = None
    if "statistics" in player:
        statistics_response = session.get(player["statistics"]["$ref"])
        if statistics_response.ok:
            statistics_dict = statistics_response.json()
            fumbles = None
            for category in statistics_dict["splits"]["categories"]:
                for stat in category["stats"]:
                    if stat["name"] == "fumbles":
                        fumbles = stat["value"]
                    elif stat["name"] == "fumblesLost":
                        fumbles_lost = stat["value"]
                    elif stat["name"] == "fumblesForced":
                        forced_fumbles = stat["value"]
                    elif stat["name"] == "fumblesRecovered":
                        fumbles_recovered = stat["value"]
                    elif stat["name"] == "fumblesRecoveredYards":
                        fumbles_recovered_yards = stat["value"]
                    elif stat["name"] == "fumblesTouchdowns":
                        fumbles_touchdowns = stat["value"]
                    elif stat["name"] == "offensiveTwoPtReturns":
                        offensive_two_point_returns = stat["value"]
                    elif stat["name"] == "offensiveFumblesTouchdowns":
                        offensive_fumbles_touchdowns = stat["value"]
                    elif stat["name"] == "defensiveFumblesTouchdowns":
                        defensive_fumbles_touchdowns = stat["value"]
                    elif stat["name"] == "avgGain":
                        average_gain = stat["value"]
                    elif stat["name"] == "completionPct":
                        completion_percentage = stat["value"]
                    elif stat["name"] == "completions":
                        completions = stat["value"]
                    elif stat["name"] == "ESPNQBRating":
                        espn_quarterback_rating = stat["value"]
                    elif stat["name"] == "interceptionPct":
                        interception_percentage = stat["value"]
                    elif stat["name"] == "interceptions":
                        interceptions = stat["value"]
                    elif stat["name"] == "longPassing":
                        long_passing = stat["value"]
                    elif stat["name"] == "miscYards":
                        misc_yards = stat["value"]
                    elif stat["name"] == "netPassingYards":
                        net_passing_yards = stat["value"]
                    elif stat["name"] == "netTotalYards":
                        net_total_yards = stat["value"]
                    elif stat["name"] == "passingAttempts":
                        passing_attempts = stat["value"]
                    elif stat["name"] == "passingBigPlays":
                        passing_big_plays = stat["value"]
                    elif stat["name"] == "passingFirstDowns":
                        passing_first_downs = stat["value"]
                    elif stat["name"] == "passingFumbles":
                        passing_fumbles = stat["value"]
                    elif stat["name"] == "passingFumblesLost":
                        passing_fumbles_lost = stat["value"]
                    elif stat["name"] == "passingTouchdownPct":
                        passing_touchdown_percentage = stat["value"]
                    elif stat["name"] == "passingTouchdowns":
                        passing_touchdowns = stat["value"]
                    elif stat["name"] == "passingYards":
                        passing_yards = stat["value"]
                    elif stat["name"] == "passingYardsAfterCatch":
                        passing_yards_after_catch = stat["value"]
                    elif stat["name"] == "QBRating":
                        quarterback_rating = stat["value"]
                    elif stat["name"] == "sacks":
                        sacks = stat["value"]
                    elif stat["name"] == "passingYardsAtCatch":
                        passing_yards_at_catch = stat["value"]
                    elif stat["name"] == "sackYardsLost":
                        sacks_yards_lost = stat["value"]
                    elif stat["name"] == "netPassingAttempts":
                        net_passing_attempts = stat["value"]
                    elif stat["name"] == "totalOffensivePlays":
                        total_offensive_plays = stat["value"]
                    elif stat["name"] == "totalPoints":
                        total_points = stat["value"]
                    elif stat["name"] == "totalTouchdowns":
                        total_touchdowns = stat["value"]
                    elif stat["name"] == "totalYards":
                        total_yards = stat["value"]
                    elif stat["name"] == "totalYardsFromScrimmage":
                        total_yards_from_scrimmage = stat["value"]
                    elif stat["name"] == "twoPtPass":
                        two_point_pass = stat["value"]
                    elif stat["name"] == "twoPtPassAttempts":
                        two_point_pass_attempt = stat["value"]
                    elif stat["name"] == "yardsPerCompletion":
                        yards_per_completion = stat["value"]
                    elif stat["name"] == "yardsPerPassAttempt":
                        yards_per_pass_attempt = stat["value"]
                    elif stat["name"] == "netYardsPerPassAttempt":
                        net_yards_per_pass_attempt = stat["value"]
                    elif stat["name"] == "longRushing":
                        long_rushing = stat["value"]
                    elif stat["name"] == "rushingAttempts":
                        rushing_attempts = stat["value"]
                    elif stat["name"] == "rushingBigPlays":
                        rushing_big_plays = stat["value"]
                    elif stat["name"] == "rushingFirstDowns":
                        rushing_first_downs = stat["value"]
                    elif stat["name"] == "rushingFumbles":
                        rushing_fumbles = stat["value"]
                    elif stat["name"] == "rushingFumblesLost":
                        rushing_fumbles_lost = stat["value"]
                    elif stat["name"] == "rushingTouchdowns":
                        rushing_touchdowns = stat["value"]
                    elif stat["name"] == "rushingYards":
                        rushing_yards = stat["value"]
                    elif stat["name"] == "stuffs":
                        stuffs = stat["value"]
                    elif stat["name"] == "stuffYardsLost":
                        stuff_yards_lost = stat["value"]
                    elif stat["name"] == "twoPtRush":
                        two_point_rush = stat["value"]
                    elif stat["name"] == "twoPtRushAttempts":
                        two_point_rush_attempts = stat["value"]
                    elif stat["name"] == "yardsPerRushAttempt":
                        yards_per_rush_attempt = stat["value"]
                    elif stat["name"] == "ESPNWRRating":
                        espn_widereceiver = stat["value"]
                    elif stat["name"] == "longReception":
                        long_reception = stat["value"]
                    elif stat["name"] == "receivingBigPlays":
                        receiving_big_plays = stat["value"]
                    elif stat["name"] == "receivingFirstDowns":
                        receiving_first_downs = stat["value"]
                    elif stat["name"] == "receivingFumbles":
                        receiving_fumbles = stat["value"]
                    elif stat["name"] == "receivingFumblesLost":
                        receiving_fumbles_lost = stat["value"]
                    elif stat["name"] == "receivingTargets":
                        receiving_targets = stat["value"]
                    elif stat["name"] == "receivingTouchdowns":
                        receiving_touchdowns = stat["value"]
                    elif stat["name"] == "receivingYards":
                        receiving_yards = stat["value"]
                    elif stat["name"] == "receivingYardsAfterCatch":
                        receiving_yards_after_catch = stat["value"]
                    elif stat["name"] == "receivingYardsAtCatch":
                        receiving_yards_at_catch = stat["value"]
                    elif stat["name"] == "receptions":
                        receptions = stat["value"]
                    elif stat["name"] == "twoPtReception":
                        two_point_receptions = stat["value"]
                    elif stat["name"] == "twoPtReceptionAttempts":
                        two_point_reception_attempts = stat["value"]
                    elif stat["name"] == "yardsPerReception":
                        yards_per_reception = stat["value"]
                    elif stat["name"] == "assistTackles":
                        assist_tackles = stat["value"]
                    elif stat["name"] == "avgInterceptionYards":
                        average_interception_yards = stat["value"]
                    elif stat["name"] == "avgSackYards":
                        average_sack_yards = stat["value"]
                    elif stat["name"] == "avgStuffYards":
                        average_stuff_yards = stat["value"]
                    elif stat["name"] == "blockedFieldGoalTouchdowns":
                        blocked_field_goal_touchdowns = stat["value"]
                    elif stat["name"] == "blockedPuntTouchdowns":
                        blocked_punt_touchdowns = stat["value"]
                    elif stat["name"] == "defensiveTouchdowns":
                        defensive_touchdowns = stat["value"]
                    elif stat["name"] == "hurries":
                        hurries = stat["value"]
                    elif stat["name"] == "kicksBlocked":
                        kicks_blocked = stat["value"]
                    elif stat["name"] == "longInterception":
                        long_interception = stat["value"]
                    elif stat["name"] == "miscTouchdowns":
                        misc_touchdowns = stat["value"]
                    elif stat["name"] == "passesBattedDown":
                        passes_batted_down = stat["value"]
                    elif stat["name"] == "passesDefended":
                        passes_defended = stat["value"]
                    elif stat["name"] == "QBHits":
                        quarterback_hits = stat["value"]
                    elif stat["name"] == "sacksAssisted":
                        sacks_assisted = stat["value"]
                    elif stat["name"] == "sacksUnassisted":
                        sacks_unassisted = stat["value"]
                    elif stat["name"] == "sackYards":
                        sacks_yards = stat["value"]
                    elif stat["name"] == "safeties":
                        safeties = stat["value"]
                    elif stat["name"] == "soloTackles":
                        solo_tackles = stat["value"]
                    elif stat["name"] == "stuffYards":
                        stuff_yards = stat["value"]
                    elif stat["name"] == "tacklesForLoss":
                        tackles_for_loss = stat["value"]
                    elif stat["name"] == "tacklesYardsLost":
                        tackles_yards_lost = stat["value"]
                    elif stat["name"] == "yardsAllowed":
                        yards_allowed = stat["value"]
                    elif stat["name"] == "pointsAllowed":
                        points_allowed = stat["value"]
                    elif stat["name"] == "onePtSafetiesMade":
                        one_point_safeties_made = stat["value"]
                    elif stat["name"] == "missedFieldGoalReturnTd":
                        missed_field_goal_return_td = stat["value"]
                    elif stat["name"] == "blockedPuntEzRecTd":
                        blocked_punt_ez_rec_td = stat["value"]
                    elif stat["name"] == "interceptionTouchdowns":
                        interception_touchdowns = stat["value"]
                    elif stat["name"] == "interceptionYards":
                        interception_yards = stat["value"]
                    elif stat["name"] == "avgKickoffReturnYards":
                        average_kickoff_return_yards = stat["value"]
                    elif stat["name"] == "avgKickoffYards":
                        average_kickoff_yards = stat["value"]
                    elif stat["name"] == "extraPointAttempts":
                        extra_point_attempts = stat["value"]
                    elif stat["name"] == "extraPointPct":
                        extra_point_percentage = stat["value"]
                    elif stat["name"] == "extraPointsBlocked":
                        extra_point_blocked = stat["value"]
                    elif stat["name"] == "extraPointsBlockedPct":
                        extra_points_blocked_percentage = stat["value"]
                    elif stat["name"] == "extraPointsMade":
                        extra_points_made = stat["value"]
                    elif stat["name"] == "fairCatches":
                        fair_catches = stat["value"]
                    elif stat["name"] == "fairCatchPct":
                        fair_catch_percentage = stat["value"]
                    elif stat["name"] == "fieldGoalAttempts1_19":
                        field_goal_attempts_max_19_yards = stat["value"]
                    elif stat["name"] == "fieldGoalAttempts20_29":
                        field_goal_attempts_max_29_yards = stat["value"]
                    elif stat["name"] == "fieldGoalAttempts30_39":
                        field_goal_attempts_max_39_yards = stat["value"]
                    elif stat["name"] == "fieldGoalAttempts40_49":
                        field_goal_attempts_max_49_yards = stat["value"]
                    elif stat["name"] == "fieldGoalAttempts50_59":
                        field_goal_attempts_max_59_yards = stat["value"]
                    elif stat["name"] == "fieldGoalAttempts60_99":
                        field_goal_attempts_max_99_yards = stat["value"]
                    elif stat["name"] == "fieldGoalAttempts50":
                        field_goal_attempts_above_50_yards = stat["value"]
                    elif stat["name"] == "fieldGoalAttemptYards":
                        field_goal_attempt_yards = stat["value"]
                    elif stat["name"] == "fieldGoalsBlocked":
                        field_goals_blocked = stat["value"]
                    elif stat["name"] == "fieldGoalsBlockedPct":
                        field_goals_blocked_percentage = stat["value"]
                    elif stat["name"] == "fieldGoalsMade":
                        field_goals_made = stat["value"]
                    elif stat["name"] == "fieldGoalsMade1_19":
                        field_goals_made_max_19_yards = stat["value"]
                    elif stat["name"] == "fieldGoalsMade20_29":
                        field_goals_made_max_29_yards = stat["value"]
                    elif stat["name"] == "fieldGoalsMade30_39":
                        field_goals_made_max_39_yards = stat["value"]
                    elif stat["name"] == "fieldGoalsMade40_49":
                        field_goals_made_max_49_yards = stat["value"]
                    elif stat["name"] == "fieldGoalsMade50_59":
                        field_goals_made_max_59_yards = stat["value"]
                    elif stat["name"] == "fieldGoalsMade60_99":
                        field_goals_made_max_99_yards = stat["value"]
                    elif stat["name"] == "fieldGoalsMade50":
                        field_goals_made_above_50_yards = stat["value"]
                    elif stat["name"] == "fieldGoalsMadeYards":
                        field_goals_made_yards = stat["value"]
                    elif stat["name"] == "fieldGoalsMissedYards":
                        field_goals_missed_yards = stat["value"]
                    elif stat["name"] == "kickoffOB":
                        kickoff_out_of_bounds = stat["value"]
                    elif stat["name"] == "kickoffReturns":
                        kickoff_returns = stat["value"]
                    elif stat["name"] == "kickoffReturnTouchdowns":
                        kickoff_returns_touchdowns = stat["value"]
                    elif stat["name"] == "kickoffReturnYards":
                        kickoff_return_yards = stat["value"]
                    elif stat["name"] == "kickoffs":
                        kickoffs = stat["value"]
                    elif stat["name"] == "kickoffYards":
                        kickoff_yards = stat["value"]
                    elif stat["name"] == "longFieldGoalAttempt":
                        long_field_goal_attempt = stat["value"]
                    elif stat["name"] == "longFieldGoalMade":
                        long_field_goal_made = stat["value"]
                    elif stat["name"] == "longKickoff":
                        long_kickoff = stat["value"]
                    elif stat["name"] == "totalKickingPoints":
                        total_kicking_points = stat["value"]
                    elif stat["name"] == "touchbackPct":
                        touchback_percentage = stat["value"]
                    elif stat["name"] == "touchbacks":
                        touchbacks = stat["value"]
                    elif stat["name"] == "defFumbleReturns":
                        defensive_fumble_returns = stat["value"]
                    elif stat["name"] == "defFumbleReturnYards":
                        defensive_fumble_return_yards = stat["value"]
                    elif stat["name"] == "fumbleRecoveries":
                        fumble_recoveries = stat["value"]
                    elif stat["name"] == "fumbleRecoveryYards":
                        fumble_recovery_yards = stat["value"]
                    elif stat["name"] == "kickReturnFairCatches":
                        kick_return_fair_catches = stat["value"]
                    elif stat["name"] == "kickReturnFairCatchPct":
                        kick_return_fair_catch_percentage = stat["value"]
                    elif stat["name"] == "kickReturnFumbles":
                        kick_return_fumbles = stat["value"]
                    elif stat["name"] == "kickReturnFumblesLost":
                        kick_return_fumbles_lost = stat["value"]
                    elif stat["name"] == "kickReturns":
                        kick_returns = stat["value"]
                    elif stat["name"] == "kickReturnTouchdowns":
                        kick_return_touchdowns = stat["value"]
                    elif stat["name"] == "kickReturnYards":
                        kick_return_yards = stat["value"]
                    elif stat["name"] == "longKickReturn":
                        long_kick_return = stat["value"]
                    elif stat["name"] == "longPuntReturn":
                        long_punt_return = stat["value"]
                    elif stat["name"] == "miscFumbleReturns":
                        misc_fumble_returns = stat["value"]
                    elif stat["name"] == "miscFumbleReturnYards":
                        misc_fumble_return_yards = stat["value"]
                    elif stat["name"] == "oppFumbleRecoveries":
                        opposition_fumble_recoveries = stat["value"]
                    elif stat["name"] == "oppFumbleRecoveryYards":
                        opposition_fumble_recovery_yards = stat["value"]
                    elif stat["name"] == "oppSpecialTeamFumbleReturns":
                        opposition_special_team_fumble_returns = stat["value"]
                    elif stat["name"] == "oppSpecialTeamFumbleReturnYards":
                        opposition_special_team_fumble_return_yards = stat["value"]
                    elif stat["name"] == "puntReturnFairCatches":
                        punt_return_fair_catches = stat["value"]
                    elif stat["name"] == "puntReturnFairCatchPct":
                        punt_return_fair_catch_percentage = stat["value"]
                    elif stat["name"] == "puntReturnFumbles":
                        punt_return_fumbles = stat["value"]
                    elif stat["name"] == "puntReturnFumblesLost":
                        punt_return_fumbles_lost = stat["value"]
                    elif stat["name"] == "puntReturns":
                        punt_returns = stat["value"]
                    elif stat["name"] == "puntReturnsStartedInsideThe10":
                        punt_returns_started_inside_the_10 = stat["value"]
                    elif stat["name"] == "puntReturnsStartedInsideThe20":
                        punt_returns_started_inside_the_20 = stat["value"]
                    elif stat["name"] == "puntReturnTouchdowns":
                        punt_return_touchdowns = stat["value"]
                    elif stat["name"] == "specialTeamFumbleReturns":
                        special_team_fumble_returns = stat["value"]
                    elif stat["name"] == "yardsPerKickReturn":
                        yards_per_kick_return = stat["value"]
                    elif stat["name"] == "yardsPerPuntReturn":
                        yards_per_punt_return = stat["value"]
                    elif stat["name"] == "yardsPerReturn":
                        yards_per_return = stat["value"]
                    elif stat["name"] == "avgPuntReturnYards":
                        average_punt_return_yards = stat["value"]
                    elif stat["name"] == "grossAvgPuntYards":
                        gross_average_punt_yards = stat["value"]
                    elif stat["name"] == "longPunt":
                        long_punt = stat["value"]
                    elif stat["name"] == "netAvgPuntYards":
                        net_average_punt_yards = stat["value"]
                    elif stat["name"] == "punts":
                        punts = stat["value"]
                    elif stat["name"] == "puntsBlocked":
                        punts_blocked = stat["value"]
                    elif stat["name"] == "puntsBlockedPct":
                        punts_blocked_percentage = stat["value"]
                    elif stat["name"] == "puntsInside10":
                        punts_inside_10 = stat["value"]
                    elif stat["name"] == "puntsInside10Pct":
                        punts_inside_10_percentage = stat["value"]
                    elif stat["name"] == "puntsInside20":
                        punts_inside_20 = stat["value"]
                    elif stat["name"] == "puntsInside20Pct":
                        punts_inside_20_percentage = stat["value"]
                    elif stat["name"] == "puntsOver50":
                        punts_over_50 = stat["value"]
                    elif stat["name"] == "puntYards":
                        punt_yards = stat["value"]
                    elif stat["name"] == "defensivePoints":
                        defensive_points = stat["value"]
                    elif stat["name"] == "miscPoints":
                        misc_points = stat["value"]
                    elif stat["name"] == "returnTouchdowns":
                        return_touchdowns = stat["value"]
                    elif stat["name"] == "totalTwoPointConvs":
                        total_two_point_conversions = stat["value"]
                    elif stat["name"] == "passingTouchdownsOf0to9Yds":
                        passing_touchdowns_9_yards = stat["value"]
                    elif stat["name"] == "passingTouchdownsOf10to19Yds":
                        passing_touchdowns_19_yards = stat["value"]
                    elif stat["name"] == "passingTouchdownsOf20to29Yds":
                        passing_touchdowns_29_yards = stat["value"]
                    elif stat["name"] == "passingTouchdownsOf30to39Yds":
                        passing_touchdowns_39_yards = stat["value"]
                    elif stat["name"] == "passingTouchdownsOf40to49Yds":
                        passing_touchdowns_49_yards = stat["value"]
                    elif stat["name"] == "passingTouchdownsOf50PlusYds":
                        passing_touchdowns_above_50_yards = stat["value"]
                    elif stat["name"] == "receivingTouchdownsOf0to9Yds":
                        receiving_touchdowns_9_yards = stat["value"]
                    elif stat["name"] == "receivingTouchdownsOf10to19Yds":
                        receiving_touchdowns_19_yards = stat["value"]
                    elif stat["name"] == "receivingTouchdownsOf20to29Yds":
                        receiving_touchdowns_29_yards = stat["value"]
                    elif stat["name"] == "receivingTouchdownsOf30to39Yds":
                        receiving_touchdowns_39_yards = stat["value"]
                    elif stat["name"] == "puntReturnYards":
                        punt_return_yards = stat["value"]
                    elif stat["name"] == "receivingTouchdownsOf40to49Yds":
                        receiving_touchdowns_49_yards = stat["value"]
                    elif stat["name"] == "receivingTouchdownsOf50PlusYds":
                        receiving_touchdowns_above_50_yards = stat["value"]
                    elif stat["name"] == "rushingTouchdownsOf0to9Yds":
                        rushing_touchdowns_9_yards = stat["value"]
                    elif stat["name"] == "rushingTouchdownsOf10to19Yds":
                        rushing_touchdowns_19_yards = stat["value"]
                    elif stat["name"] == "rushingTouchdownsOf20to29Yds":
                        rushing_touchdowns_29_yards = stat["value"]
                    elif stat["name"] == "rushingTouchdownsOf30to39Yds":
                        rushing_touchdowns_39_yards = stat["value"]
                    elif stat["name"] == "rushingTouchdownsOf40to49Yds":
                        rushing_touchdowns_49_yards = stat["value"]
                    elif stat["name"] == "rushingTouchdownsOf50PlusYds":
                        rushing_touchdowns_above_50_yards = stat["value"]
    athlete_dict = {}
    athelete_url = player["athlete"]["$ref"]
    if athelete_url not in _BAD_URLS:
        athlete_response = session.get(athelete_url)
        athlete_response.raise_for_status()
        athelete_url = athlete_response.url
        athlete_dict = athlete_response.json()
    position_response = session.get(player["position"]["$ref"])
    position_response.raise_for_status()
    position_dict = position_response.json()
    college_dict = {}
    if "college" in athlete_dict:
        college_url = athlete_dict["college"]["$ref"]
        if (
            college_url
            != "http://sports.core.api.espn.com/v2/colleges/429?lang=en&region=us"
        ):
            college_response = session.get(college_url)
            college_response.raise_for_status()
            college_dict = college_response.json()
    name = athlete_dict.get("fullName", identifier)

    birth_date = None
    try:
        birth_date = parse(athlete_dict["dateOfBirth"]).date()
    except KeyError:
        logging.debug("Failed to get birth date for %s", athelete_url)

    birth_place = athlete_dict.get("birthPlace", {})
    birth_address_components = []
    city = birth_place.get("city")
    if city is not None:
        birth_address_components.append(city)
    state = birth_place.get("state")
    if state is not None:
        birth_address_components.append(state)
    country = birth_place.get("country")
    if country is not None:
        birth_address_components.append(country)

    birth_address = None
    if not birth_address_components:
        query = ", ".join(birth_address_components).strip()
        if query:
            try:
                birth_address = create_google_address_model(
                    query=query,
                    session=session,
                    dt=None,
                )
            except ValueError:
                logging.warning("Failed to get birth address for: %s", query)

    position_abbreviation = position_dict["abbreviation"]
    college = None
    try:
        if "id" in college_dict:
            college = create_espn_venue_model(
                venue=college_dict, session=session, dt=dt, version=VENUE_VERSION
            )
    except (KeyError, AddressException) as exc:
        logging.warning("Failed to get college: %s", str(exc))

    headshot = None
    if "headshot" in athlete_dict:
        headshot = athlete_dict["headshot"]["href"]

    return PlayerModel(
        identifier=identifier,
        jersey=jersey,
        kicks=None,
        fumbles=fumbles,
        fumbles_lost=fumbles_lost,
        field_goals=None,
        field_goals_attempted=None,
        offensive_rebounds=None,
        assists=None,
        turnovers=None,
        name=name,
        marks=None,
        handballs=None,
        disposals=None,
        goals=None,
        behinds=None,
        hit_outs=None,
        tackles=None,
        rebounds=None,
        insides=None,
        clearances=None,
        clangers=None,
        free_kicks_for=None,
        free_kicks_against=None,
        brownlow_votes=None,
        contested_possessions=None,
        uncontested_possessions=None,
        contested_marks=None,
        marks_inside=None,
        one_percenters=None,
        bounces=None,
        goal_assists=None,
        percentage_played=None,
        birth_date=birth_date,
        species=str(Species.HUMAN),
        handicap_weight=None,
        father=None,
        sex=str(Sex.MALE),
        age=None if birth_date is None else relativedelta(birth_date, dt.date()).years,
        starting_position=positions_validator[position_abbreviation]
        if position_abbreviation != "-"
        else None,
        weight=athlete_dict["weight"] * 0.453592 if "weight" in athlete_dict else None,
        birth_address=birth_address,
        owner=None,
        seconds_played=None,
        three_point_field_goals=None,
        three_point_field_goals_attempted=None,
        free_throws=None,
        free_throws_attempted=None,
        defensive_rebounds=None,
        steals=None,
        blocks=None,
        personal_fouls=None,
        points=None,
        game_score=None,
        point_differential=None,
        version=version,
        height=athlete_dict["height"] * 2.54 if "height" in athlete_dict else None,
        colleges=[college] if college is not None else [],
        headshot=headshot,
        forced_fumbles=forced_fumbles,
        fumbles_recovered=fumbles_recovered,
        fumbles_recovered_yards=fumbles_recovered_yards,
        fumbles_touchdowns=fumbles_touchdowns,
        offensive_two_point_returns=offensive_two_point_returns,
        offensive_fumbles_touchdowns=offensive_fumbles_touchdowns,
        defensive_fumbles_touchdowns=defensive_fumbles_touchdowns,
        average_gain=average_gain,
        completion_percentage=completion_percentage,
        completions=completions,
        espn_quarterback_rating=espn_quarterback_rating,
        interception_percentage=interception_percentage,
        interceptions=interceptions,
        long_passing=long_passing,
        misc_yards=misc_yards,
        net_passing_yards=net_passing_yards,
        net_total_yards=net_total_yards,
        passing_attempts=passing_attempts,
        passing_big_plays=passing_big_plays,
        passing_first_downs=passing_first_downs,
        passing_fumbles=passing_fumbles,
        passing_fumbles_lost=passing_fumbles_lost,
        passing_touchdown_percentage=passing_touchdown_percentage,
        passing_touchdowns=passing_touchdowns,
        passing_yards=passing_yards,
        passing_yards_after_catch=passing_yards_after_catch,
        quarterback_rating=quarterback_rating,
        sacks=sacks,
        passing_yards_at_catch=passing_yards_at_catch,
        sacks_yards_lost=sacks_yards_lost,
        net_passing_attempts=net_passing_attempts,
        total_offensive_plays=total_offensive_plays,
        total_points=total_points,
        total_touchdowns=total_touchdowns,
        total_yards=total_yards,
        total_yards_from_scrimmage=total_yards_from_scrimmage,
        two_point_pass=two_point_pass,
        two_point_pass_attempt=two_point_pass_attempt,
        yards_per_completion=yards_per_completion,
        yards_per_pass_attempt=yards_per_pass_attempt,
        net_yards_per_pass_attempt=net_yards_per_pass_attempt,
        long_rushing=long_rushing,
        rushing_attempts=rushing_attempts,
        rushing_big_plays=rushing_big_plays,
        rushing_first_downs=rushing_first_downs,
        rushing_fumbles=rushing_fumbles,
        rushing_fumbles_lost=rushing_fumbles_lost,
        rushing_touchdowns=rushing_touchdowns,
        rushing_yards=rushing_yards,
        stuffs=stuffs,
        stuff_yards_lost=stuff_yards_lost,
        two_point_rush=two_point_rush,
        two_point_rush_attempts=two_point_rush_attempts,
        yards_per_rush_attempt=yards_per_rush_attempt,
        espn_widereceiver=espn_widereceiver,
        long_reception=long_reception,
        receiving_big_plays=receiving_big_plays,
        receiving_first_downs=receiving_first_downs,
        receiving_fumbles=receiving_fumbles,
        receiving_fumbles_lost=receiving_fumbles_lost,
        receiving_targets=receiving_targets,
        receiving_touchdowns=receiving_touchdowns,
        receiving_yards=receiving_yards,
        receiving_yards_after_catch=receiving_yards_after_catch,
        receiving_yards_at_catch=receiving_yards_at_catch,
        receptions=receptions,
        two_point_receptions=two_point_receptions,
        two_point_reception_attempts=two_point_reception_attempts,
        yards_per_reception=yards_per_reception,
        assist_tackles=assist_tackles,
        average_interception_yards=average_interception_yards,
        average_sack_yards=average_sack_yards,
        average_stuff_yards=average_stuff_yards,
        blocked_field_goal_touchdowns=blocked_field_goal_touchdowns,
        blocked_punt_touchdowns=blocked_punt_touchdowns,
        defensive_touchdowns=defensive_touchdowns,
        hurries=hurries,
        kicks_blocked=kicks_blocked,
        long_interception=long_interception,
        misc_touchdowns=misc_touchdowns,
        passes_batted_down=passes_batted_down,
        passes_defended=passes_defended,
        quarterback_hits=quarterback_hits,
        sacks_assisted=sacks_assisted,
        sacks_unassisted=sacks_unassisted,
        sacks_yards=sacks_yards,
        safeties=safeties,
        solo_tackles=solo_tackles,
        stuff_yards=stuff_yards,
        tackles_for_loss=tackles_for_loss,
        tackles_yards_lost=tackles_yards_lost,
        yards_allowed=yards_allowed,
        points_allowed=points_allowed,
        one_point_safeties_made=one_point_safeties_made,
        missed_field_goal_return_td=missed_field_goal_return_td,
        blocked_punt_ez_rec_td=blocked_punt_ez_rec_td,
        interception_touchdowns=interception_touchdowns,
        interception_yards=interception_yards,
        average_kickoff_return_yards=average_kickoff_return_yards,
        average_kickoff_yards=average_kickoff_yards,
        extra_point_attempts=extra_point_attempts,
        extra_point_percentage=extra_point_percentage,
        extra_point_blocked=extra_point_blocked,
        extra_points_blocked_percentage=extra_points_blocked_percentage,
        extra_points_made=extra_points_made,
        fair_catches=fair_catches,
        fair_catch_percentage=fair_catch_percentage,
        field_goal_attempts_max_19_yards=field_goal_attempts_max_19_yards,
        field_goal_attempts_max_29_yards=field_goal_attempts_max_29_yards,
        field_goal_attempts_max_39_yards=field_goal_attempts_max_39_yards,
        field_goal_attempts_max_49_yards=field_goal_attempts_max_49_yards,
        field_goal_attempts_max_59_yards=field_goal_attempts_max_59_yards,
        field_goal_attempts_max_99_yards=field_goal_attempts_max_99_yards,
        field_goal_attempts_above_50_yards=field_goal_attempts_above_50_yards,
        field_goal_attempt_yards=field_goal_attempt_yards,
        field_goals_blocked=field_goals_blocked,
        field_goals_blocked_percentage=field_goals_blocked_percentage,
        field_goals_made=field_goals_made,
        field_goals_made_max_19_yards=field_goals_made_max_19_yards,
        field_goals_made_max_29_yards=field_goals_made_max_29_yards,
        field_goals_made_max_39_yards=field_goals_made_max_39_yards,
        field_goals_made_max_49_yards=field_goals_made_max_49_yards,
        field_goals_made_max_59_yards=field_goals_made_max_59_yards,
        field_goals_made_max_99_yards=field_goals_made_max_99_yards,
        field_goals_made_above_50_yards=field_goals_made_above_50_yards,
        field_goals_made_yards=field_goals_made_yards,
        field_goals_missed_yards=field_goals_missed_yards,
        kickoff_out_of_bounds=kickoff_out_of_bounds,
        kickoff_returns=kickoff_returns,
        kickoff_returns_touchdowns=kickoff_returns_touchdowns,
        kickoff_return_yards=kickoff_return_yards,
        kickoffs=kickoffs,
        kickoff_yards=kickoff_yards,
        long_field_goal_attempt=long_field_goal_attempt,
        long_field_goal_made=long_field_goal_made,
        long_kickoff=long_kickoff,
        total_kicking_points=total_kicking_points,
        touchback_percentage=touchback_percentage,
        touchbacks=touchbacks,
        defensive_fumble_returns=defensive_fumble_returns,
        defensive_fumble_return_yards=defensive_fumble_return_yards,
        fumble_recoveries=fumble_recoveries,
        fumble_recovery_yards=fumble_recovery_yards,
        kick_return_fair_catches=kick_return_fair_catches,
        kick_return_fair_catch_percentage=kick_return_fair_catch_percentage,
        kick_return_fumbles=kick_return_fumbles,
        kick_return_fumbles_lost=kick_return_fumbles_lost,
        kick_returns=kick_returns,
        kick_return_touchdowns=kick_return_touchdowns,
        kick_return_yards=kick_return_yards,
        long_kick_return=long_kick_return,
        long_punt_return=long_punt_return,
        misc_fumble_returns=misc_fumble_returns,
        misc_fumble_return_yards=misc_fumble_return_yards,
        opposition_fumble_recoveries=opposition_fumble_recoveries,
        opposition_fumble_recovery_yards=opposition_fumble_recovery_yards,
        opposition_special_team_fumble_returns=opposition_special_team_fumble_returns,
        opposition_special_team_fumble_return_yards=opposition_special_team_fumble_return_yards,
        punt_return_fair_catches=punt_return_fair_catches,
        punt_return_fair_catch_percentage=punt_return_fair_catch_percentage,
        punt_return_fumbles=punt_return_fumbles,
        punt_return_fumbles_lost=punt_return_fumbles_lost,
        punt_returns=punt_returns,
        punt_returns_started_inside_the_10=punt_returns_started_inside_the_10,
        punt_returns_started_inside_the_20=punt_returns_started_inside_the_20,
        punt_return_touchdowns=punt_return_touchdowns,
        special_team_fumble_returns=special_team_fumble_returns,
        yards_per_kick_return=yards_per_kick_return,
        yards_per_punt_return=yards_per_punt_return,
        yards_per_return=yards_per_return,
        average_punt_return_yards=average_punt_return_yards,
        gross_average_punt_yards=gross_average_punt_yards,
        long_punt=long_punt,
        net_average_punt_yards=net_average_punt_yards,
        punts=punts,
        punts_blocked=punts_blocked,
        punts_blocked_percentage=punts_blocked_percentage,
        punts_inside_10=punts_inside_10,
        punts_inside_10_percentage=punts_inside_10_percentage,
        punts_inside_20=punts_inside_20,
        punts_inside_20_percentage=punts_inside_20_percentage,
        punts_over_50=punts_over_50,
        punt_yards=punt_yards,
        defensive_points=defensive_points,
        misc_points=misc_points,
        return_touchdowns=return_touchdowns,
        total_two_point_conversions=total_two_point_conversions,
        passing_touchdowns_9_yards=passing_touchdowns_9_yards,
        passing_touchdowns_19_yards=passing_touchdowns_19_yards,
        passing_touchdowns_29_yards=passing_touchdowns_29_yards,
        passing_touchdowns_39_yards=passing_touchdowns_39_yards,
        passing_touchdowns_49_yards=passing_touchdowns_49_yards,
        passing_touchdowns_above_50_yards=passing_touchdowns_above_50_yards,
        receiving_touchdowns_9_yards=receiving_touchdowns_9_yards,
        receiving_touchdowns_19_yards=receiving_touchdowns_19_yards,
        receiving_touchdowns_29_yards=receiving_touchdowns_29_yards,
        receiving_touchdowns_39_yards=receiving_touchdowns_39_yards,
        punt_return_yards=punt_return_yards,
        receiving_touchdowns_49_yards=receiving_touchdowns_49_yards,
        receiving_touchdowns_above_50_yards=receiving_touchdowns_above_50_yards,
        rushing_touchdowns_9_yards=rushing_touchdowns_9_yards,
        rushing_touchdowns_19_yards=rushing_touchdowns_19_yards,
        rushing_touchdowns_29_yards=rushing_touchdowns_29_yards,
        rushing_touchdowns_39_yards=rushing_touchdowns_39_yards,
        rushing_touchdowns_49_yards=rushing_touchdowns_49_yards,
        rushing_touchdowns_above_50_yards=rushing_touchdowns_above_50_yards,
        penalties_in_minutes=None,
        even_strength_goals=None,
        power_play_goals=None,
        short_handed_goals=None,
        game_winning_goals=None,
        even_strength_assists=None,
        power_play_assists=None,
        short_handed_assists=None,
        shots_on_goal=None,
        shooting_percentage=None,
        shifts=None,
        time_on_ice=None,
        decision=None,
        goals_against=None,
        shots_against=None,
        saves=None,
        save_percentage=None,
        shutouts=None,
        individual_corsi_for_events=None,
        on_shot_ice_for_events=None,
        on_shot_ice_against_events=None,
        corsi_for_percentage=None,
        relative_corsi_for_percentage=None,
        offensive_zone_starts=None,
        defensive_zone_starts=None,
        offensive_zone_start_percentage=None,
        hits=None,
        true_shooting_percentage=None,
        at_bats=None,
        runs_scored=None,
        runs_batted_in=None,
        bases_on_balls=None,
        strikeouts=None,
        plate_appearances=None,
        hits_at_bats=None,
        obp=None,
        slg=None,
        ops=None,
        pitches=None,
        strikes=None,
        win_probability_added=None,
        average_leverage_index=None,
        wpa_plus=None,
        wpa_minus=None,
        cwpa=None,
        acli=None,
        re24=None,
        putouts=None,
        innings_pitched=None,
        earned_runs=None,
        home_runs=None,
        era=None,
        batters_faced=None,
        strikes_by_contact=None,
        strikes_swinging=None,
        strikes_looking=None,
        ground_balls=None,
        fly_balls=None,
        line_drives=None,
        inherited_runners=None,
        inherited_scores=None,
        effective_field_goal_percentage=None,
        penalty_kicks_made=None,
        penalty_kicks_attempted=None,
        shots_total=None,
        shots_on_target=None,
        yellow_cards=None,
        red_cards=None,
        touches=None,
        expected_goals=None,
        non_penalty_expected_goals=None,
        expected_assisted_goals=None,
        shot_creating_actions=None,
        goal_creating_actions=None,
        passes_completed=None,
        passes_attempted=None,
        pass_completion=None,
        progressive_passes=None,
        carries=None,
        progressive_carries=None,
        take_ons_attempted=None,
        successful_take_ons=None,
        total_passing_distance=None,
        progressive_passing_distance=None,
        passes_completed_short=None,
        passes_attempted_short=None,
        pass_completion_short=None,
        passes_completed_medium=None,
        passes_attempted_medium=None,
        pass_completion_medium=None,
        passes_completed_long=None,
        passes_attempted_long=None,
        pass_completion_long=None,
        expected_assists=None,
        key_passes=None,
        passes_into_final_third=None,
        passes_into_penalty_area=None,
        crosses_into_penalty_area=None,
        live_ball_passes=None,
        dead_ball_passes=None,
        passes_from_free_kicks=None,
        through_balls=None,
        switches=None,
        crosses=None,
        throw_ins_taken=None,
        corner_kicks=None,
        inswinging_corner_kicks=None,
        outswinging_corner_kicks=None,
        straight_corner_kicks=None,
        passes_offside=None,
        passes_blocked=None,
        tackles_won=None,
        tackles_in_defensive_third=None,
        tackles_in_middle_third=None,
        tackles_in_attacking_third=None,
        dribblers_tackled=None,
        dribbles_challenged=None,
        percent_of_dribblers_tackled=None,
        challenges_lost=None,
        shots_blocked=None,
        tackles_plus_interceptions=None,
        errors=None,
        touches_in_defensive_penalty_area=None,
        touches_in_defensive_third=None,
        touches_in_middle_third=None,
        touches_in_attacking_third=None,
        touches_in_attacking_penalty_area=None,
        live_ball_touches=None,
        successful_take_on_percentage=None,
        times_tackled_during_take_ons=None,
        tackled_during_take_on_percentage=None,
        total_carrying_distance=None,
        progressive_carrying_distance=None,
        carries_into_final_third=None,
        carries_into_penalty_area=None,
        miscontrols=None,
        dispossessed=None,
        passes_received=None,
        progressive_passes_received=None,
        second_yellow_card=None,
        fouls_committed=None,
        fouls_drawn=None,
        offsides=None,
        penalty_kicks_won=None,
        penalty_kicks_conceded=None,
        own_goals=None,
        ball_recoveries=None,
        aerials_won=None,
        aerials_lost=None,
        percentage_of_aerials_won=None,
        shots_on_target_against=None,
        post_shot_expected_goals=None,
        passes_attempted_minus_goal_kicks=None,
        throws_attempted=None,
        percentage_of_passes_that_were_launched=None,
        average_pass_length=None,
        goal_kicks_attempted=None,
        percentage_of_goal_kicks_that_were_launched=None,
        average_goal_kick_length=None,
        crosses_faced=None,
        crosses_stopped=None,
        percentage_crosses_stopped=None,
        defensive_actions_outside_penalty_area=None,
        average_distance_of_defensive_actions=None,
        three_point_attempt_rate=None,
        batting_style=None,
        bowling_style=None,
        playing_roles=None,
        runs=None,
        balls=None,
        fours=None,
        sixes=None,
        strikerate=None,
        fall_of_wicket_order=None,
        fall_of_wicket_num=None,
        fall_of_wicket_runs=None,
        fall_of_wicket_balls=None,
        fall_of_wicket_overs=None,
        fall_of_wicket_over_number=None,
        ball_over_actual=None,
        ball_over_unique=None,
        ball_total_runs=None,
        ball_batsman_runs=None,
        overs=None,
        maidens=None,
        conceded=None,
        wickets=None,
        economy=None,
        runs_per_ball=None,
        dots=None,
        wides=None,
        no_balls=None,
        free_throw_attempt_rate=None,
        offensive_rebound_percentage=None,
        defensive_rebound_percentage=None,
        total_rebound_percentage=None,
        assist_percentage=None,
        steal_percentage=None,
        block_percentage=None,
        turnover_percentage=None,
        usage_percentage=None,
        offensive_rating=None,
        defensive_rating=None,
        box_plus_minus=None,
        ace_percentage=None,
        double_fault_percentage=None,
        first_serves_in=None,
        first_serve_percentage=None,
        second_serve_percentage=None,
        break_points_saved=None,
        return_points_won_percentage=None,
        winners=None,
        winners_fronthand=None,
        winners_backhand=None,
        unforced_errors=None,
        unforced_errors_fronthand=None,
        unforced_errors_backhand=None,
        serve_points=None,
        serves_won=None,
        serves_aces=None,
        serves_unreturned=None,
        serves_forced_error_percentage=None,
        serves_won_in_three_shots_or_less=None,
        serves_wide_percentage=None,
        serves_body_percentage=None,
        serves_t_percentage=None,
        serves_wide_deuce_percentage=None,
        serves_body_deuce_percentage=None,
        serves_t_deuce_percentage=None,
        serves_wide_ad_percentage=None,
        serves_body_ad_percentage=None,
        serves_t_ad_percentage=None,
        serves_net_percentage=None,
        serves_wide_direction_percentage=None,
        shots_deep_percentage=None,
        shots_deep_wide_percentage=None,
        shots_foot_errors_percentage=None,
        shots_unknown_percentage=None,
        points_won_percentage=None,
    )


@MEMORY.cache(ignore=["session"])
def _cached_create_espn_player_model(
    session: requests_cache.CachedSession,
    player: dict[str, Any],
    positions_validator: dict[str, str],
    dt: datetime.datetime,
    version: str,
) -> PlayerModel:
    return _create_espn_player_model(
        session=session,
        player=player,
        positions_validator=positions_validator,
        dt=dt,
        version=version,
    )


def create_espn_player_model(
    session: requests_cache.CachedSession,
    player: dict[str, Any],
    dt: datetime.datetime,
    positions_validator: dict[str, str],
) -> PlayerModel:
    """Create a player model based off ESPN."""
    if (
        not pytest_is_running.is_running()
        and dt.date() < datetime.datetime.today().date() - datetime.timedelta(days=7)
    ):
        return _cached_create_espn_player_model(
            session=session,
            player=player,
            positions_validator=positions_validator,
            dt=dt,
            version=VERSION,
        )
    with session.cache_disabled():
        return _create_espn_player_model(
            session=session,
            player=player,
            positions_validator=positions_validator,
            dt=dt,
            version=VERSION,
        )
