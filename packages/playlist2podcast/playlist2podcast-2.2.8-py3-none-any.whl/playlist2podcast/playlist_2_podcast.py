"""Main / Overall logic for downloading videos of a Youtube playlist,
converting to MP3 and creating a podcast ATOM feed.

playlist2podcast - create podcast feed from a playlist URL
Copyright (C) 2021 - 2022  Mark S Burgunder

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import copy
import json
import re
import sys
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from typing import TypedDict

import msgspec
import requests
import typer
from feedgen.feed import FeedEntry
from feedgen.feed import FeedGenerator
from loguru import logger as log
from PIL import Image
from typing_extensions import Annotated
from typing_extensions import NotRequired
from whenever import PlainDateTime
from whenever import TimeDelta
from whenever import ZonedDateTime
from yt_dlp import YoutubeDL

from playlist2podcast import __display_name__
from playlist2podcast import __version__

log.catch()


class IgnoringLogger:
    """Logger class that ignores all logging silently."""

    def debug(self, msg: str) -> None:
        """Process debug log messages."""
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith("[debug] "):
            pass
        else:
            self.info(msg)

    def info(self, msg: str) -> None:
        """Process info log messages."""
        pass

    def warning(self, msg: str) -> None:
        """Process warning log messages."""
        pass

    def error(self, msg: str) -> None:
        """Process error log messages."""
        pass


YDL_DL_OPTS = {
    "quiet": "true",
    "ignoreerrors": "true",
    "logger": IgnoringLogger(),
    "format": "bestaudio/best",
    "outtmpl": "publish/media/%(id)s.%(ext)s",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "opus",
        }
    ],
}


class PlayList(msgspec.Struct):
    """Definition of a playlist."""

    url: str
    include: List[str] = msgspec.field(default_factory=list)
    exclude: List[str] = msgspec.field(default_factory=list)
    cookie_file: Optional[str] = None


class Config(msgspec.Struct):
    """Attributes that make up the Configuration."""

    version: str
    podcast_host: str
    publish_dir: str = "publish"
    media_dir: str = "media"
    number_of_episodes: int = 5
    log_level: str = "INFO"
    youtube_cookie_file: Optional[str] = None
    cookie_file: Optional[str] = None
    play_lists: list[PlayList] = msgspec.field(default_factory=list)


class VideoThumbnail(TypedDict):
    """Represents a single video thumbnail from yt_dlp info."""

    url: str


class VideoInfo(TypedDict):
    """Definition of dict holding info about a video."""

    id: str
    title: str
    original_url: str
    upload_date: NotRequired[str]
    release_date: NotRequired[str]
    uploader: str
    webpage_url: str
    description: str
    duration: NotRequired[int]
    entries: NotRequired[List["VideoInfo"]]
    thumbnails: List[VideoThumbnail]


class PlaylistInfo(TypedDict):
    """Playlist dict definition."""

    id: str
    entries: list[VideoInfo]


def start_main() -> None:
    """Start main processing."""
    typer.run(main)


def main(  # nocl
    config_file: Annotated[
        Path,
        typer.Option(
            "--config-file",
            "-c",
            help="Path of configuration file",
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ] = Path("config.toml"),
    logging_config: Annotated[
        Optional[Path],
        typer.Option(
            "--logging-config",
            "-l",
            help="Path of filename that defines logging",
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ] = None,
    publish_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--publish-dir",
            "-p",
            help="Directory to save feed.rss and media to. Overrides setting config file",
            file_okay=False,
            dir_okay=True,
            writable=True,
            resolve_path=True,
        ),
    ] = None,
) -> None:
    """Create Podcast feed from Youtube Playlist."""
    with config_file.open(mode="rb") as file:
        config = msgspec.toml.decode(file.read(), type=Config)
    setup_logging(logging_config)
    log.opt(colors=True).info(
        f"<cyan>Welcome to</cyan> <green><bold>{__display_name__}</bold></green> "
        f"<cyan>version</cyan> <yellow>{__version__}</yellow>"
    )

    if publish_dir:
        config.publish_dir = str(publish_dir)

    if not (Path(config.publish_dir) / Path(config.media_dir)).exists():
        (Path(config.publish_dir) / Path(config.media_dir)).mkdir(parents=True)

    if not config.cookie_file and config.youtube_cookie_file:
        config.cookie_file = config.youtube_cookie_file

    feed = create_feed(config)

    for current_play_list in config.play_lists:
        playlist_downloader = setup_downloader(config, current_play_list.cookie_file)
        log.opt(colors=True).info(
            f"<cyan>Downloading info for videos on playlist:</cyan> <bold><red>{current_play_list.url}</red></bold>"
        )
        download_info: PlaylistInfo = playlist_downloader.extract_info(url=current_play_list.url, download=False)
        log.debug(f"main() - download_info = {json.dumps(download_info, indent=4)}")
        videos_list = download_info["entries"]

        videos_to_download: list[VideoInfo] = determine_videos_to_download(current_play_list, videos_list)
        log.opt(colors=True).debug(f"<bold>Downloading first {config.number_of_episodes} videos.</bold>")
        for video in videos_to_download:
            log.debug(f"Downloading video with id={video['id']} titled {video['title']}")

        add_episodes(
            config=config,
            feed_cookies=current_play_list.cookie_file,
            feed=feed,
            videos_list=videos_to_download,
        )

    feed.rss_file(filename=f"{config.publish_dir}/feed.rss", extensions=True, pretty=True, xml_declaration=True)


def determine_videos_to_download(
    current_play_list: PlayList,
    videos_list: list[VideoInfo],
) -> List[VideoInfo]:
    """Determine list of videos to download."""
    videos_to_download: list[VideoInfo] = []
    check_videos: list[VideoInfo] = []
    for video in videos_list:
        if video and (entries := video.get("entries")):
            check_videos.extend(entries)
        elif video and video.get("original_url"):
            check_videos.append(video)

    if not check_videos:
        check_videos = videos_list

    for video in check_videos:
        if (
            video
            and ("original_url" in video)
            and is_video_included(
                video_title=video["title"],
                video_original_url=video["original_url"],
                include_filters=current_play_list.include,
                exclude_filters=current_play_list.exclude,
            )
        ):
            videos_to_download.append(video)
    return videos_to_download


def setup_downloader(
    config: Config,
    playlist_cookies: Optional[str] = None,
    playlist_items: Optional[str] = None,
) -> YoutubeDL:
    """Set up downloader."""
    download_options = copy.deepcopy(YDL_DL_OPTS)
    download_options["outtmpl"] = f"{config.publish_dir}/{config.media_dir}/%(id)s.%(ext)s"
    download_options["playlistend"] = config.number_of_episodes * 3
    if playlist_cookies:
        download_options["cookiefile"] = playlist_cookies
    elif config.cookie_file:
        download_options["cookiefile"] = config.cookie_file
    if playlist_items:
        download_options["playlist_items"] = playlist_items
    downloader = YoutubeDL(download_options)
    return downloader


def create_feed(config: Config) -> FeedGenerator:
    """Create feed."""
    feed = FeedGenerator()
    feed.load_extension("podcast")
    feed.author(name="Marvin", email="marvin@example.com")
    feed.link(href=f"{config.podcast_host}/feed.rss", rel="alternate")
    feed.title("Marvin's Youtube Playlist Podcast")
    feed.description("Marvin's Youtube Playlist Podcast")
    return feed


def setup_logging(logging_config_file: Optional[Path]) -> None:
    """Set up logging."""
    if logging_config_file and logging_config_file.is_file():
        with logging_config_file.open(mode="rb") as log_config_file:
            logging_config = msgspec.toml.decode(log_config_file.read())

        for handler in logging_config.get("handlers"):
            if handler.get("sink") == "sys.stdout":
                handler["sink"] = sys.stdout

        log.configure(**logging_config)


def _matches_any_filter(text: str, filters: List[str]) -> bool:
    """Check if text matches any of the provided regex filters."""
    if not text:
        return False
    for pattern in filters:
        if re.search(pattern, text):  # Use re.search for partial matches
            return True
    return False


def is_video_included(
    video_title: str,
    video_original_url: str,
    include_filters: List[str],
    exclude_filters: List[str],
) -> bool:
    """Check video title and URL against include and exclude filters to determine if
    video should be considered for adding to podcast or not.

    :param video_title: Title of video to check filters against.
    :param video_original_url: Original URL of video to check filters against.
    :param include_filters: List of regex patterns acting as include filters.
        If one include filter matches, video will be considered for adding.
    :param exclude_filters: List of regex patterns acting as exclude filters.
        If one exclude filter matches, video will be skipped, even if there is a
        matching include filter. I.e. exclude > include
    :return: True if video should be considered for adding and False if video should
        be skipped based on filters.
    """
    log.debug(f"Filtering: Checking video: {video_title} at {video_original_url}")

    if not video_title and not video_original_url:
        log.debug("Filtering: Video title and URL are empty. Skipping.")
        return False

    # Check for exclude filters first as they take precedence
    if exclude_filters:
        if _matches_any_filter(video_title, exclude_filters):
            log.debug(f"Filtering: Exclude filter matches video title '{video_title}'. Skipping.")
            return False
        if _matches_any_filter(video_original_url, exclude_filters):
            log.debug(f"Filtering: Exclude filter matches video URL '{video_original_url}'. Skipping.")
            return False

    # If no include filters are provided, all videos are included (after exclude check)
    if not include_filters:
        log.debug("Filtering: No include filters provided. Including video.")
        return True

    # Check for include filters
    should_include = _matches_any_filter(video_title, include_filters) or _matches_any_filter(
        video_original_url, include_filters
    )

    log.debug(f"Filtering: Video '{video_title}' included? {should_include}")
    return should_include


def _process_and_add_episode(
    config: Config,
    feed: FeedGenerator,
    video: VideoInfo,
    video_downloader,
) -> bool:
    """Process and add a single episode to the feed."""
    video_id = video["id"]
    local_audio_file = Path(config.publish_dir) / config.media_dir / f"{video_id}.opus"
    host_audio_file = f"{config.podcast_host}/{config.media_dir}/{video_id}.opus"
    thumbnail = get_thumbnail(config=config, video=video)

    feed_entry = create_feed_entry(
        video=video,
        thumbnail=thumbnail,
        host_audio_file=host_audio_file,
        config=config,
    )
    feed.add_entry(feedEntry=feed_entry)

    if not local_audio_file.is_file():
        log.opt(colors=True).info(_get_download_log_message(feed_entry=feed_entry))
        try:
            info_dirty = video_downloader.extract_info(url=video["webpage_url"])
            info = video_downloader.sanitize_info(info_dirty)
            log.debug(f"Downloader info={json.dumps(info, indent=4)}")
            move_download_if_needed(config=config, info=info, local_audio_file=local_audio_file)
        except Exception as e:
            log.error(f"Error downloading video {video_id}: {e}")
            return False  # Indicate failure to add episode

    log.debug(_get_episode_added_log(feed_entry=feed_entry))
    return True  # Indicate success


def _get_episode_added_log(feed_entry: FeedEntry) -> str:
    """Construct the log message for episodes added to feed."""
    return (
        f"Added episode with id {feed_entry.id()} "
        f"from {feed_entry.published():%Y-%m-%d} "
        f"with title {feed_entry.title()}"
    )


def _get_download_log_message(feed_entry: FeedEntry) -> str:
    """Construct the detailed download log message."""
    return (
        f"Downloading episode with id <green>{feed_entry.id()}</green> "
        f"and length <yellow>{TimeDelta(seconds=int(feed_entry.podcast.itunes_duration()))}</yellow> "
        f"uploaded on <yellow>{feed_entry.published():%Y-%m-%d}</yellow> with "
        f"title <green>{feed_entry.title()}</green>"
    )


def add_episodes(
    config: Config,
    feed: FeedGenerator,
    videos_list: List[VideoInfo],
    feed_cookies: Optional[str] = None,
) -> None:
    """Iterate through play list info and decides which videos to process and
    add to feed and then does so.

    :param config: Contains program configuration
    :param feed: RSS feed to add episodes to
    :param videos_list: List of info dicts for each video in the playlist
    :param feed_cookies: OPTIONAL string containing file name to cookies to use
    :return: None
    """
    video_downloader = setup_downloader(config=config, playlist_cookies=feed_cookies, playlist_items="1")
    ids_in_feed = {entry.id() for entry in feed.entry()}
    number_episodes_added = 0

    for video in videos_list:
        video_id = video["id"]
        log.debug(f"Processing video: {video_id}")

        if video_id in ids_in_feed:
            log.debug(f"Video {video_id} already in feed. Skipping.")
            continue

        if number_episodes_added >= config.number_of_episodes:
            log.debug(f"Reached episode limit ({config.number_of_episodes}). Removing unneeded files for {video_id}.")
            remove_unneeded_files(config, video)
            continue

        if _process_and_add_episode(config, feed, video, video_downloader):
            number_episodes_added += 1
            ids_in_feed.add(video_id)  # Add video_id directly as it's the unique identifier


def move_download_if_needed(config: Config, info: dict[str, Any], local_audio_file: Path) -> None:
    """Move downloaded file if needed."""
    if "entries" in info:
        downloaded_id = info["entries"][0]["id"]
        log.debug(f"{downloaded_id=}")
        downloaded_file = Path(config.publish_dir) / Path(config.media_dir) / Path(f"{downloaded_id}.opus")
        if downloaded_file.is_file():
            downloaded_file.rename(target=local_audio_file)
            log.debug(f"Renamed file from {downloaded_file}.opus to {local_audio_file}")


def create_feed_entry(
    video: VideoInfo,
    thumbnail: Path,
    host_audio_file: str,
    config: Config,
) -> FeedEntry:
    """Create feed entry to add to rss feed."""
    published_on = extract_date(video)
    duration = extract_duration(video)

    feed_entry = FeedEntry()
    feed_entry.load_extension("podcast")
    feed_entry.author(name=video["uploader"])
    feed_entry.id(id=video["id"])
    feed_entry.link(href=video["webpage_url"])
    feed_entry.title(title=video["title"])
    feed_entry.description(description=video["description"])
    feed_entry.published(published=published_on.py_datetime())
    feed_entry.podcast.itunes_image(f"{config.podcast_host}/{config.media_dir}/{thumbnail}")
    if duration:
        feed_entry.podcast.itunes_duration(duration)
    feed_entry.enclosure(url=host_audio_file, type="audio/ogg")

    return feed_entry


def extract_date(video: VideoInfo) -> ZonedDateTime:
    """Extract date from video dict with preference to upload_date over release_date and if no date has been given use
    1 January 1970.
    """
    if "upload_date" in video:
        published_on = PlainDateTime.parse_strptime(video["upload_date"], format="%Y%m%d").assume_tz("UTC")
    elif "release_date" in video:
        published_on = PlainDateTime.parse_strptime(video["release_date"], format="%Y%m%d").assume_tz("UTC")
    else:
        published_on = PlainDateTime.parse_strptime("19700101", format="%Y%m%d").assume_tz("UTC")
    return published_on


def extract_duration(video: VideoInfo) -> Optional[int]:
    """Extract duration in seconds from video. If no duration can be found in dict, return None."""
    duration: Optional[int] = None
    if "duration" in video:
        duration = video["duration"]
    elif "entries" in video:
        duration = video["entries"][0].get("duration")
    return duration


def remove_unneeded_files(config: Config, video: VideoInfo) -> None:
    """Remove files not needed for published feed."""
    try:
        (Path(config.publish_dir) / Path(config.media_dir) / Path(f"{video['id']}.*")).unlink()
        log.debug(
            f"Removed old files for episode with id {video['id']} "
            f"from {video['upload_date']} with title {video['title']}"
        )
    except FileNotFoundError:
        log.debug(f"Skipping episode with id {video['id']} from {video['upload_date']} with title {video['title']}")


def get_thumbnail(config: Config, video: VideoInfo) -> Path:
    """Get the highest quality thumbnail out of the video dict, converts it to
    JPG and returns the filename of the converted file.

    :param config: Configuration class instance
    :param video_id: YouTube video id
    :param video: youtube-dl information dict about one particular video

    :return:  Filename of the converted Thumbnail
    """
    video_id = video["id"]
    image_url = video["thumbnails"][-1]["url"]
    image_type = image_url.split(".")[-1]
    local_image = Path(config.publish_dir) / Path(f"{video_id}.{image_type}")
    publish_image = Path(f"{video_id}.jpg")
    publish_image_path = Path(config.publish_dir) / config.media_dir / publish_image
    if not publish_image_path.is_file():
        remote_image = requests.get(url=image_url, timeout=5)
        with local_image.open("wb") as file:
            file.write(remote_image.content)
        thumbnail_wip = Image.open(local_image)
        thumbnail_wip.save(publish_image_path)
        local_image.unlink()
    return publish_image
