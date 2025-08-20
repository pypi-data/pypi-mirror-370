from . import YouTube
from .Playlist import Playlist
from .Thumbnail import Thumbnail


class Channel:
    def __init__(self, yt: YouTube, item: dict):
        self._yt: YouTube = yt

        self.id: str = item['id']
        self.title: str = item['snippet']['title']
        self.description: str = item['snippet']['description']
        self.custom_url: str = item['snippet']['customUrl']
        self.thumbnails: list[Thumbnail] = [Thumbnail(n, t) for n, t in item['snippet']['thumbnails'].items()]

    async def uploads(self) -> Playlist:
        result = await self._yt.get('channels', part='contentDetails', id=self.id)
        for item in result['items']:
            return await self._yt.get_playlist(item['contentDetails']['relatedPlaylists']['uploads'])
