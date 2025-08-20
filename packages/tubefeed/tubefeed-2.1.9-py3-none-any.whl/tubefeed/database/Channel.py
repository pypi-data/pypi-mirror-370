from datetime import datetime

from . import Database
from .Playlist import Playlist
from .Thumbnail import Thumbnail
from ..ytapi import Playlist as YTPlaylist


class Channel:
    def __init__(self, db: Database,
                 id: str, title: str, description: str, custom_url: str, uploads: str, updated: str):
        self._db: Database = db

        self.id: str = id
        self.title: str = title
        self.description: str = description
        self.custom_url: str = custom_url
        self.uploads_id: str = uploads
        self.updated: datetime = datetime.strptime(updated, '%Y-%m-%d %H:%M:%S.%f')

    @property
    def url(self) -> str:
        return f'https://www.youtube.com/channel/{self.id}'

    async def avatars(self) -> list[Thumbnail]:
        return [
            Thumbnail(*row)
            async for row in await self._db.con.execute('''
                SELECT name, width, height, url
                FROM avatars
                WHERE channel = ?
            ''', (self.id,))
        ]

    async def uploads(self) -> Playlist | None:
        async for row in await self._db.con.execute('''
            SELECT playlists.*
            FROM playlists
            JOIN channels
                ON playlists.id = channels.uploads
            WHERE channels.id = ?
        ''', (self.id,)):
            return Playlist(self._db, *row)

    async def add_playlist(self, pl: YTPlaylist, parent_pl: YTPlaylist = None, child_name: str = None) -> 'Playlist':
        parent_id = parent_pl.id if parent_pl else None

        await self._db.con.execute('''
            INSERT INTO playlists
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (id)
                DO UPDATE SET
                    parent = COALESCE(parent, ?),
                    child_name = COALESCE(child_name, ?),
                    title = ?,
                    description = ?,
                    published = ?
        ''', (pl.id, parent_id, child_name, pl.channel_id, pl.title, pl.description, pl.published,
              parent_id, child_name, pl.title, pl.description, pl.published))
        await self._db.con.executemany('''
            INSERT INTO playlist_thumbnails
                VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (playlist, name)
                DO UPDATE SET width = ?, height = ?, url = ?
        ''', [
            (pl.id, t.name, t.width, t.height, t.url,
             t.width, t.height, t.url)
            for t in pl.thumbnails
        ])

        return await self._db.get_playlist(pl.id)
