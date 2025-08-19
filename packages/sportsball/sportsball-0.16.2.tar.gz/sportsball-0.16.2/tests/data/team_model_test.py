"""Tests for the team model class."""
import unittest

from sportsball.data.team_model import TeamModel, VERSION


class TestTeamModel(unittest.TestCase):

    def setUp(self):
        self._team_model = TeamModel(
            identifier="A",
            name="B",
            location=None,
            players=[],
            odds=[],
            points=2.0,
            ladder_rank=10,
            kicks=None,
            news=[],
            social=[],
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
            version=VERSION,
        )

    def test_notnull(self):
        self.assertIsNotNone(self._team_model)
