import asyncio
import subprocess
from pathlib import Path
from typing import Any

import yt_dlp


def _fetch_audio_url_sync(url: str, options: dict) -> dict:
    with yt_dlp.YoutubeDL({
        'quiet': True,
        'skip_download': True,
        **options
    }) as ydl:
        return ydl.extract_info(url, download=False)


async def _fetch_audio_url_async(url: str, **options) -> dict:
    return await asyncio.get_event_loop().run_in_executor(None, _fetch_audio_url_sync, url, options)


async def get_audio_url(video_url: str, ytdlp_format: str) -> str:
    response = await _fetch_audio_url_async(video_url, format=ytdlp_format)
    return response['url']


async def store_audio(yt_url: str,
                      yt_dlp_options: dict[str, Any],
                      ffmpeg_chapter_path: Path | None, ffmpeg_output_path: Path, ffmpeg_options: dict[str, Any]):
    # Use a normal subprocess for yt-dlp. The output is piped to ffmpeg
    # and therefore does not block the thread anyway.
    yt_dlp_command = [
        'yt-dlp',
        '-q',
        *(
            e
            for k, v in yt_dlp_options.items()
            if v is not None
            for e in (f'-{k}', str(v))
        ),
        '-o', '-',
        yt_url
    ]

    yt_dlp_process = subprocess.Popen(
        yt_dlp_command,
        stdout=subprocess.PIPE
    )

    # Use an async process for ffmpeg.
    ffmpeg_command = [
        'ffmpeg',
        '-v', 'warning',
        '-i', '-',
        *(('-i', str(ffmpeg_chapter_path.absolute())) if ffmpeg_chapter_path is not None else ()),
        '-map', '0:0',
        *(
            e
            for k, v in ffmpeg_options.items()
            if v is not None
            for e in (f'-{k}', str(v))
        ),
        *(('-map_chapters', '1') if ffmpeg_chapter_path is not None else ()),
        '-y',
        str(ffmpeg_output_path.absolute())
    ]

    ffmpeg_process = await asyncio.create_subprocess_exec(
        *ffmpeg_command,
        stdin=yt_dlp_process.stdout
    )

    # Wait for the download to finish.
    return_code = await ffmpeg_process.wait()

    # Handle errors in case the return code is not 0.
    if return_code:
        # TODO error handling
        print('return code not 0')
