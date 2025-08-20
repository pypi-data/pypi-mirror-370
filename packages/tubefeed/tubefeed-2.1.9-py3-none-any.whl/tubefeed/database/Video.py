from datetime import datetime

from . import Database
from .Thumbnail import Thumbnail


class Video:
    def __init__(self, db: Database, id: str, title: str, description: str, published: str, duration: int):
        self._db: Database = db

        self.id: str = id
        self.title: str = title
        self.description: str = description
        self.published: datetime = datetime.strptime(published, '%Y-%m-%d %H:%M:%S')
        self.duration: int = duration

    @property
    def url(self) -> str:
        return f'https://www.youtube.com/watch?v={self.id}'

    async def thumbnails(self) -> list[Thumbnail]:
        return [
            Thumbnail(*row)
            async for row in await self._db.con.execute('''
                SELECT name, width, height, url
                FROM video_thumbnails
                WHERE video = ?
            ''', (self.id,))
        ]
