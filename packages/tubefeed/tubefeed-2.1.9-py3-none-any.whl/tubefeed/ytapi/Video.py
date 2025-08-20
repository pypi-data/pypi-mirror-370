import re

from . import YouTube
from .PlaylistItem import PlaylistItem


class Video(PlaylistItem):
    i = 0

    def __init__(self, yt: YouTube, item: dict):
        item['snippet']['resourceId'] = {'videoId': item['id']}
        super().__init__(yt, item['snippet'])

        # duration
        match = re.match(r'^P((\d+)D)?(T((\d+)H)?((\d+)M)?((\d+)S)?)?$', item['contentDetails']['duration'])
        days, hours, minutes, seconds = (int(m) if m else 0 for m in (match.group(i) for i in (2, 5, 7, 9)))

        self.duration: int = ((days * 24 + hours) * 60 + minutes) * 60 + seconds

        # livestreams
        self.is_live: bool = 'liveStreamingDetails' in item and not 'actualEndTime' in item['liveStreamingDetails']
