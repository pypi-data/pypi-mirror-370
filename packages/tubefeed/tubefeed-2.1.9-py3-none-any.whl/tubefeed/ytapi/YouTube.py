import asyncio

from aiohttp import ClientSession

from .Channel import Channel
from .Error import Error
from .Playlist import Playlist
from .PlaylistItem import PlaylistItem
from .Video import Video


class YouTube:
    BASE_URL: str = 'https://www.googleapis.com/youtube/v3/'

    def __init__(self, api_key: str):
        self.api_key: str = api_key

    async def __aenter__(self):
        self._session: ClientSession = ClientSession(YouTube.BASE_URL)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.close()

    async def get(self, path, **args) -> dict:
        # prepare query and add api key
        args['key'] = self.api_key

        for key in list(args.keys()):
            if args[key] is None:
                del args[key]
            elif isinstance(args[key], tuple) or isinstance(args[key], list):
                args[key] = ','.join(args[key])

        # send request
        async with self._session.get(path, params=args) as response:
            result = await response.json()

        # check errors
        if 'error' in result:
            raise Error(result['error'])

        return result

    async def find_channels(self, id: str = None, handle: str = None) -> list[Channel]:
        result = await self.get('channels', part='snippet', id=id, forHandle=handle)

        if result['pageInfo']['totalResults'] == 0:
            return []
        else:
            return [Channel(self, item) for item in result['items']]

    async def get_playlist(self, id: str) -> Playlist | None:
        result = await self.get('playlists', part='snippet', id=id)
        for item in result['items']:
            return Playlist(self, item)

    async def _get_videos(self, ids: list[PlaylistItem | str]) -> list[Video]:
        id_list = [p.id if isinstance(p, PlaylistItem) else p for p in ids]

        result = await self.get('videos', part=('snippet', 'contentDetails', 'liveStreamingDetails'), id=id_list)
        videos = [Video(self, item) for item in result['items']]
        videos_dict = {v.id: v for v in videos}

        return [videos_dict.get(p, None) for p in id_list]

    async def get_videos(self, ids: list[PlaylistItem | str]) -> list[Video]:
        video_lists = await asyncio.gather(*(
            self._get_videos(ids[i:i + 50])
            for i in range(0, len(ids), 50)
        ))
        return [el for vl in video_lists for el in vl]

    async def get_video(self, id: PlaylistItem | str) -> Video | None:
        return (await self._get_videos([id]))[0]
