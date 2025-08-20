from copy import copy
from datetime import datetime
from typing import AsyncIterable, Optional

from . import Channel
from . import YouTube
from .PlaylistItem import PlaylistItem
from .Thumbnail import Thumbnail


class Playlist:
    def __init__(self, yt: YouTube, item: dict):
        self._yt: YouTube = yt

        self.id: str = item['id']
        self.channel_id: str = item['snippet']['channelId']
        self.title: str = item['snippet']['title']
        self.description: str = item['snippet']['description']
        self.thumbnails: list[Thumbnail] = [Thumbnail(n, t) for n, t in item['snippet']['thumbnails'].items()]

        try:
            self.published: datetime = datetime.strptime(item['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            self.published: datetime = datetime.strptime(item['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def from_id(yt: YouTube, id: str) -> 'Playlist':
        return Playlist(yt, {
            'id': id,
            'snippet': {
                'channelId': None,
                'title': None,
                'description': None,
                'publishedAt': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                'thumbnails': {}
            }
        })

    def _clone_with_prefix(self, id_prefix: str, name_suffix: str) -> 'Playlist':
        assert self.id[:2] == 'UU'

        c = copy(self)
        c.id = f'{id_prefix}{c.id[2:]}'
        c.title = f'{c.title} - {name_suffix}'

        return c

    @property
    def children(self) -> dict[str, 'Playlist']:
        return {
            name.lower(): self._clone_with_prefix(prefix, name)
            for name, prefix in [
                ('Videos', 'UULF'),
                ('Livestreams', 'UULV'),
                ('Shorts', 'UUSH'),
            ]
        }

    async def channel(self) -> Optional[Channel]:
        for channel in await self._yt.find_channels(id=self.channel_id):
            return channel

    async def videos(self) -> AsyncIterable[list[PlaylistItem]]:
        next_page_token = None
        first_iteration = True

        while next_page_token is not None or first_iteration:
            result = await self._yt.get('playlistItems',
                                        part=('snippet', 'status'), playlistId=self.id,
                                        maxResults=50, pageToken=next_page_token)

            next_page_token = result['nextPageToken'] if 'nextPageToken' in result else None
            first_iteration = False

            yield [PlaylistItem(self._yt, item['snippet'])
                   for item in result['items']
                   if item['status']['privacyStatus'] == 'public']
