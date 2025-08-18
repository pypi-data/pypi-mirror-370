"""ESPN league model."""

# pylint: disable=too-many-locals,too-many-arguments
from typing import Any, Iterator

import tqdm
from scrapesession.scrapesession import ScrapeSession  # type: ignore

from ..game_model import GameModel
from ..league import League
from ..league_model import SHUTDOWN_FLAG, LeagueModel
from ..season_type import SeasonType
from .espn_game_model import create_espn_game_model


def _season_type_from_name(name: str) -> SeasonType:
    if name == "Regular Season":
        return SeasonType.REGULAR
    if name == "Preseason":
        return SeasonType.PRESEASON
    if name == "Postseason":
        return SeasonType.POSTSEASON
    if name == "Off Season":
        return SeasonType.OFFSEASON
    raise ValueError(f"Unrecognised season name: {name}")


class ESPNLeagueModel(LeagueModel):
    """ESPN implementation of the league model."""

    def __init__(
        self,
        start_url: str,
        league: League,
        session: ScrapeSession,
        position: int | None = None,
    ) -> None:
        super().__init__(league, session, position=position)
        self._start_url = start_url

    @classmethod
    def name(cls) -> str:
        return "espn-league-model"

    @classmethod
    def position_validator(cls) -> dict[str, str]:
        """A dictionary that contains the mapping from positions to standard positions."""
        raise NotImplementedError(
            "position_validator is not implemented by parent class"
        )

    def _produce_games(
        self,
        week: dict[str, Any],
        week_count: int,
        season_type_json: dict[str, Any],
        pbar: tqdm.tqdm,
        cache_disabled: bool,
    ) -> Iterator[GameModel]:
        def produce_game(
            event_item: dict[str, Any],
            game_number: int,
        ) -> GameModel:
            if cache_disabled:
                with self.session.cache_disabled():
                    event_response = self.session.get(event_item["$ref"])
            else:
                event_response = self.session.get(event_item["$ref"])
            event_response.raise_for_status()
            event = event_response.json()
            game_model = create_espn_game_model(
                event,
                week_count,
                game_number,
                self.session,
                self.league,
                season_type_json["year"],
                _season_type_from_name(season_type_json["name"]),
                self.position_validator(),
            )
            pbar.update(1)
            pbar.set_description(
                f"ESPN {game_model.year} - {game_model.season_type} - {game_model.dt}"
            )
            return game_model

        events_page = 1
        events_count = 0
        while True:
            if "events" not in week:
                break
            events_response = self.session.get(
                week["events"]["$ref"] + f"&page={events_page}"
            )
            events_response.raise_for_status()
            events = events_response.json()
            for event_item in events["items"]:
                yield produce_game(event_item, events_count)
                events_count += 1
            if events_page >= events["pageCount"]:
                break
            events_page += 1
        qbr_page = 1
        qbr_count = 0
        while True:
            if "qbr" not in week:
                break
            qbr_response = self.session.get(week["qbr"]["$ref"] + f"&page={qbr_page}")
            qbr = qbr_response.json()
            for qbr_item in qbr["items"]:
                yield produce_game(qbr_item["event"], qbr_count)
                qbr_count += 1
            if qbr_page >= qbr["pageCount"]:
                break
            qbr_page += 1

    def _produce_week_games(
        self,
        season_type_json: dict[str, Any],
        page: int,
        pbar: tqdm.tqdm,
        cache_disabled: bool,
    ) -> Iterator[GameModel]:
        if "weeks" not in season_type_json:
            return
        game_page = 1
        week_count = 0
        while True:
            if cache_disabled:
                with self.session.cache_disabled():
                    weeks_response = self.session.get(
                        season_type_json["weeks"]["$ref"] + f"&page={page}"
                    )
            else:
                weeks_response = self.session.get(
                    season_type_json["weeks"]["$ref"] + f"&page={page}"
                )
            weeks_response.raise_for_status()
            weeks = weeks_response.json()
            for item in weeks["items"]:
                if SHUTDOWN_FLAG.is_set():
                    return
                if cache_disabled:
                    with self.session.cache_disabled():
                        week_response = self.session.get(item["$ref"])
                else:
                    week_response = self.session.get(item["$ref"])
                week_response.raise_for_status()
                week = week_response.json()
                yield from self._produce_games(
                    week, week_count, season_type_json, pbar, cache_disabled
                )
                week_count += 1
            if game_page >= weeks["pageCount"]:
                break
            game_page += 1

    @property
    def games(self) -> Iterator[GameModel]:
        try:
            with self.session.wayback_disabled():
                page = 1
                first = True
                with tqdm.tqdm(position=self.position) as pbar:
                    while True:
                        if page == 1:
                            with self.session.cache_disabled():
                                response = self.session.get(
                                    self._start_url + f"&page={page}"
                                )
                        else:
                            response = self.session.get(
                                self._start_url + f"&page={page}"
                            )
                        response.raise_for_status()
                        seasons = response.json()
                        for item in seasons.get("items", []):
                            season_response = self.session.get(item["$ref"])
                            season_response.raise_for_status()
                            season_json = season_response.json()

                            for season_item in season_json["types"]["items"]:
                                season_type_response = self.session.get(
                                    season_item["$ref"]
                                )
                                season_type_response.raise_for_status()
                                season_type_json = season_type_response.json()

                                yield from self._produce_week_games(
                                    season_type_json, page, pbar, first
                                )
                            first = False

                        if page >= seasons.get("pageCount", 0):
                            break
                        page += 1
        except Exception as exc:
            SHUTDOWN_FLAG.set()
            raise exc
