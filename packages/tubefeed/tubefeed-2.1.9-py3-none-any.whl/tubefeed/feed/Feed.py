import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from functools import reduce

from ..database import Channel, Playlist, Video


# Audiobookshelf requires the descriptions of the podcasts with line breaks,
# while the descriptions of the episodes must be formatted with '<br>'.


class Feed(ET.Element):
    def __init__(self, base_url: str, item_limit: int | None, delay: int, remuxed: bool, **query_params: str):
        super().__init__('rss', version='2.0', **{
            'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        })

        self.base_url: str = base_url
        self.item_limit: int | None = item_limit
        self.datetime_threshold: datetime = datetime.now() - timedelta(seconds=delay)
        self.audio_suffix: str = '_remuxed' if remuxed else ''
        self.query_parameters = '&'.join(f'{k}={v}' for k, v in query_params.items() if v is not None)

    def __str__(self) -> str:
        return ET.tostring(self, encoding='utf-8').decode('utf-8')

    async def add_channel(self, channel: Channel, *playlists: Playlist):
        union = reduce(lambda a, v: a | v, playlists + playlists)
        videos = [(p, v) async for p, _, v in union.videos(self.item_limit)]

        el = ET.SubElement(self, 'channel')

        # general information
        ET.SubElement(el, 'title').text = channel.title
        ET.SubElement(el, 'description').text = channel.description
        ET.SubElement(el, 'link').text = channel.url
        ET.SubElement(el, 'copyright').text = channel.title

        ET.SubElement(el, 'itunes:summary').text = channel.description
        ET.SubElement(el, 'itunes:type').text = 'episodic'
        ET.SubElement(el, 'itunes:new-feed-url').text = f'{self.base_url}/channel/{channel.id}'
        ET.SubElement(el, 'itunes:author').text = channel.title

        # image
        thumbnail_url = f'{self.base_url}/channel/{channel.id}/avatar.jpg'

        avatars = await channel.avatars()
        if len(avatars) > 0:
            image_el = ET.SubElement(el, 'image')
            ET.SubElement(image_el, 'url').text = thumbnail_url
            ET.SubElement(image_el, 'title').text = channel.title
            ET.SubElement(image_el, 'link').text = channel.url

            ET.SubElement(el, 'itunes:image', href=thumbnail_url)

        # videos
        for position, video in videos:
            await self.add_video(el, position, video)

    async def add_playlist(self, playlist: Playlist):
        channel = await playlist.channel()
        videos = [(p, v) async for p, _, v in playlist.videos(self.item_limit)]

        el = ET.SubElement(self, 'channel')

        # general information
        ET.SubElement(el, 'title').text = playlist.title
        ET.SubElement(el, 'description').text = playlist.description
        ET.SubElement(el, 'link').text = playlist.url
        ET.SubElement(el, 'copyright').text = channel.title

        ET.SubElement(el, 'itunes:summary').text = playlist.description
        ET.SubElement(el, 'itunes:type').text = 'episodic'
        ET.SubElement(el, 'itunes:new-feed-url').text = f'{self.base_url}/playlist/{playlist.id}'
        ET.SubElement(el, 'itunes:author').text = channel.title

        # image
        # thumbnail_url = f'{self.base_url}/playlist/{playlist.id}/thumbnail.jpg'

        thumbnails = await playlist.thumbnails()
        if len(thumbnails) > 0:
            thumbnail_url = max(thumbnails, key=lambda a: a.width).url

            image_el = ET.SubElement(el, 'image')
            ET.SubElement(image_el, 'url').text = thumbnail_url
            ET.SubElement(image_el, 'title').text = playlist.title
            ET.SubElement(image_el, 'link').text = playlist.url

            ET.SubElement(el, 'itunes:image', href=thumbnail_url)

        # videos
        for position, video in videos:
            await self.add_video(el, position, video)

    async def add_video(self, channel_el, position: int, video: Video):
        # skip if video should be delayed further
        if video.published > self.datetime_threshold:
            return

        # create element
        el = ET.SubElement(channel_el, 'item')

        # general information
        ET.SubElement(el, 'title').text = video.title
        ET.SubElement(el, 'description').text = re.sub(r"\r?\n", "<br>", video.description)
        ET.SubElement(el, 'link').text = video.url
        ET.SubElement(el, 'pubDate').text = video.published.strftime('%a, %d %b %Y %H:%M:%S GMT')

        audio_url = f'{self.base_url}/video/{video.id}/audio{self.audio_suffix}.m4a?{self.query_parameters}'
        ET.SubElement(el, 'enclosure', url=audio_url)

        ET.SubElement(el, 'itunes:title').text = video.title
        ET.SubElement(el, 'itunes:summary').text = re.sub(r"\r?\n", "<br>", video.description)
        ET.SubElement(el, 'itunes:episodeType').text = 'full'
        ET.SubElement(el, 'itunes:episode').text = str(position)

        # see https://help.apple.com/itc/podcasts_connect/#/itcb54353390
        ET.SubElement(el, 'itunes:duration').text = str(video.duration)

        # image
        # ET.SubElement(el, 'itunes:image', href=f'{self.base_url}/video/{video.id}/thumbnail.jpg')
