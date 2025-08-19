"""FIFA combined league model."""

# pylint: disable=line-too-long
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ...combined.combined_league_model import CombinedLeagueModel
from ...league import League
from ..oddsportal.fifa_oddsportal_league_model import FIFAOddsPortalLeagueModel
from ..sportsdb.fifa_sportsdb_league_model import FIFASportsDBLeagueModel
from ..sportsreference.fifa_sportsreference_league_model import \
    FIFASportsReferenceLeagueModel

FIFA_TEAM_IDENTITY_MAP: dict[str, str] = {}
FIFA_VENUE_IDENTITY_MAP: dict[str, str] = {}
FIFA_PLAYER_IDENTITY_MAP: dict[str, str] = {}


class FIFACombinedLeagueModel(CombinedLeagueModel):
    """FIFA combined implementation of the league model."""

    def __init__(self, session: ScrapeSession, league_filter: str | None) -> None:
        super().__init__(
            session,
            League.FIFA,
            [
                FIFASportsDBLeagueModel(session, position=0),
                FIFASportsReferenceLeagueModel(session, position=1),
                FIFAOddsPortalLeagueModel(session, position=2),
            ],
            league_filter,
        )

    @classmethod
    def team_identity_map(cls) -> dict[str, str]:
        return FIFA_TEAM_IDENTITY_MAP

    @classmethod
    def venue_identity_map(cls) -> dict[str, str]:
        return FIFA_VENUE_IDENTITY_MAP

    @classmethod
    def player_identity_map(cls) -> dict[str, str]:
        return FIFA_PLAYER_IDENTITY_MAP

    @classmethod
    def name(cls) -> str:
        return "fifa-combined-league-model"
