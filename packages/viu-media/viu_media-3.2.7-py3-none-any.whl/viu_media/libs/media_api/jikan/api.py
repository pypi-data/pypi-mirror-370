import logging
from typing import TYPE_CHECKING, List, Optional

from ..base import BaseApiClient
from ..params import (
    MediaAiringScheduleParams,
    MediaCharactersParams,
    MediaRecommendationParams,
    MediaRelationsParams,
    MediaSearchParams,
    UpdateUserMediaListEntryParams,
    UserMediaListSearchParams,
)
from ..types import (
    AiringScheduleResult,
    CharacterSearchResult,
    MediaImage,
    MediaItem,
    MediaSearchResult,
    MediaTitle,
    Notification,
    UserProfile,
)
from . import mapper

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

JIKAN_ENDPOINT = "https://api.jikan.moe/v4"


class JikanApi(BaseApiClient):
    """
    Jikan API (MyAnimeList) implementation of the BaseApiClient contract.
    Note: Jikan is a read-only API for public data. All authentication and
    list modification methods will be no-ops.
    """

    def _execute_request(
        self, endpoint: str, params: Optional[dict] = None
    ) -> Optional[dict]:
        """Executes a GET request to a Jikan endpoint."""
        try:
            response = self.http_client.get(
                f"{JIKAN_ENDPOINT}{endpoint}", params=params, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Jikan API request failed for endpoint '{endpoint}': {e}")
            return None

    # --- Read-Only Method Implementations ---

    def search_media(self, params: MediaSearchParams) -> Optional[MediaSearchResult]:
        """Searches for anime on MyAnimeList via Jikan."""
        jikan_params = {
            "q": params.query,
            "page": params.page,
            "limit": params.per_page,
        }
        raw_data = self._execute_request("/anime", params=jikan_params)
        return mapper.to_generic_search_result(raw_data) if raw_data else None

    def fetch_trending_media(
        self, page: int, per_page: int
    ) -> Optional[MediaSearchResult]:
        """Jikan doesn't have a 'trending' sort, so we'll use 'bypopularity'."""
        jikan_params = {"order_by": "popularity", "page": page, "limit": per_page}
        raw_data = self._execute_request("/anime", params=jikan_params)
        return mapper.to_generic_search_result(raw_data) if raw_data else None

    def fetch_popular_media(
        self, page: int, per_page: int
    ) -> Optional[MediaSearchResult]:
        """Alias for trending in Jikan's case."""
        return self.fetch_trending_media(page, per_page)

    def fetch_favourite_media(
        self, page: int, per_page: int
    ) -> Optional[MediaSearchResult]:
        """Fetches the most favorited media."""
        jikan_params = {"order_by": "favorites", "page": page, "limit": per_page}
        raw_data = self._execute_request("/anime", params=jikan_params)
        return mapper.to_generic_search_result(raw_data) if raw_data else None

    # --- No-Op Methods (Jikan is Read-Only) ---

    def is_authenticated(self) -> bool:
        """Jikan is a public API that doesn't require authentication."""
        return False

    def authenticate(self, token: str) -> Optional[UserProfile]:
        logger.warning("Jikan API does not support authentication.")
        return None

    def get_viewer_profile(self) -> Optional[UserProfile]:
        logger.warning("Jikan API does not support user profiles.")
        return None

    def search_media_list(
        self, params: UserMediaListSearchParams
    ) -> Optional[MediaSearchResult]:
        logger.warning("Jikan API does not support fetching user lists.")
        return None

    def update_list_entry(self, params: UpdateUserMediaListEntryParams) -> bool:
        logger.warning("Jikan API does not support updating list entries.")
        return False

    def delete_list_entry(self, media_id: int) -> bool:
        logger.warning("Jikan API does not support deleting list entries.")
        return False

    def get_recommendation_for(
        self, params: MediaRecommendationParams
    ) -> Optional[List[MediaItem]]:
        """Fetches anime recommendations for a given media ID."""
        try:
            endpoint = f"/anime/{params.id}/recommendations"
            raw_data = self._execute_request(endpoint)
            if not raw_data or "data" not in raw_data:
                return None

            recommendations = []
            for item in raw_data["data"]:
                # Jikan recommendation structure has an 'entry' field with anime data
                entry = item.get("entry", {})
                if entry:
                    media_item = mapper._to_generic_media_item(entry)
                    recommendations.append(media_item)

            return recommendations
        except Exception as e:
            logger.error(f"Failed to fetch recommendations for media {params.id}: {e}")
            return None

    def get_characters_of(
        self, params: MediaCharactersParams
    ) -> Optional[CharacterSearchResult]:
        """Fetches characters for a given anime."""
        logger.warning(
            "Jikan API does not support fetching character data in the standardized format."
        )
        return None

    def get_related_anime_for(
        self, params: MediaRelationsParams
    ) -> Optional[List[MediaItem]]:
        """Fetches related anime for a given media ID."""
        try:
            endpoint = f"/anime/{params.id}/relations"
            raw_data = self._execute_request(endpoint)
            if not raw_data or "data" not in raw_data:
                return None

            related_anime = []
            for relation in raw_data["data"]:
                entries = relation.get("entry", [])
                for entry in entries:
                    if entry.get("type") == "anime":
                        # Create a minimal MediaItem from the relation data
                        media_item = MediaItem(
                            id=entry["mal_id"],
                            id_mal=entry["mal_id"],
                            title=MediaTitle(
                                english=entry["name"], romaji=entry["name"], native=None
                            ),
                            cover_image=MediaImage(large=""),
                            description=None,
                            genres=[],
                            studios=[],
                            streaming_episodes={},
                            user_status=None,
                        )
                        related_anime.append(media_item)

            return related_anime
        except Exception as e:
            logger.error(f"Failed to fetch related anime for media {params.id}: {e}")
            return None

    def get_notifications(self) -> Optional[List[Notification]]:
        """Jikan is a public API and does not support user notifications."""
        logger.warning("Jikan API does not support fetching user notifications.")
        return None

    def get_airing_schedule_for(
        self, params: MediaAiringScheduleParams
    ) -> Optional[AiringScheduleResult]:
        """Jikan doesn't provide a direct airing schedule endpoint per anime."""
        logger.warning(
            "Jikan API does not support fetching airing schedules for individual anime."
        )
        return None
