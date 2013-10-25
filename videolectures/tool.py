# -*- coding: utf-8 -*-
# ------
# License: MIT
# Copyright (c) 2013 Kohei Ozaki (eowenr atmark gmail dot com)

"""
CLI of videolectures-dl
"""
import argparse
import sys

from videolectures.util import VideoDownloader
from videolectures import __version__


def parse_args():
    """
    Parse arguments of videolectures-dl
    """
    desc = 'A command-line program to download videos from videolectures.net'

    p = argparse.ArgumentParser(
        description=desc,
        prog='videolectures-dl',
        conflict_handler='resolve')
    p.add_argument(
        '-h', '--help', action='help',
        help='print this help text and exit')
    p.add_argument(
        '-v', '--version', action='version',
        version=__version__,
        help='print program version and exit')
    p.add_argument(
        '-w', '--overwrite', action='store_true',
        help='overwrite an existent file')
    p.add_argument(
        '-t', '--title', action='store_true',
        help='use title as a filename')
    p.add_argument(
        '-o', '--output', type=str, default=None,
        help='video filename')
    p.add_argument('video_url', help='url of video page')

    args = p.parse_args()
    if not len(args.video_url) > len("videolectures.net"):
        p.print_help()
        sys.exit(1)

    return args


def main():
    arguments = parse_args()
    download = VideoDownloader(arguments)
    download.run(arguments.output, arguments.video_url)
    sys.exit(0)


if __name__ == '__main__':
    main()
