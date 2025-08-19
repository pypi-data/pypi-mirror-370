"""Module for mapping Gazelle API responses to domain models and vice versa."""

import html
import re
from typing import Dict, Any, List

from red_plex.domain.models import Collection, TorrentGroup
from red_plex.infrastructure.logger.logger import logger


class GazelleMapper:
    """Maps Gazelle API responses to domain models"""

    @staticmethod
    def map_collage(response: Dict[str, Any]) -> Collection:
        """Convert raw API response to Collage domain object"""
        collage_data = response.get('response', {})
        collage_id = collage_data.get('id')
        return Collection(
            external_id=str(collage_id),
            name=GazelleMapper._clean_text(collage_data.get('name', f'Collage {collage_id}')),
            torrent_groups=[
                TorrentGroup(id=tg_id)
                for tg_id in collage_data.get('torrentGroupIDList', [])
            ]
        )

    @staticmethod
    def map_bookmarks(response: Dict[str, Any], site: str) -> Collection:
        """Convert raw API response to Collage domain object"""
        bookmarks_data = response.get('response', {})
        return Collection(
            name=f"{site.upper()} Bookmarks",
            torrent_groups=GazelleMapper._get_torrent_groups_from_bookmarks(bookmarks_data)
        )

    @staticmethod
    def map_torrent_group(data: Dict[str, Any], torrents: List[Dict] = None) -> TorrentGroup:
        """Map individual torrent group data."""
        torrents = torrents or []

        group_data = data.get('group') or {}
        music_info = data.get('musicInfo') or group_data.get('musicInfo') or {}

        person_roles = [
            'artists', 'composers', 'conductor',
            'dj', 'producer', 'arranger', 'remixedBy'
                                          'with'
        ]

        return TorrentGroup(
            id=data.get('id')
               or data.get('groupId')
               or group_data.get('id')
               or group_data.get('groupId'),

            album_name=GazelleMapper._clean_text(
                data.get('name')
                or data.get('groupName')
                or group_data.get('name')
                or group_data.get('groupName')
                or ''
            ),

            artists=[
                        GazelleMapper._clean_text(person.get('name', ''))
                        for role in person_roles
                        for person in music_info.get(role, [])
                    ] or ([data.get('artist')] if data.get('artist') else []),

            file_paths=GazelleMapper._map_torrent_group_file_paths(torrents),

            tags=data.get('tags') or group_data.get('tags') or []
        )

    @staticmethod
    def _map_torrent_group_file_paths(torrents: List[Dict]) -> List[str]:
        """Extracts file paths from a torrent group."""
        logger.debug('Extracting file paths from torrent group response.')
        try:
            file_paths = [torrent.get('filePath') for torrent in torrents if 'filePath' in torrent]
            normalized_file_paths = [GazelleMapper._clean_text(path) for path in file_paths if path]
            return normalized_file_paths
        except Exception as e:  # pylint: disable=W0718
            logger.exception('Error extracting file paths from torrent group: %s', e)
            return []

    @staticmethod
    def _get_torrent_groups_from_bookmarks(response: Dict[str, Any]) -> List[TorrentGroup]:
        """Extracts file paths from user bookmarks."""
        logger.debug('Extracting file paths from bookmarks response.')
        try:
            # Bookmarks are at the group level
            bookmarked_group_ids = [bookmark.get('id')
                                    for bookmark in response.get('bookmarks', [])]
            logger.debug('Bookmarked group IDs: %s', bookmarked_group_ids)
            return [TorrentGroup(id=group_id, file_paths=[]) for group_id in bookmarked_group_ids]
        except Exception as e:  # pylint: disable=W0718
            logger.exception('Error extracting group ids from bookmarks: %s', e)
            return []

    @staticmethod
    def _clean_text(text: str) -> str:
        """Sanitize text from API response"""
        unescaped = html.unescape(text)
        return re.sub(r'[\u200e\u200f\u202a-\u202e]', '', unescaped)
