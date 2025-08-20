import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile

import aiofiles
from aiohttp import web
from yt_dlp import DownloadError

from .. import APP_VERSION, DB_VERSION
from ..chapters import ChapterList
from ..database import Database, Channel, Playlist
from ..feed import Feed
from ..sbapi import SponsorBlock
from ..ytapi import YouTube, Error as YTError, Playlist as YTPlaylist
from ..ytdlp import get_audio_url, store_audio, m4a_header

###########################################################
# configuration                                           #
# mostly read from environment variables                  #
###########################################################
HOST = os.environ.get('HOST', '127.0.0.1')
PORT = int(os.environ.get('PORT', '8000'))

BASE_URL = os.environ['BASE_URL']
DATA_DIR = Path(os.environ.get('DATA_DIR', './data/'))
YT_API_KEY = os.environ['YT_API_KEY']

RDS = int(os.environ.get('RELEASE_DELAY_STATIC', '600'))
RDDF = float(os.environ.get('RELEASE_DELAY_DURATION_FACTOR', '0.0'))

FSL = os.environ.get('FEED_SIZE_LIMIT', None)
FSL = int(FSL) if FSL is not None else FSL

UNSAFE_DOWNLOAD_METHOD = os.environ.get('UNSAFE_DOWNLOAD_METHOD', '').lower() in ('true', 'yes', '1')
MAX_DOWNLOAD_RATE = os.environ.get('MAX_DOWNLOAD_RATE', None)
YT_DLP_FORMAT = os.environ.get('YT_DLP_FORMAT', 'bestaudio[ext=m4a]')
FFMPEG_BITRATE = os.environ.get('FFMPEG_BITRATE', None)

SPONSORBLOCK = os.environ.get('SPONSORBLOCK', '').lower() in ('true', 'yes', '1')

VERSION_PATH = DATA_DIR / 'version.txt'
DATABASE_PATH = DATA_DIR / 'cache.db'

###########################################################
# aiohttp configuration                                   #
# includes creating and initializing the cache database   #
###########################################################
routes = web.RouteTableDef()


async def app_startup(_: web.Application):
    # create data directory
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)

    # get database version from file
    if VERSION_PATH.exists():
        with open(VERSION_PATH, 'r') as f:
            current_version = f.read().strip()
    else:
        current_version = None

    # recreate database if outdated
    if current_version != DB_VERSION:
        logging.warning(f'database schema is outdated, recreating')

        DATABASE_PATH.unlink(missing_ok=True)
        with open(VERSION_PATH, 'w') as f:
            f.write(DB_VERSION)

    # create database tables
    async with Database(DATABASE_PATH) as db:
        await db.create_tables()


###########################################################
# API functions                                           #
###########################################################
@routes.get('/')
async def root(_: web.Request):
    """
    This function is just included for convenience. It returns a couple of
    notices on how to use the API. However, this is neither a real API
    description, nor does it contain all the usable parameters.
    """
    return web.json_response({
        'title': 'Tubefeed',
        'version': APP_VERSION,
        'refs': {
            '/channel/{id}': 'rss feed from channel id',
            '/handle/{handle}': 'rss feed from channel handle',
            '/playlist/{id}': 'rss feed from playlist id',
            '/video/{id}': 'url to m4a audio stream for video id',
        }
    })


@routes.get('/handle/{handle}')
async def get_channel_by_handle(request: web.Request):
    handle: str = request.match_info.get('handle')
    handle = handle.lower()

    # ensure channel is in database
    async with Database(DATABASE_PATH) as db:
        channel = await ensure_channel_handle_in_db(db, handle)

    # return response
    return await get_channel_by_id(request, channel.id)


@routes.get('/handle/{handle}/avatar.jpg')
async def get_channel_avatar_by_handle(request: web.Request):
    handle: str = request.match_info.get('handle')
    handle = handle.lower()

    # ensure channel is in database
    async with Database(DATABASE_PATH) as db:
        channel = await ensure_channel_handle_in_db(db, handle)

    # return response
    return await get_channel_avatar_by_id(request, channel.id)


@routes.get('/channel/{id}')
async def get_channel_by_id(request: web.Request, id: str = None):
    id: str = id or request.match_info.get('id')

    include: list[str] = request.query.get('include', 'videos livestreams').split(' ')
    limit: int | None = int(request.query.get('limit')) if 'limit' in request.query else None
    delay: int = int(request.query.get('delay')) if 'delay' in request.query else 0
    format: str | None = request.query.get('format', None)
    bitrate: str | None = request.query.get('bitrate', None)

    # ensure channel is in database and build feed
    async with Database(DATABASE_PATH) as db:
        # load channel from database
        channel = await ensure_channel_id_in_db(db, id)

        # run get_playlist to update playlist items
        uploads = await channel.uploads()
        children = [
            c
            for c in await uploads.children()
            if c.child_name in include
        ]

        await asyncio.gather(*(
            ensure_playlist_in_db(db, c)
            for c in children
        ))

        # build feed
        feed = Feed(BASE_URL, limit or FSL, delay, UNSAFE_DOWNLOAD_METHOD, format=format, bitrate=bitrate)
        await feed.add_channel(channel, *children)

    # return response
    return web.Response(text=str(feed), content_type='application/xml')


@routes.get('/channel/{id}/avatar.jpg')
async def get_channel_avatar_by_id(request: web.Request, id: str = None):
    id: str = id or request.match_info.get('id')

    # get channel and avatars from database
    async with Database(DATABASE_PATH) as db:
        channel = await ensure_channel_id_in_db(db, id)
        avatars = await channel.avatars()

    # return error if no avatar is found
    if len(avatars) == 0:
        raise web.HTTPNotFound(reason=f'no avatar found for channel {id=}')

    # select avatar with max size
    avatar_url = max(avatars, key=lambda a: a.width).url

    # send redirect to client
    return web.HTTPFound(location=avatar_url)


@routes.get('/playlist/{id}')
async def get_playlist(request: web.Request):
    id: str = request.match_info.get('id')

    limit: int | None = int(request.query.get('limit')) if 'limit' in request.query else None
    delay: int = int(request.query.get('delay')) if 'delay' in request.query else 0
    format: str | None = request.query.get('format', None)
    bitrate: str | None = request.query.get('bitrate', None)

    # ensure playlist is in database and build feed
    async with Database(DATABASE_PATH) as db:
        # get playlist from database
        playlist = await ensure_playlist_in_db(db, id)

        # build feed
        feed = Feed(BASE_URL, limit or FSL, delay, UNSAFE_DOWNLOAD_METHOD, format=format, bitrate=bitrate)
        await feed.add_playlist(playlist)

    # return response
    return web.Response(text=str(feed), content_type='application/xml')


@routes.get('/playlist/{id}/thumbnail.jpg')
async def get_playlist_thumbnail(request: web.Request):
    id: str = request.match_info.get('id')

    # get playlist and thumbnails from database
    async with Database(DATABASE_PATH) as db:
        playlist = await ensure_playlist_in_db(db, id)
        thumbnails = await playlist.thumbnails()

    # return error if no thumbnail is found
    if len(thumbnails) == 0:
        raise web.HTTPNotFound(reason=f'no thumbnail found for {id}')

    # select thumbnail with max size
    thumbnail_url = max(thumbnails, key=lambda a: a.width).url

    # send redirect to client
    return web.HTTPFound(location=thumbnail_url)


@routes.get('/video/{id}/thumbnail.jpg')
async def get_video_thumbnail(request: web.Request):
    id: str = request.match_info.get('id')

    # get video and thumbnails from database
    async with Database(DATABASE_PATH) as db:
        video = await db.get_video(id)
        if video is None:
            raise web.HTTPNotFound(reason=f'video {id} not found')

        thumbnails = await video.thumbnails()

    # return error if no thumbnail is found
    if len(thumbnails) == 0:
        raise web.HTTPNotFound(reason=f'no thumbnail found for {id}')

    # select thumbnail with max size
    thumbnail_url = max(thumbnails, key=lambda a: a.width).url

    # send redirect to client
    return web.HTTPFound(location=thumbnail_url)


@routes.get('/video/{id}/audio.m4a')
async def get_video_audio_m4a(request: web.Request):
    """
    The old download method uses yt-dlp to receive a file url from YouTube
    and redirects Audiobookshelf to this url. This is a very simple approach
    and should work even with outdated versions of yt-dlp. The downside is
    that YouTube often limits the download speed to twice the bitrate of the
    file, which means that a one-hour video will take 30 minutes to download.
    This also means that we cannot change anything about the video file.
    """
    id: str = request.match_info.get('id')

    format: str | None = request.query.get('format', YT_DLP_FORMAT)

    try:
        audio_url = await get_audio_url(f'https://www.youtube.com/watch?v={id}', format)
        return web.HTTPFound(location=audio_url)

    # error from yt-dlp
    except DownloadError as e:
        raise web.HTTPInternalServerError(reason=e.msg)


@routes.get('/video/{id}/audio_remuxed.m4a')
async def get_video_audio_m4a_remuxed(request: web.Request):
    """
    The new download version uses yt-dlp in conjunction with ffmpeg. This
    should make downloads much faster, rewrites metadata and allows chapter
    marks to be added to the file.
    """
    id: str = request.match_info.get('id')

    format: str | None = request.query.get('format', YT_DLP_FORMAT)
    bitrate: str | None = request.query.get('bitrate', FFMPEG_BITRATE)

    # receive video info from database
    async with Database(DATABASE_PATH) as db:
        video = await db.get_video(id)
        if video is None:
            raise web.HTTPNotFound(reason=f'video {id} not found')

    # extract chapters
    video_chapters = ChapterList.from_video(video.title, video.duration)
    description_chapters = ChapterList.from_description(video.description, video.duration)

    if SPONSORBLOCK:
        async with SponsorBlock() as sb:
            sb_chapters = await ChapterList.from_sponsorblock(await sb.skip_segments(video.id))
    else:
        sb_chapters = ChapterList([])

    all_chapters = video_chapters & description_chapters & sb_chapters

    # store chapters to temporary file if there are any
    if len(all_chapters) > 1:
        with NamedTemporaryFile(suffix='_chapters.metadata', mode='w', encoding='utf-8', delete=False) as metadata_file:
            metadata_file.write(';FFMETADATA1\n')

            for chapter in all_chapters:
                metadata_file.write('[CHAPTER]\n')
                metadata_file.write('TIMEBASE=1/1\n')
                metadata_file.write(f'START={chapter.start}\n')
                metadata_file.write(f'END={chapter.end}\n')
                metadata_file.write(f'title={chapter.title}\n')

            metadata_path = Path(metadata_file.name)
    else:
        metadata_path = None

    # create a temporary file to store the audio
    with NamedTemporaryFile(suffix='_audio.m4a', delete=False) as m4a_file:
        m4a_path = Path(m4a_file.name)

    # prepare response
    response = web.StreamResponse(headers={'Content-Type': 'audio/m4a'})
    await response.prepare(request)

    # start download function in background
    yt_dlp_options = {
        'f': format,
        'r': MAX_DOWNLOAD_RATE
    }

    if bitrate is None:
        ffmpeg_options = {
            'c': 'copy'
        }
    else:
        ffmpeg_options = {
            'c:a': 'aac',
            'b:a': bitrate
        }

    store_job = store_audio(video.url, yt_dlp_options, metadata_path, m4a_path, ffmpeg_options)
    store_task = asyncio.create_task(store_job)

    # wait up to 20 seconds before sending the first byte
    for _ in range(20):
        if not store_task.done():
            await asyncio.sleep(1)

    # Send a byte of the header every 28 seconds while the download is running.
    # This should prevent Audiobookshelf from closing the connection.
    for i in range(len(m4a_header)):
        await response.write(m4a_header[i:i + 1])

        if not store_task.done():
            for _ in range(28):
                if not store_task.done():
                    await asyncio.sleep(1)

    # finally read the file
    await store_task

    async with aiofiles.open(m4a_path, 'rb') as m4a_input:
        # skip header
        await m4a_input.read(len(m4a_header))

        # send data in chunks
        while chunk := await m4a_input.read(8192):
            await response.write(chunk)

    # remove temporary files
    for path in (metadata_path, m4a_path):
        if path is None:
            continue

        try:
            path.unlink()
        except FileNotFoundError:
            pass

    # finish response
    return response


###########################################################
# data transport functions                                #
# These ensure the required data is in the database.      #
###########################################################
async def ensure_channel_in_db(db: Database, now: datetime, id: str = None, handle: str = None) -> Channel:
    async with YouTube(YT_API_KEY) as yt:
        try:
            # search for id / handle
            for yt_c in await yt.find_channels(id=id, handle=handle):
                # get uploads playlist
                yt_u = await yt_c.uploads()

                # store in database
                channel = await db.add_channel(yt_c, yt_u, now)

                # break so no 404 is raised
                break

            # handle not found
            else:
                raise web.HTTPNotFound(reason=f'channel {id=} / {handle=} not found')

        # error from YouTube
        except YTError as e:
            error = web.HTTPException(reason=e.message)
            error.status_code = e.code

            raise error

    await db.commit()
    return channel


async def ensure_channel_handle_in_db(db: Database, handle: str) -> Channel:
    now = datetime.now()

    # get channel object from database
    channel = await db.get_channel_by_handle(handle)

    # fetch from YouTube if missing in database
    if channel is None or channel.updated < now - timedelta(days=7):
        channel = await ensure_channel_in_db(db, now, handle=handle)

    return channel


async def ensure_channel_id_in_db(db: Database, id: str) -> Channel:
    now = datetime.now()

    # get channel object from database
    channel = await db.get_channel_by_id(id)

    # fetch from YouTube if missing in database
    if channel is None or channel.updated < now - timedelta(days=7):
        channel = await ensure_channel_in_db(db, now, id=id)

    return channel


async def ensure_playlist_in_db(db: Database, playlist: str | Playlist) -> Playlist:
    now = datetime.now()

    async with YouTube(YT_API_KEY) as yt:
        # If the given playlist is a Playlist object from the database
        # package, we just need to create a yt_pl object to use later.
        if isinstance(playlist, Playlist):
            yt_pl = YTPlaylist.from_id(yt, playlist.id)

        # If the given playlist is a string / id, we need to get the
        # object from the database or create it with data from YouTube
        # before updating the videos.
        else:
            id = playlist

            # get playlist object from database
            playlist = await db.get_playlist(id)

            if playlist is not None:
                yt_pl = YTPlaylist.from_id(yt, id)

            # fetch playlist from YouTube if missing in database
            else:
                try:
                    # fetch playlist
                    yt_pl = await yt.get_playlist(id)
                    if yt_pl is None:
                        raise web.HTTPNotFound(reason=f'playlist {id} not found')

                    # check if channel is not already in database
                    channel = await db.get_channel_by_id(yt_pl.channel_id)

                    if channel is None or channel.updated < now - timedelta(days=7):
                        # fetch channel and store in database
                        yt_ch = await yt_pl.channel()
                        yt_ch_u = await yt_ch.uploads()

                        channel = await db.add_channel(yt_ch, yt_ch_u, now)

                    # store playlist in database
                    playlist = await channel.add_playlist(yt_pl)

                # error from YouTube
                except YTError as e:
                    error = web.HTTPException(reason=e.message)
                    error.status_code = e.code

                    raise error

        # We request the playlist items from YouTube and store the missing
        # ones in the database.
        try:
            async for yt_videos in yt_pl.videos():
                # fetch video objects from database
                db_videos = await asyncio.gather(*(playlist.get_video(v.id) for v in yt_videos))

                # find missing videos
                yt_v_missing = [yt_v for db_v, yt_v in zip(db_videos, yt_videos) if db_v is None]

                # receive details for missing videos
                yt_v_details = await yt.get_videos(yt_v_missing)

                # store in database
                yt_v_insert = ((v, int(v.published.timestamp()) + max(RDDF * v.duration, RDS)) for v in yt_v_details)

                await asyncio.gather(*(
                    playlist.add_video(v, sk)
                    for v, sk in yt_v_insert
                    if not v.is_live and sk <= now.timestamp()
                ))

                # break if oldest fetched video is already in db
                if db_videos[-1] is not None:
                    break

        except YTError as e:
            # Under some circumstances we do not want to raise an error here.
            # If a channel did not upload a single short for example, the
            # playlist does not exist. This is expected behaviour though.
            if not playlist.child_name or e.code != 404:
                raise e

    await db.commit()
    return playlist


###########################################################
# start script                                            #
###########################################################
def main():
    app = web.Application()
    app.on_startup.append(app_startup)
    app.add_routes(routes)

    web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
