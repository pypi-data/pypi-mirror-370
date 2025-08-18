import abc
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ...core.config import AnilistConfig
from .params import (
    MediaAiringScheduleParams,
    MediaCharactersParams,
    MediaRecommendationParams,
    MediaRelationsParams,
    MediaReviewsParams,
    MediaSearchParams,
    UpdateUserMediaListEntryParams,
    UserMediaListSearchParams,
)
from .types import (
    AiringScheduleResult,
    CharacterSearchResult,
    MediaItem,
    MediaReview,
    MediaSearchResult,
    Notification,
    UserProfile,
)

if TYPE_CHECKING:
    from httpx import Client


class BaseApiClient(abc.ABC):
    """
    Abstract Base Class defining a generic contract for media database APIs.
    """

    def __init__(self, config: AnilistConfig | Any, client: "Client"):
        self.config = config
        self.http_client = client

    @abc.abstractmethod
    def authenticate(self, token: str) -> Optional[UserProfile]:
        pass

    @abc.abstractmethod
    def is_authenticated(self) -> bool:
        pass

    @abc.abstractmethod
    def get_viewer_profile(self) -> Optional[UserProfile]:
        pass

    @abc.abstractmethod
    def search_media(self, params: MediaSearchParams) -> Optional[MediaSearchResult]:
        """Searches for media based on a query and other filters."""
        pass

    @abc.abstractmethod
    def search_media_list(
        self, params: UserMediaListSearchParams
    ) -> Optional[MediaSearchResult]:
        pass

    @abc.abstractmethod
    def update_list_entry(self, params: UpdateUserMediaListEntryParams) -> bool:
        pass

    @abc.abstractmethod
    def delete_list_entry(self, media_id: int) -> bool:
        pass

    @abc.abstractmethod
    def get_recommendation_for(
        self, params: MediaRecommendationParams
    ) -> Optional[List[MediaItem]]:
        pass

    @abc.abstractmethod
    def get_characters_of(
        self, params: MediaCharactersParams
    ) -> Optional[CharacterSearchResult]:
        pass

    @abc.abstractmethod
    def get_related_anime_for(
        self, params: MediaRelationsParams
    ) -> Optional[List[MediaItem]]:
        pass

    @abc.abstractmethod
    def get_airing_schedule_for(
        self, params: MediaAiringScheduleParams
    ) -> Optional[AiringScheduleResult]:
        pass

    @abc.abstractmethod
    def get_reviews_for(
        self, params: MediaReviewsParams
    ) -> Optional[List[MediaReview]]:
        pass

    @abc.abstractmethod
    def get_notifications(self) -> Optional[List[Notification]]:
        """Fetches the user's unread notifications."""
        pass

    @abc.abstractmethod
    def transform_raw_search_data(self, raw_data: Dict) -> Optional[MediaSearchResult]:
        """
        Transform raw API response data into a MediaSearchResult.

        Args:
            raw_data: Raw response data from the API

        Returns:
            MediaSearchResult object or None if transformation fails
        """
        pass
