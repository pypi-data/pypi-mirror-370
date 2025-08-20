# Tubefeed

First things first: I love [Audiobookshelf](https://github.com/advplyr/audiobookshelf). &#x2764;

I use Audiobookshelf every day in my car to listen to podcasts. However, I have subscribed to some podcasts that are
only available on YouTube. The goal of this project is to seamlessly integrate YouTube channels and playlists into
Audiobookshelf.

*Creating a feed for other podcast clients is not one of my goals and there will be **no** development in this
direction.*

## Highlights

- Designed for **seamless** integration with Audiobookshelf - nothing else.
- Video *information* is **cached**, so even large feeds are fast.
- Automatically add a configurable **delay** to give YouTube some time to finish encoding.
- **Chapter** information is added automatically (when using [`UNSAFE_DOWNLOAD_METHOD`](#unsafe_download_method-bool)).

## Quick Start

There is an example to start Tubefeed using [docker compose](doc/docker-compose.yml).

### YouTube API key

An API key is required to receive data from YouTube. The free quota of 10,000 should be more than enough for a single
user instance. If you do not already have an API key, please create one:

1. navigate to [Google Developers Console](https://console.developers.google.com/)
2. sign in if needed
3. read and accept the ToS if needed
4. create a new project
    - If you do not have any projects yet, there should be a button to do so in the overview.
    - If you already have a project, use the project selection menu in the header and click the `New Project` button in
      the modal dialogue.
5. choose a name and an organisation
6. after the project is created click `ENABLE APIS AND SERVICES`
7. find `YouTube Data API v3`
8. click `ENABLE`
9. click `CREATE CREDENTIALS`
10. select `Public Data` and click `Next`
11. copy your `API Key` and click `Done`

### Audiobookshelf

Audiobookshelf [prohibits access to local services](https://www.audiobookshelf.org/docs/#security) by default.
Explicitly allow Tubefeed by adding its domain to the whitelist using the environment variable
`SSRF_REQUEST_FILTER_WHITELIST`. Alternatively, set the environment variable `DISABLE_SSRF_REQUEST_FILTER` to `1` to
disable this protection method entirely.

### Tubefeed

Create a container using the image `troebs/tubefeed`. Make sure to set at least the required environment variables:

- `BASE_URL` to the url where Tubefeed is accessible from Audiobookshelf. It must contain the protocol and must not
  contain a trailing slash. When using Docker and the name `tubefeed` for the container, the address is usually
  `http://tubefeed`.
- `YT_API_KEY` to your YouTube API key received in the first step.

There are a couple of other [configuration options](#configuration) you should consider.

### Add Podcasts to Audiobookshelf

Open Audiobookshelf and add a new podcast. Use a URL like:

- `http://tubefeed/handle/@<handle>` (The channel handle can be found on the channel page. It starts with `@`. Channel
  feeds contain uploads and livestreams [by default](#channels). Please see [caveats](#caveats) if you receive a timeout
  for large channels.)
- `http://tubefeed/channel/@<id>`
- `http://tubefeed/playlist/<id>` (Click on `share` to get the link to the playlist. The identifier between `list=` and
  the next `&` is the ID of the playlist. It is usually 34 characters long.)

There are some [query parameters](#building-links) to adapt the feed to your needs.

## Table of Contents

- [Related Work](#related-work)
- [Building Links](#building-links)
- [Configuration](#configuration)
- [Caveats](#caveats)
- [Running via the CLI](#running-via-the-cli)
- [Future Work](#future-work)
- [Honorable Mentions](#honorable-mentions)

## Related Work

*This is not a rating, just a list of projects that implement a similar idea.*

[vod2pod-rss](https://github.com/madiele/vod2pod-rss) creates RSS feeds from YouTube and Twitch channels. However, it
seems to fetch the entire channel or playlist from the API every time you request the feed. There is also no option to
add chapter information automatically. Apparently there are also [some issues](https://redd.it/18q20f6) when used with
Audiobookshelf, which may require additional tinkering. *Bear in mind the discussion is one year old and I did not
review any changes since then.*

[podsync](https://github.com/mxpv/podsync) also provides RSS feeds created from YouTube, but requires configuration in a
separate configuration file. Again, there is no option to add chapter information.

[PodTube](https://github.com/amckee/PodTube) provides a similar approach. There is not much information available on how
it works in detail. However, there is some configuration regarding cleanup, so I assume it needs to pre-download the
audio files before serving them.

[ytdl-sub](https://github.com/jmbannon/ytdl-sub) automates downloading channels and playlists to a user definable folder
structure. [pinchflat](https://github.com/kieraneglin/pinchflat) follows a similar approach and can create RSS feeds. It
should be possible to integrate them with Audiobookshelf. However, I would like to use features such as downloading,
cleaning, adding channel and video descriptions **from within** Audiobookshelf.

[PODTUBE.ME](https://podtube.me/) is a hosted service that generates RSS feeds from YouTube. It is neither self-hosted
nor open source software.

## Building Links

Tubefeed supports channels and playlists separately.

### Channels

The path to add a channel is either `/handle/@<handle>` or `/channel/<id>`. The handle may be obtained from a channel's
page. (It starts with `@` and is neither the ID of the channel nor the title.)

A full URL to add to Audiobookshelf while using the default container name `tubefeed` from the provided
[docker compose example](doc/docker-compose.yml) looks like `http://tubefeed/handle/@<handle>`.

There are three types of videos that a channel can publish:

- `videos`: regular videos
- `livestreams`: recordings of livestreams
- `shorts`: YouTube Shorts (vertical videos, max. 180 seconds)

By default, regular videos and livestreams are included in the feed. To select a specific type, you can use the
`include` query parameter followed by a list of types separated by a plus sign:

- `http://tubefeed/handle/@<handle>?include=shorts` (shorts only)
- `http://tubefeed/handle/@<handle>?include=videos+shorts` (regular videos and shorts)
- `http://tubefeed/handle/@<handle>?include=videos+livestreams` (*default* if parameter is omitted)

### Playlists

The path to add a playlist is `/playlists/<id>`. The easiest way to get a playlist id is to click the `share` button on
a playlist page and extract the part between `list=` and the next `&`. It is usually 34 characters long.

A full URL to add to Audiobookshelf while using the default container name `tubefeed` from the provided
[docker compose example](doc/docker-compose.yml) looks like `http://tubefeed/playlist/<id>`.

The `limit` parameter, which can be used with channels, also works with playlists.

### Query Parameters

The following query parameters can be used with both channels and playlists.

#### `limit`

By default, all videos are included in the feed. For very large channels and playlists (I added one with about 9,000
videos), this will slow down Audiobookshelf as it has to parse and display this large feed. To display only a maximum
number of the most recent items, you can use the `limit` query parameter as shown below. (See
[`FEED_SIZE_LIMIT`](#feed_size_limit-int) for a global option.)

- `http://tubefeed/playlist/@<id>?limit=500`
  (display a maximum of 500 items)

#### `delay`

By default, videos are added to the feed as soon as they are added to the database, which is controllable by
[`RELEASE_DELAY_STATIC`](#release_delay_static-int) and
[`RELEASE_DELAY_STATIC_DURATION_FACTOR`](#release_delay_duration_factor-float). However, when using SponsorBlock for
example, it is sometimes helpful to add a greater delay. This parameter determines in seconds how much time must have
passed since the video was published before it is added to the feed.

#### `format`

By default, `bestaudio[ext=m4a]` is passed to yt-dlp as the value for `-f`, which should equal 128 kbps. The `format`
query parameter may be set as shown below to override the value. (See [`YT_DLP_FORMAT`](#yt_dlp_format-string) for a
global option and more detail.)

- `http://tubefeed/playlist/@<id>?format=139`
  (download 48 kbps)

#### `bitrate`

By default, no transcoding will be applied. If you want to re-encode the audio file using ffmpeg, set `bitrate` to the
desired bitrate. (See [`FFMPEG_BITRATE`](#ffmpeg_bitrate-string) for a global option and more detail.)

- `http://tubefeed/playlist/@<id>?bitrate=96k`
  (transcode to 96 kbps)

#### Combining Query Parameters

You can combine multiple query parameters using an `&` sign:

- `http://tubefeed/handle/@<handle>?include=shorts&limit=50&format=251&bitrate=96k`
  (50 most recent shorts, source: 128 kbps opus, target: 96 kbps aac / m4a)

## Configuration

The configuration is set via environment variables and is applied globally.

### `BASE_URL` (string, required)

Tubefeed generates some absolute URLs and therefore needs to know its own address. This is the address that
Audiobookshelf should call. It must contain the protocol and must not contain a trailing slash.

If hosted on the same docker network, this should be `http://<container name>`. When using the container name
`tubefeed` as shown in the [docker compose example](doc/docker-compose.yml), set this to `http://tubefeed`.

If hosted publicly (not recommended) behind a reverse proxy, it should be the address that the reverse proxy forwards,
such as `https://tubefeed.example.org`.

### `YT_API_KEY` (string, required)

Your personal API key. Get one as described in [Quick Start](#youtube-api-key).

### `RELEASE_DELAY_STATIC` (int)

default: `0`

A video is only included in the feed if it is older than `RELEASE_DELAY_STATIC` seconds.

If both `RELEASE_DELAY_STATIC` and `RELEASE_DELAY_DURATION_FACTOR` are specified, the video will be added once the
current time passes:

```
video.release + max(RELEASE_DELAY_STATIC, video.duration * RELEASE_DELAY_DURATION_FACTOR)
```

### `RELEASE_DELAY_DURATION_FACTOR` (float)

default: `0`

A video is only included in the feed if it is older than `video.duration * RELEASE_DELAY_DURATION_FACTOR`.

If both `RELEASE_DELAY_STATIC` and `RELEASE_DELAY_DURATION_FACTOR` are specified, the video will be added once the
current time passes:

```
video.release + max(RELEASE_DELAY_STATIC, video.duration * RELEASE_DELAY_DURATION_FACTOR)
```

### `FEED_SIZE_LIMIT` (int)

default: `None` (no limit)

Large channels and playlists (I added one with about 9,000 videos) slow down Audiobookshelf as it has to parse and
display large feeds. This can be set to limit the feed size to the `FEED_SIZE_LIMIT` most recent items globally.

This value will be overridden if [`limit`](#query-parameters) is added as a query parameter.

### `UNSAFE_DOWNLOAD_METHOD` (bool)

default: `false`

Tubefeed supports two download methods:

1. `false` (default): The old download method uses yt-dlp to receive a file url from YouTube and redirects
   Audiobookshelf to this url. This is a very simple approach and should work even with outdated versions of yt-dlp. The
   downside is that YouTube often limits the download speed to twice the bitrate of the file, which means that a
   one-hour video will take 30 minutes to download. This also means that we cannot change anything about the video file.
2. `true`: The new download version uses yt-dlp in conjunction with ffmpeg. This should make downloads much faster,
   rewrites metadata and allows chapter marks to be added to the file.

The second method obviously has some advantages, but it's not called unsafe for no reason. Before the audio file is
served, it must be fully downloaded to write the full header including duration and chapter information. Unfortunately,
Audiobookshelf closes the connection after 30 seconds of inactivity, so the download has to be completed within those 30
seconds. I managed to implement a dirty workaround to trick Audiobookshelf into waiting a little more than 17 minutes.

However, **if you are using the unsafe download method and the download takes more than 17 minutes to complete, the
download will fail.** If you can guarantee the download will never take more than 17 minutes, I would encourage you to
set `UNSAFE_DOWNLOAD_METHOD` to `true`. (With a [download limit](#max_download_rate-string) of one MByte per second, 17
minutes of download time equal slightly more than 17 hours of playback time with the default format.)

### `MAX_DOWNLOAD_RATE` (string)

default: `None` (no limit)

This value is passed to yt-dlp as the value for `-r`. For example, setting this to `2M` will limit the download speed to
two megabytes per second.

This only applies when used with `UNSAFE_DOWNLOAD_METHOD=true`.

### `YT_DLP_FORMAT` (string)

default: `bestaudio[ext=m4a]` (should equal `140` / 128 kbps)

This value is passed to yt-dlp as the value for `-f`.

If [`FFMPEG_BITRATE`](#ffmpeg_bitrate-string) is not set, m4a must be selected here. These are e.g. `140` for 128 kbps
or `139` for 48 kbps. If [`FFMPEG_BITRATE`](#ffmpeg_bitrate-string) is set, you can select any audio format that ffmpeg
can process as input.

This value will be overridden if [`format`](#query-parameters) is added as a query parameter.

### `FFMPEG_BITRATE` (string)

default: `None` (no transcoding)

If this option is set, the downloaded audio file is transcoded with the specified bitrate. For example, set this to
`96k` (please note the `k`!) to create an audio file with 96 kbps. (The audio format will always be set to aac in m4a).

This only applies when used with `UNSAFE_DOWNLOAD_METHOD=true`.

This value will be overridden if [`bitrate`](#query-parameters) is added as a query parameter.

### `SPONSORBLOCK` (bool)

default: `false`

If activated, [SponsorBlock](https://sponsor.ajay.app/) is queried for each download and received information is 
added as chapter information.

This only applies when used with `UNSAFE_DOWNLOAD_METHOD=true`.

## Caveats

**Fetching the feed for a channel / playlist with many videos exceeds the 12-second timeout.** Even if the request
fails, Tubefeed will continue to request the data from YouTube. Wait a minute and try again, then the request can be
served from the cache and you will not receive a timeout. (I have tested this with a channel with about 9,000 videos.)
You may additionally want to [limit](#query-parameters) the size of the feed to avoid poor performance with
Audiobookshelf's web interface.

**The download is very slow (about 30 kByte per second).** YouTube often limits the download speed to twice the bitrate
of the file. Use the unsafe download method to improve download speed.

**I cannot select an audio codec other than m4a or a bitrate other than 128k.** Tubefeed is built around m4a.
[There may be](#future-work) an option to select the bitrate in the future.

**Videos are not available immediately upon release.** Adding videos to the feed will be delayed by
[`RELEASE_DELAY_STATIC`](#release_delay_static-int) and
[`RELEASE_DELAY_DURATION_FACTOR`](#release_delay_duration_factor-float) to give YouTube some additional time to fully
process the video. For livestreams, this delay starts **after** the stream has finished.

**Videos do not appear in the same order as they do on YouTube.** Feed items are sorted by upload time (for livestreams,
the time the stream ended) with the delay added. (Imagine a channel releases a 30-minute video and then a 10-minute
video. If `RELEASE_DELAY_DURATION_FACTOR` equals 1 and the release timestamp is used to sort the feed items, the
10-minute video would appear first, Audiobookshelf would download it and skip the "older" (according to the feed)
30-minute video once it was added 20 minutes later.)

**I want to add a playlist ordered by oldest first.** Podcast-like formats typically use a sort order that shows the
most recent videos first. In fact, I would even call it best practice. If there is a real need for this type of
playlist, [support could be added](#future-work) in the future. However, this will lead to an increased number of
requests to the YouTube API.

## Running via the CLI

In case you do not want to use the docker image and want to run the service bare-metal:

```bash
# install package
pip3 install -U tubefeed

# run tubefeed
BASE_URL="<...>" YT_API_KEY="<...>" python3 -m tubefeed.app
```

Set [`BASE_URL`](#base_url-string-required) and [`YT_API_KEY`](#yt_api_key-string-required) as described above.

You can also set the environment variables `HOST`, `PORT` and `DATA_DIR` according to your needs.

Make sure `ffmpeg` is installed and in your `$PATH` when using the unsafe download method.

## Future Work

In no particular order:

- ~~environment variable to select the default bitrate~~ (added in 1.0.3)
- ~~query parameter to select the bitrate~~ (added in 1.0.3)
- add more documentation to the code
- support for playlists that are not ordered by newest first
- instructions to run from command line / without docker

## Honorable Mentions

This project depends on:

- [aiofiles](https://github.com/Tinche/aiofiles) - library to access files asynchronously
- [aiohttp](https://github.com/aio-libs/aiohttp) - library to send HTTP requests asynchronously
- [aiosqlite](https://github.com/omnilib/aiosqlite) - library to access sqlite databases asynchronously
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - versatile software / library to download from YouTube
- [ffmpeg](https://www.ffmpeg.org/) - software to convert audio streams (and much more)

Without the work the authors put into their code, Tubefeed would not be possible.
 