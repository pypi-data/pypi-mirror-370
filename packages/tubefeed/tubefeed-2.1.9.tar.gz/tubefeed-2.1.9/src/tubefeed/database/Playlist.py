from datetime import datetime
from typing import AsyncIterator

from . import Channel
from . import Database
from .PlaylistUnion import PlaylistUnion
from .Thumbnail import Thumbnail
from .Video import Video
from ..ytapi import Video as YTVideo


class Playlist:
    def __init__(self,
                 db: Database,
                 id: str,
                 parent_id: str | None, child_name: str | None,
                 channel_id: str,
                 title: str, description: str, published: datetime):
        self._db: Database = db

        self.id: str = id
        self.parent_id: str | None = parent_id
        self.child_name: str | None = child_name
        self.channel_id: str = channel_id
        self.title: str = title
        self.description: str = description
        self.published: datetime = published

    @property
    def url(self) -> str:
        return f'https://www.youtube.com/playlist?list={self.id}'

    async def children(self) -> list['Playlist']:
        return [
            Playlist(self._db, *row)
            async for row in await self._db.con.execute('''
                SELECT *
                FROM playlists
                WHERE parent = ?
            ''', (self.id,))
        ]

    async def thumbnails(self) -> list[Thumbnail]:
        return [
            Thumbnail(*row)
            async for row in await self._db.con.execute('''
                SELECT name, width, height, url
                FROM playlist_thumbnails
                WHERE playlist = ?
            ''', (self.id,))
        ]

    async def channel(self) -> 'Channel':
        from . import Channel

        async for row in await self._db.con.execute('''
            SELECT channels.*
            FROM channels
            JOIN playlists
                ON channels.id = playlists.channel
            WHERE playlists.id = ?
        ''', (self.id,)):
            return Channel(self._db, *row)

    async def videos(self, limit: int | None) -> AsyncIterator[tuple[int, Video]]:
        async for row in await self._db.con.execute(f'''
            SELECT
                ROW_NUMBER() OVER (ORDER BY in_playlist.sort_key, videos.published) AS position,
                in_playlist.sort_key,
                videos.*
            FROM videos
            JOIN in_playlist
                ON videos.id = in_playlist.video
            WHERE in_playlist.playlist = ?
            ORDER BY sort_key DESC, videos.published DESC
            {f'LIMIT {limit}' if limit is not None else ''}
        ''', (self.id,)):
            yield row[0], row[1], Video(self._db, *row[2:])

    async def get_video(self, id: str) -> Video | None:
        async for row in await self._db.con.execute('''
            SELECT videos.*
            FROM videos
            JOIN in_playlist
                ON videos.id = in_playlist.video
            WHERE videos.id = ? AND in_playlist.playlist = ?
        ''', (id, self.id)):
            return Video(self._db, *row)

    async def add_video(self, video: YTVideo, sort_key: int) -> Video:
        await self._db.con.execute('''
            INSERT INTO videos
                VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (id)
                DO UPDATE SET title = ?, description = ?, published = ?, duration = ?
        ''', (video.id, video.title, video.description, video.published, video.duration,
              video.title, video.description, video.published, video.duration))
        await self._db.con.executemany('''
            INSERT INTO video_thumbnails
                VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (video, name)
                DO UPDATE SET width = ?, height = ?, url = ?
        ''', [
            (video.id, t.name, t.width, t.height, t.url,
             t.width, t.height, t.url)
            for t in video.thumbnails
        ])
        await self._db.con.execute('''
            INSERT OR REPLACE INTO in_playlist VALUES (?, ?, ?)
        ''', (self.id, video.id, sort_key))

        return await self._db.get_video(video.id)

    def __or__(self, other) -> PlaylistUnion:
        return PlaylistUnion(self._db, self, other)
