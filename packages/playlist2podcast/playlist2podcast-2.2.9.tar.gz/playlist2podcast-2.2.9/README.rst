Playlist2Podcast
================

|Repo| |Downloads| |Code style| |Checked with| |PyPI - Python Version| |PyPI - Wheel|
|CI - Woodpecker| |AGPL|


Playlist2Podcast is a command line tool that takes a Youtube playlist, downloads the audio portion of the videos on that
list, and creates a podcast feed from this.

Playlist2Podcast:

1) downloads and converts the videos in one or more playlists to opus audio only files,
2) downloads thumbnails and converts them to JPEG format, and
3) creates a podcast feed with the downloaded videos and thumbnails.

Install and run natively
------------------------

Easiest way to use Playlist2Podcast is to use `pipx` to install it from PyPi. Then you can simply use
`playlist2podcast` on the command line run it.
To configure playlist2podacast you can rename the `config.toml.example`_ file to `config.toml` and adjust values as
needed.

Below is an annotated version of the config.toml file explaining the various settings:

.. Todo: Explain config.toml.example file ...

.. code-block:: ini

   # version of playlist2podcasts this configuration file is built for.
   version = "2.0.0"
   # URL where the feed.rss file will be published. This value is used for references within the generated `feed.rss`
   # file. This value needs to be provided.
   podcast_host = "http://<...>"
   # directory on local file system to place all files for podcast in
   publish_dir = "publish"
   # directory on local file system where all media files are saved to, this is a sub directory inside the publish_dir
   media_dir = "media"
   # how many of the most recent episodes to download and save for each playlist
   number_of_episodes = 5
   # optional, file (with path if needed) on local filesystem where youtube cookie is stored for yt-dlp to use
   youtube_cookie_file = "youtube-dl-cookies.txt"

   # Each youtube playlist to be processed into your podcast is contained under a `[[play_lists]]` header. You can have
   # multiple `[[play_lists]]` sections

   [[play_lists]]
   # URL to list of media to look at and download audio files from to build your personalised podcast
   url = "https://www.youtube.com/@PythonBytes/streams"
   # Include filters allowing to only process some videos. Will allow all if empty.
   include = []
   # Exclude filters for videos NOT to download. If some video has been selected with an include filer but is also selected
   # with an exclude filter, that video will be excluded. In other words, exclude filters trump include filters.
   exclude = []

   [[play_lists]]
   # Second playlist to show an example of include and exclude filters. In this example, we exclude all videos that
   # contain "shorts" anywhere in the title or url. Additionally we only include videos where the title starts with
   # "The Level1 Show"
   url = "https://www.youtube.com/c/Level1Techs/videos"
   include = [
       "^The Level1 Show.*",
   ]
   exclude = [
       "shorts",
   ]


Docker
------

There is a container image published for playlist2podcast that can be used with docker of Podman.

Following is an example run command using podman (replace podman with docker to run with docker):

.. code-block:: bash

   podman run \
      --rm \
      --replace \
      --detach \
      --env TZ=UTC \
      --env UPDATE_INTERVAL=4h \
      --env LOGGING_CONFIG=/config/logging-config.toml \
      --name playlist2podcasts \
      --volume ./playlist2podcasts/config:/config \
      --volume ./playlist2podcasts/publish:/publish \
      --volume ./playlist2podcasts/logging:/logging \
      codeberg.org/pyyttools/playlist2podcasts:latest

Changelog
---------

See the `Changelog`_ for any changes introduced with each version.

License
-------

Playlist2Podcast is licences under the `GNU Affero General Public License v3.0`_

.. _GNU Affero General Public License v3.0: http://www.gnu.org/licenses/agpl-3.0.html

.. |AGPL| image:: https://www.gnu.org/graphics/agplv3-with-text-162x68.png
    :alt: AGLP 3 or later
    :target: https://codeberg.org/pyyttools/playlist2podcasts/src/branch/main/LICENSE.md

.. |Repo| image:: https://img.shields.io/badge/repo-Codeberg.org-blue
    :alt: Repo at Codeberg
    :target: https://codeberg.org/pyyttools/playlist2podcasts

.. |Downloads| image:: https://pepy.tech/badge/playlist2podcast
    :target: https://pepy.tech/project/playlist2podcast

.. |Code style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code Style: Black
    :target: https://github.com/psf/black

.. |Checked with| image:: https://img.shields.io/badge/pip--audit-Checked-green
    :alt: Checked with pip-audit
    :target: https://pypi.org/project/pip-audit/

.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/playlist2podcast

.. |PyPI - Wheel| image:: https://img.shields.io/pypi/wheel/playlist2podcast

.. |CI - Woodpecker| image:: https://ci.codeberg.org/api/badges/2911/status.svg
    :target: https://ci.codeberg.org/repos/2911

.. _Changelog: https://codeberg.org/pyyttools/playlist2podcasts/src/branch/main/CHANGELOG.rst

.. _config.toml.example: https://codeberg.org/pyyttools/playlist2podcasts/src/branch/main/config.toml.example
