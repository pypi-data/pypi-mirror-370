from __future__ import annotations

from enum import Enum
from typing import Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from ...libs.media_api.params import MediaSearchParams, UserMediaListSearchParams
from ...libs.media_api.types import MediaItem, PageInfo
from ...libs.provider.anime.types import Anime, SearchResults, Server


class MenuName(Enum):
    MAIN = "MAIN"
    AUTH = "AUTH"
    EPISODES = "EPISODES"
    RESULTS = "RESULTS"
    SERVERS = "SERVERS"
    WATCH_HISTORY = "WATCH_HISTORY"
    PROVIDER_SEARCH = "PROVIDER_SEARCH"
    PLAYER_CONTROLS = "PLAYER_CONTROLS"
    USER_MEDIA_LIST = "USER_MEDIA_LIST"
    SESSION_MANAGEMENT = "SESSION_MANAGEMENT"
    MEDIA_ACTIONS = "MEDIA_ACTIONS"
    DOWNLOADS = "DOWNLOADS"
    DYNAMIC_SEARCH = "DYNAMIC_SEARCH"
    MEDIA_REVIEW = "MEDIA_REVIEW"
    MEDIA_CHARACTERS = "MEDIA_CHARACTERS"
    MEDIA_AIRING_SCHEDULE = "MEDIA_AIRING_SCHEDULE"
    PLAY_DOWNLOADS = "PLAY_DOWNLOADS"
    DOWNLOADS_PLAYER_CONTROLS = "DOWNLOADS_PLAYER_CONTROLS"
    DOWNLOAD_EPISODES = "DOWNLOAD_EPISODES"


class InternalDirective(Enum):
    MAIN = "MAIN"

    BACK = "BACK"

    BACKX2 = "BACKX2"

    BACKX3 = "BACKX3"

    BACKX4 = "BACKX4"

    EXIT = "EXIT"

    CONFIG_EDIT = "CONFIG_EDIT"

    RELOAD = "RELOAD"


class StateModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class MediaApiState(StateModel):
    search_result_: Optional[Dict[int, MediaItem]] = Field(
        default=None, alias="search_result"
    )
    search_params_: Optional[Union[MediaSearchParams, UserMediaListSearchParams]] = (
        Field(default=None, alias="search_params")
    )
    page_info_: Optional[PageInfo] = Field(default=None, alias="page_info")
    media_id_: Optional[int] = Field(default=None, alias="media_id")

    @property
    def search_result(self) -> dict[int, MediaItem]:
        if not self.search_result_:
            raise RuntimeError("Malformed state, please report")
        return self.search_result_

    @property
    def search_params(self) -> Union[MediaSearchParams, UserMediaListSearchParams]:
        if not self.search_params_:
            raise RuntimeError("Malformed state, please report")
        return self.search_params_

    @property
    def page_info(self) -> PageInfo | None:
        # if not self._page_info:
        #     raise RuntimeError("Malformed state, please report")
        return self.page_info_

    @property
    def media_id(self) -> int:
        if not self.media_id_:
            raise RuntimeError("Malformed state, please report")
        return self.media_id_

    @property
    def media_item(self) -> MediaItem:
        return self.search_result[self.media_id]


class ProviderState(StateModel):
    search_results_: Optional[SearchResults] = Field(
        default=None, alias="search_results"
    )
    anime_: Optional[Anime] = Field(default=None, alias="anime")
    episode_: Optional[str] = Field(default=None, alias="episode")
    servers_: Optional[Dict[str, Server]] = Field(default=None, alias="servers")
    server_name_: Optional[str] = Field(default=None, alias="server_name")
    start_time_: Optional[str] = Field(default=None, alias="start_time")

    @property
    def search_results(self) -> SearchResults:
        if not self.search_results_:
            raise RuntimeError("Malformed state, please report")
        return self.search_results_

    @property
    def anime(self) -> Anime:
        if not self.anime_:
            raise RuntimeError("Malformed state, please report")
        return self.anime_

    @property
    def episode(self) -> str | None:
        # if not self._episode:
        #     raise RuntimeError("Malformed state, please report")
        return self.episode_

    @property
    def servers(self) -> Dict[str, Server]:
        if not self.servers_:
            raise RuntimeError("Malformed state, please report")
        return self.servers_

    @property
    def server_name(self) -> str:
        if not self.server_name_:
            raise RuntimeError("Malformed state, please report")
        return self.server_name_

    @property
    def start_time(self) -> str | None:
        # if not self._start_time:
        #     raise RuntimeError("Malformed state, please report")
        return self.start_time_

    @property
    def server(self) -> Server:
        return self.servers[self.server_name]


class State(StateModel):
    menu_name: MenuName
    media_api: MediaApiState = Field(default_factory=MediaApiState)
    provider: ProviderState = Field(default_factory=ProviderState)
