import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List, Optional, TypedDict

from ....core.config.model import MediaRegistryConfig
from ....core.exceptions import ViuError
from ....core.utils.file import AtomicWriter, FileLock, check_file_modified
from ....libs.media_api.params import MediaSearchParams
from ....libs.media_api.types import (
    MediaItem,
    MediaSearchResult,
    PageInfo,
    UserMediaListStatus,
)
from .models import (
    REGISTRY_VERSION,
    DownloadStatus,
    MediaRecord,
    MediaRegistryIndex,
    MediaRegistryIndexEntry,
)


class StatBreakdown(TypedDict):
    total_media_breakdown: Dict[int, int]
    status_breakdown: Dict[int, int]
    last_updated: str


logger = logging.getLogger(__name__)


class MediaRegistryService:
    def __init__(self, media_api: str, config: MediaRegistryConfig):
        self.config = config
        self.media_registry_dir = self.config.media_dir / media_api
        self._media_api = media_api
        self._ensure_directories()
        self._index = None
        self._index_file = self.config.index_dir / "registry.json"
        self._index_file_modified_time = 0
        _lock_file = self.config.media_dir / "registry.lock"
        self._lock = FileLock(_lock_file)

    def _ensure_directories(self) -> None:
        """Ensure registry directories exist."""
        try:
            self.media_registry_dir.mkdir(parents=True, exist_ok=True)
            self.config.index_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create registry directories: {e}")

    def _load_index(self) -> MediaRegistryIndex:
        """Load or create the registry index."""
        self._index_file_modified_time, is_modified = check_file_modified(
            self._index_file, self._index_file_modified_time
        )
        if not is_modified and self._index is not None:
            return self._index
        if self._index_file.exists():
            with self._index_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self._index = MediaRegistryIndex.model_validate(data)
        else:
            self._index = MediaRegistryIndex()
            self._save_index(self._index)

        # check if there was a major change in the registry
        if self._index.version[0] != REGISTRY_VERSION[0]:
            raise ViuError(
                f"Incompatible registry version of {self._index.version}. Current registry supports version {REGISTRY_VERSION}. Please migrate your registry using the migrator"
            )

        logger.debug(f"Loaded registry index with {self._index.media_count} entries")
        return self._index

    def _save_index(self, index: MediaRegistryIndex):
        """Save the registry index."""
        with self._lock:
            index.last_updated = datetime.now()
            with AtomicWriter(self._index_file) as f:
                json.dump(index.model_dump(mode="json"), f, indent=2)

            logger.debug("saved registry index")

    def get_seen_notifications(self) -> dict[int, str]:
        seen = {}
        for id, index_entry in self._load_index().media_index.items():
            if episode := index_entry.last_notified_episode:
                seen[index_entry.media_id] = episode
        return seen

    def get_media_index_entry(self, media_id: int) -> Optional[MediaRegistryIndexEntry]:
        index = self._load_index()
        return index.media_index.get(f"{self._media_api}_{media_id}")

    def _get_media_file_path(self, media_id: int) -> Path:
        """Get file path for media record."""
        return self.media_registry_dir / f"{media_id}.json"

    def get_media_record(self, media_id: int) -> Optional[MediaRecord]:
        record_file = self._get_media_file_path(media_id)
        if not record_file.exists():
            return None

        data = json.load(record_file.open(mode="r", encoding="utf-8"))

        record = MediaRecord.model_validate(data)

        # logger.debug(f"Loaded media record for {media_id}")
        return record

    def get_or_create_index_entry(self, media_id: int) -> MediaRegistryIndexEntry:
        index_entry = self.get_media_index_entry(media_id)
        if not index_entry:
            index = self._load_index()
            index_entry = MediaRegistryIndexEntry(
                media_id=media_id,
                media_api=self._media_api,  # pyright:ignore
            )
            index.media_index[f"{self._media_api}_{media_id}"] = index_entry
            self._save_index(index)
            return index_entry
        return index_entry

    def save_media_index_entry(self, index_entry: MediaRegistryIndexEntry) -> bool:
        index = self._load_index()
        index.media_index[f"{self._media_api}_{index_entry.media_id}"] = index_entry
        self._save_index(index)

        logger.debug(f"Saved media record for {index_entry.media_id}")
        return True

    def save_media_record(self, record: MediaRecord) -> bool:
        self.get_or_create_index_entry(record.media_item.id)
        with self._lock:
            media_id = record.media_item.id

            record_file = self._get_media_file_path(media_id)

            with AtomicWriter(record_file) as f:
                json.dump(record.model_dump(mode="json"), f, indent=2, default=str)

            logger.debug(f"Saved media record for {media_id}")
            return True

    def get_or_create_record(self, media_item: MediaItem) -> MediaRecord:
        record = self.get_media_record(media_item.id)
        if record is None:
            record = MediaRecord(media_item=media_item)
            self.save_media_record(record)
        else:
            record.media_item = media_item
            self.save_media_record(record)

        return record

    def update_media_index_entry(
        self,
        media_id: int,
        watched: bool = False,
        media_item: Optional[MediaItem] = None,
        progress: Optional[str] = None,
        status: Optional[UserMediaListStatus] = None,
        last_watch_position: Optional[str] = None,
        total_duration: Optional[str] = None,
        score: Optional[float] = None,
        repeat: Optional[int] = None,
        notes: Optional[str] = None,
        last_notified_episode: Optional[str] = None,
    ):
        if media_item:
            self.get_or_create_record(media_item)

        index = self._load_index()
        index_entry = index.media_index[f"{self._media_api}_{media_id}"]

        if progress:
            index_entry.progress = progress
        if status:
            index_entry.status = status
        if (
            progress
            and status == UserMediaListStatus.COMPLETED
            and media_item
            and media_item.episodes
        ):
            index_entry.progress = str(media_item.episodes)
        else:
            if not index_entry.status:
                index_entry.status = UserMediaListStatus.WATCHING
            elif index_entry.status == UserMediaListStatus.COMPLETED:
                index_entry.status = UserMediaListStatus.REPEATING

        if last_watch_position:
            index_entry.last_watch_position = last_watch_position
        if total_duration:
            index_entry.total_duration = total_duration
        if score:
            index_entry.score = score
        if repeat:
            index_entry.repeat = repeat
        if notes:
            index_entry.notes = notes
        if last_notified_episode:
            index_entry.last_notified_episode = last_notified_episode

        if watched:
            index_entry.last_watched = datetime.now()

        index.media_index[f"{self._media_api}_{media_id}"] = index_entry
        self._save_index(index)

    # TODO: standardize params passed to this
    def get_recently_watched(self, limit: Optional[int] = None) -> MediaSearchResult:
        """Get recently watched anime."""
        index = self._load_index()

        sorted_entries = sorted(
            index.media_index.values(), key=lambda x: x.last_watched, reverse=True
        )

        recent_media: List[MediaItem] = []
        for entry in sorted_entries:
            record = self.get_media_record(entry.media_id)
            if record:
                recent_media.append(record.media_item)
        page_info = PageInfo(
            total=len(sorted_entries),
        )
        return MediaSearchResult(page_info=page_info, media=recent_media)

    def search_for_media(self, params: MediaSearchParams) -> MediaSearchResult:
        """Search for media in the local registry based on search parameters."""
        from ....libs.media_api.types import MediaSearchResult, PageInfo

        index = self._load_index()
        all_media: List[MediaItem] = []

        # Get all media records and attach user status
        for entry in index.media_index.values():
            record = self.get_media_record(entry.media_id)
            if record:
                # Create UserListItem from index entry
                all_media.append(record.media_item)

        # Apply filters based on search parameters
        filtered_media = self._apply_search_filters(all_media, params, index)

        # Apply sorting
        sorted_media = self._apply_sorting(filtered_media, params, index)

        # Apply pagination
        page = params.page or 1
        per_page = params.per_page or 15
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        paginated_media = sorted_media[start_idx:end_idx]

        page_info = PageInfo(
            total=len(sorted_media),
            current_page=page,
            has_next_page=end_idx < len(sorted_media),
            per_page=per_page,
        )

        return MediaSearchResult(page_info=page_info, media=paginated_media)

    def _apply_search_filters(
        self, media_list: List[MediaItem], params: MediaSearchParams, index
    ) -> List[MediaItem]:
        """Apply search filters to media list."""
        filtered = media_list.copy()

        # Query filter (search in title)
        if params.query:
            query_lower = params.query.lower()
            filtered = [
                media
                for media in filtered
                if (
                    query_lower in media.title.english.lower()
                    if media.title.english
                    else False
                )
                or (
                    query_lower in media.title.romaji.lower()
                    if media.title.romaji
                    else False
                )
                or (
                    query_lower in media.title.native.lower()
                    if media.title.native
                    else False
                )
                or any(query_lower in synonym.lower() for synonym in media.synonymns)
            ]

        # Status filters
        if params.status:
            filtered = [media for media in filtered if media.status == params.status]
        if params.status_in:
            filtered = [media for media in filtered if media.status in params.status_in]
        if params.status_not_in:
            filtered = [
                media for media in filtered if media.status not in params.status_not_in
            ]

        # Genre filters
        if params.genre_in:
            filtered = [
                media
                for media in filtered
                if any(genre in media.genres for genre in params.genre_in)
            ]
        if params.genre_not_in:
            filtered = [
                media
                for media in filtered
                if not any(genre in media.genres for genre in params.genre_not_in)
            ]

        # Tag filters
        if params.tag_in:
            media_tags = [tag.name for media in filtered for tag in media.tags]
            filtered = [
                media
                for media in filtered
                if any(tag in media_tags for tag in params.tag_in)
            ]
        if params.tag_not_in:
            media_tags = [tag.name for media in filtered for tag in media.tags]
            filtered = [
                media
                for media in filtered
                if not any(tag in media_tags for tag in params.tag_not_in)
            ]

        # Format filter
        if params.format_in:
            filtered = [media for media in filtered if media.format in params.format_in]

        # Type filter
        if params.type:
            filtered = [media for media in filtered if media.type == params.type]

        # Score filters
        if params.averageScore_greater is not None:
            filtered = [
                media
                for media in filtered
                if media.average_score
                and media.average_score >= params.averageScore_greater
            ]
        if params.averageScore_lesser is not None:
            filtered = [
                media
                for media in filtered
                if media.average_score
                and media.average_score <= params.averageScore_lesser
            ]

        # Popularity filters
        if params.popularity_greater is not None:
            filtered = [
                media
                for media in filtered
                if media.popularity and media.popularity >= params.popularity_greater
            ]
        if params.popularity_lesser is not None:
            filtered = [
                media
                for media in filtered
                if media.popularity and media.popularity <= params.popularity_lesser
            ]

        # ID filter
        if params.id_in:
            filtered = [media for media in filtered if media.id in params.id_in]

        # User list filter
        if params.on_list is not None:
            if params.on_list:
                # Only show media that has user status (is on list)
                filtered = [
                    media for media in filtered if media.user_status is not None
                ]
            else:
                # Only show media that doesn't have user status (not on list)
                filtered = [media for media in filtered if media.user_status is None]

        return filtered

    def _apply_sorting(
        self, media_list: List[MediaItem], params: MediaSearchParams, index
    ) -> List[MediaItem]:
        """Apply sorting to media list."""
        if not params.sort:
            return media_list

        # Get the MediaSort value
        sort = params.sort
        if isinstance(sort, list):
            sort = sort[0]  # Use first sort if multiple provided

        # Apply sorting based on MediaSort enum
        try:
            if sort.value == "POPULARITY_DESC":
                return sorted(media_list, key=lambda x: x.popularity or 0, reverse=True)
            elif sort.value == "SCORE_DESC":
                return sorted(
                    media_list, key=lambda x: x.average_score or 0, reverse=True
                )
            elif sort.value == "FAVOURITES_DESC":
                return sorted(media_list, key=lambda x: x.favourites or 0, reverse=True)
            elif sort.value == "TRENDING_DESC":
                # For local registry, we'll sort by popularity as proxy for trending
                return sorted(media_list, key=lambda x: x.popularity or 0, reverse=True)
            elif sort.value == "UPDATED_AT_DESC":
                # Sort by last watched time from registry
                def get_last_watched(media):
                    entry = index.media_index.get(f"{self._media_api}_{media.id}")
                    return entry.last_watched if entry else datetime.min

                return sorted(media_list, key=get_last_watched, reverse=True)
            else:
                # Default to title sorting
                return sorted(
                    media_list, key=lambda x: x.title.english or x.title.romaji or ""
                )
        except Exception as e:
            logger.warning(f"Failed to apply sorting {sort}: {e}")
            return media_list

    def get_media_by_status(self, status: UserMediaListStatus) -> MediaSearchResult:
        """Get media filtered by user status from registry."""
        index = self._load_index()

        # Filter entries by status
        status_entries = [
            entry
            for entry in index.media_index.values()
            if entry.status.value == status.value
        ]

        # Get media items for these entries
        media_list: List[MediaItem] = []
        for entry in status_entries:
            record = self.get_media_record(entry.media_id)
            if record:
                # Create UserListItem from index entry
                media_list.append(record.media_item)

        # Sort by last watched
        sorted_media = sorted(
            media_list,
            key=lambda media_item: next(
                (
                    entry.last_watched
                    for entry in index.media_index.values()
                    if entry.media_id == media_item.id
                ),
                datetime.min,
            ),
            reverse=True,
        )

        page_info = PageInfo(total=len(sorted_media))
        return MediaSearchResult(page_info=page_info, media=sorted_media)

    def get_registry_stats(self) -> "StatBreakdown":
        """Get comprehensive registry statistics."""
        stats: "StatBreakdown" = {}  # type: ignore
        try:
            index = self._load_index()

            stats.update(
                StatBreakdown(
                    **{
                        "total_media_breakdown": index.media_count_breakdown,
                        "status_breakdown": index.status_breakdown,
                        "last_updated": index.last_updated.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                )
            )

        except Exception as e:
            logger.error(f"Failed to get registry stats: {e}")
        return stats

    def get_all_media_records(self) -> Generator[MediaRecord, None, List[MediaRecord]]:
        records = []
        for record_file in self.media_registry_dir.iterdir():
            try:
                if record_file.is_file():
                    id = record_file.stem
                    if record := self.get_media_record(int(id)):
                        records.append(record)
                        yield record
                else:
                    logger.warning(
                        f"{self.media_registry_dir} is impure; ignoring folder: {record_file}"
                    )
            except Exception as e:
                logger.warning(f"{self.media_registry_dir} is impure which caused: {e}")
        return records

    def remove_media_record(self, media_id: int):
        with self._lock:
            record_file = self._get_media_file_path(media_id)
            if record_file.exists():
                record_file.unlink()
                try:
                    record_file.parent.rmdir()
                except OSError:
                    pass

        index = self._load_index()
        id = f"{self._media_api}_{media_id}"
        if id in index.media_index:
            del index.media_index[id]
            self._save_index(index)

            logger.debug(f"Removed media record {media_id}")

    def update_episode_download_status(
        self,
        media_id: int,
        episode_number: str,
        status: "DownloadStatus",
        file_path: Optional[Path] = None,
        file_size: Optional[int] = None,
        quality: Optional[str] = None,
        provider_name: Optional[str] = None,
        server_name: Optional[str] = None,
        subtitle_paths: Optional[list[Path]] = None,
        error_message: Optional[str] = None,
        download_date: Optional[datetime] = None,
    ) -> bool:
        """Update the download status and metadata for a specific episode."""
        try:
            from .models import DownloadStatus, MediaEpisode

            record = self.get_media_record(media_id)
            if not record:
                logger.error(f"No media record found for ID {media_id}")
                return False

            # Find existing episode or create new one
            episode_record = None
            for episode in record.media_episodes:
                if episode.episode_number == episode_number:
                    episode_record = episode
                    break

            if not episode_record:
                # Allow creation without file_path for queued/in-progress states.
                # Only require file_path once the episode is marked COMPLETED.
                episode_record = MediaEpisode(
                    episode_number=episode_number,
                    download_status=status,
                    file_path=file_path,
                )
                record.media_episodes.append(episode_record)

            # Update episode metadata
            episode_record.download_status = status
            if file_path:
                episode_record.file_path = file_path
            elif status.name == "COMPLETED" and not episode_record.file_path:
                logger.warning(
                    "Completed status set without file_path for media %s episode %s",
                    media_id,
                    episode_number,
                )
            if file_size is not None:
                episode_record.file_size = file_size
            if quality:
                episode_record.quality = quality
            if provider_name:
                episode_record.provider_name = provider_name
            if server_name:
                episode_record.server_name = server_name
            if subtitle_paths:
                episode_record.subtitle_paths = subtitle_paths
            if error_message:
                episode_record.last_error = error_message

            # Increment download attempts if this is a failure
            if status == DownloadStatus.FAILED:
                episode_record.download_attempts += 1

            # Save the updated record
            return self.save_media_record(record)

        except Exception as e:
            logger.error(f"Failed to update episode download status: {e}")
            return False

    def get_episodes_by_download_status(
        self, status: "DownloadStatus"
    ) -> list[tuple[int, str]]:
        """Get all episodes with a specific download status."""
        try:
            episodes = []
            for record in self.get_all_media_records():
                for episode in record.media_episodes:
                    if episode.download_status == status:
                        episodes.append((record.media_item.id, episode.episode_number))
            return episodes

        except Exception as e:
            logger.error(f"Failed to get episodes by status: {e}")
            return []

    def get_download_statistics(self) -> dict:
        """Get comprehensive download statistics."""
        try:
            stats = {
                "total_episodes": 0,
                "downloaded": 0,
                "failed": 0,
                "queued": 0,
                "downloading": 0,
                "paused": 0,
                "total_size_bytes": 0,
                "by_quality": {},
                "by_provider": {},
            }

            for record in self.get_all_media_records():
                for episode in record.media_episodes:
                    stats["total_episodes"] += 1

                    # Count by status
                    status_key = episode.download_status.value.lower()
                    if status_key == "completed":
                        stats["downloaded"] += 1
                    elif status_key == "failed":
                        stats["failed"] += 1
                    elif status_key == "queued":
                        stats["queued"] += 1
                    elif status_key == "downloading":
                        stats["downloading"] += 1
                    elif status_key == "paused":
                        stats["paused"] += 1

                    # Aggregate file sizes
                    if episode.file_size:
                        stats["total_size_bytes"] += episode.file_size

                    # Count by quality
                    if episode.quality:
                        stats["by_quality"][episode.quality] = (
                            stats["by_quality"].get(episode.quality, 0) + 1
                        )

                    # Count by provider
                    if episode.provider_name:
                        stats["by_provider"][episode.provider_name] = (
                            stats["by_provider"].get(episode.provider_name, 0) + 1
                        )

            return stats

        except Exception as e:
            logger.error(f"Failed to get download statistics: {e}")
            return {}
