from datetime import datetime

from . import YouTube
from .Thumbnail import Thumbnail


class PlaylistItem:
    def __init__(self, yt: YouTube, snippet: dict):
        self._yt: YouTube = yt

        self.id: str = snippet['resourceId']['videoId']
        self.title: str = snippet['title']
        self.description: str = snippet['description']
        self.published: datetime = self._parse_date(snippet['publishedAt'])
        self.thumbnails: list[Thumbnail] = [Thumbnail(n, t) for n, t in snippet['thumbnails'].items()]

    @staticmethod
    def _parse_date(val: str) -> datetime:
        return datetime.strptime(val, "%Y-%m-%dT%H:%M:%SZ")
