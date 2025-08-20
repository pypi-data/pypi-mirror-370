from typing import AsyncIterator

from . import Database
from . import Playlist
from .Video import Video


class PlaylistUnion:
    def __init__(self, db: Database, *playlists: Playlist):
        self._db: Database = db
        self.playlists: tuple[Playlist, ...] = playlists

    def __or__(self, other: Playlist):
        return PlaylistUnion(self._db, *self.playlists, other)

    async def videos(self, limit: int | None) -> AsyncIterator[tuple[int, Video]]:
        async for row in await self._db.con.execute(f'''
            SELECT
                ROW_NUMBER() OVER (ORDER BY in_playlist.sort_key, videos.published) AS position,
                in_playlist.sort_key,
                videos.*
            FROM videos
            JOIN in_playlist
                ON videos.id = in_playlist.video
            WHERE in_playlist.playlist IN ({','.join('?' for _ in self.playlists)})
            ORDER BY sort_key DESC, videos.published DESC
            {f'LIMIT {limit}' if limit is not None else ''}
        ''', [p.id for p in self.playlists]):
            yield row[0], row[1], Video(self._db, *row[2:])
