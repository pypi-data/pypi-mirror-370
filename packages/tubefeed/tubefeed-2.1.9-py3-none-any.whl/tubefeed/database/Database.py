import asyncio
from datetime import datetime
from pathlib import Path

import aiosqlite

from .Channel import Channel
from .Playlist import Playlist
from .Video import Video
from ..ytapi import Channel as YTChannel, Playlist as YTPlaylist


class Database:
    def __init__(self, path: Path):
        self._path: Path = path

    async def __aenter__(self) -> 'Database':
        self.con: aiosqlite.Connection = await aiosqlite.connect(self._path)
        await self.con.execute('PRAGMA foreign_keys = ON')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

        await self.con.__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        await self.con.commit()

    async def rollback(self):
        await self.con.rollback()

    async def create_tables(self):
        await self.con.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id          VARCHAR  PRIMARY KEY,
                title       VARCHAR  NOT NULL,
                description TEXT     NOT NULL,
                custom_url  VARCHAR  NOT NULL,
                uploads     VARCHAR  NOT NULL,
                updated     DATETIME NOT NULL,
                FOREIGN KEY (uploads) REFERENCES playlists(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
                    DEFERRABLE INITIALLY DEFERRED
            )
        ''')
        await self.con.execute('''
            CREATE TABLE IF NOT EXISTS handles (
                handle  VARCHAR PRIMARY KEY,
                channel VARCHAR NOT NULL,
                FOREIGN KEY (channel) REFERENCES channels(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''')
        await self.con.execute('''
            CREATE TABLE IF NOT EXISTS avatars (
                channel VARCHAR NOT NULL,
                name    VARCHAR NOT NULL,
                width   INTEGER NOT NULL,
                height  INTEGER NOT NULL,
                url     VARCHAR NOT NULL,
                PRIMARY KEY (channel, name),
                FOREIGN KEY (channel) REFERENCES channels(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''')
        await self.con.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id          VARCHAR PRIMARY KEY,
                parent      VARCHAR,
                child_name  VARCHAR,
                channel     VARCHAR NOT NULL,
                title       VARCHAR NOT NULL,
                description VARCHAR NOT NULL,
                published   DATETIME NOT NULL,
                UNIQUE (parent, child_name),
                FOREIGN KEY (parent) REFERENCES playlists(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
                FOREIGN KEY (channel) REFERENCES channels(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''')
        await self.con.execute('''
            CREATE TABLE IF NOT EXISTS playlist_thumbnails (
                playlist VARCHAR NOT NULL,
                name     VARCHAR NOT NULL,
                width    INTEGER NOT NULL,
                height   INTEGER NOT NULL,
                url      VARCHAR NOT NULL,
                PRIMARY KEY (playlist, name),
                FOREIGN KEY (playlist) REFERENCES playlists(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''')
        await self.con.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id          VARCHAR  PRIMARY KEY,
                title       VARCHAR  NOT NULL,
                description TEXT     NOT NULL,
                published   DATETIME NOT NULL,
                duration    INTEGER  NOT NULL
            )
        ''')
        await self.con.execute('''
            CREATE TABLE IF NOT EXISTS video_thumbnails (
                video   VARCHAR NOT NULL,
                name    VARCHAR NOT NULL,
                width   INTEGER NOT NULL,
                height  INTEGER NOT NULL,
                url     VARCHAR NOT NULL,
                PRIMARY KEY (video, name),
                FOREIGN KEY (video) REFERENCES videos(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''')
        await self.con.execute('''
            CREATE TABLE IF NOT EXISTS in_playlist(
                playlist VARCHAR NOT NULL,
                video    VARCHAR NOT NULL,
                sort_key INTEGER NOT NULL,
                PRIMARY KEY (playlist, video),
                FOREIGN KEY (playlist) REFERENCES playlists(id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (video) REFERENCES videos(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
        ''')

    async def get_channel_by_id(self, id: str) -> Channel | None:
        async for row in await self.con.execute('''
            SELECT *
            FROM channels
            WHERE id = ?
        ''', (id,)):
            return Channel(self, *row)

    async def get_channel_by_handle(self, handle: str) -> Channel | None:
        async for row in await self.con.execute('''
            SELECT channels.*
            FROM channels
            JOIN handles
                ON channels.id = handles.channel
            WHERE handles.handle = ?
        ''', (handle,)):
            return Channel(self, *row)

    async def add_channel(self, channel: YTChannel, uploads: YTPlaylist, updated: datetime) -> Channel:
        await self.con.execute('''
            INSERT INTO channels
                VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (id)
                DO UPDATE SET
                    title = ?,
                    description = ?,
                    custom_url = ?,
                    uploads = ?,
                    updated = ?
        ''', (
            channel.id, channel.title, channel.description, channel.custom_url, uploads.id, updated,
            channel.title, channel.description, channel.custom_url, uploads.id, updated
        ))
        await self.con.execute('''
            INSERT OR REPLACE INTO handles
                VALUES (?, ?)
        ''', (channel.custom_url, channel.id))
        await self.con.executemany('''
            INSERT OR REPLACE INTO avatars
                VALUES (?, ?, ?, ?, ?)
        ''', [
            (channel.id, t.name, t.width, t.height, t.url)
            for t in channel.thumbnails
        ])

        channel = await self.get_channel_by_handle(channel.custom_url)

        await channel.add_playlist(uploads)
        await asyncio.gather(*(
            channel.add_playlist(c, uploads, n)
            for n, c, in uploads.children.items()
        ))

        return channel

    async def get_playlist(self, id: str) -> Playlist | None:
        async for row in await self.con.execute('''
            SELECT *
            FROM playlists
            WHERE id = ?
        ''', (id,)):
            return Playlist(self, *row)

    async def get_video(self, id: str) -> Video | None:
        async for row in await self.con.execute('''
            SELECT *
            FROM videos
            WHERE id = ?
        ''', (id,)):
            return Video(self, *row)
