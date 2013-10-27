# -*- coding: utf-8 -*-
# ------
# License: MIT
# Copyright (c) 2013 Kohei Ozaki (eowenr atmark gmail dot com)

"""
Utils for videolectures-dl
"""
import re
import sys
import os
import subprocess
import time

import requests


def _regex_match_get(pattern, text, position=1):
    """
    Return matched pattern or None
    """
    match = re.search(pattern, text)
    if match is not None:
        return match.group(position)
    else:
        return None


def _convert_display_size(size):
    """
    Convert filesize into human-readable size using unit suffixes
    """
    unit_gigabyte = 1024 * 1024 * 1024.0
    unit_megabyte = 1024 * 1024.0
    unit_kilobyte = 1024.0

    if size > unit_gigabyte:
        return "{:.2f} GB".format(
            size / unit_gigabyte)
    elif size > unit_megabyte:
        return "{:.2f} MB".format(
            size / unit_megabyte)
    elif size > unit_kilobyte:
        return "{:.1f} KB".format(
            size / unit_kilobyte)

    return "{0} bytes".format(size)


class ExtractionError(Exception):
    """
    Exception for Extractor
    """
    pass


class DownloadError(Exception):
    """
    Exception for Downloader
    """
    pass


class VideoDownloader(object):
    """
    Download videos from videolectures.net
    """
    _CLEAR_STDOUT = '\r                                '

    def __init__(self, opts):
        self.info_extract = VideoInfoExtractor()
        self.opts = opts

    def _to_stderr(self, message):
        """
        Print a message to stderr
        """
        sys.stderr.write(message)

    def _to_stdout(self, message, skip_eol=False):
        """
        Print a message to stdout
        """
        sys.stdout.write(("{0}{1}".format(message, ["\n", ""][skip_eol])))
        sys.stdout.flush()

    def show_video_detail(self, filename, metadata):
        """
        Show video detail
        """
        print("File name: {0}".format(filename))
        print("Title: {0}".format(metadata['meta_title']))
        print("Date: {0}".format(metadata['meta_date']))
        print("Type: {0}".format(metadata['meta_type']))
        print("Part: {0}".format(metadata['meta_part']))

    def error(self, err, message=None):
        """
        Raise error with a given message
        """
        if message is not None:
            self._to_stderr(message)
        raise err(message)

    def run(self, filename, url):
        """
        Run VideoDownloader
        """
        extractor = self.info_extract

        video_info = extractor.get_info(url)
        if not video_info:
            self.error(ExtractionError,
                       'ERROR: no video infomation was extracted.')

        meta_url = video_info['streaming_meta_path']
        meta_data = extractor.get_streaming_meta(meta_url)

        # Set filename
        if filename is None:
            if self.opts.title is False:
                name = video_info['default_filename']
            else:
                name = meta_data['meta_title']

            filename = "{0}.{1}".format(
                name,
                meta_data['ext'])

        # Show video details
        self.show_video_detail(filename, meta_data)

        # Dump video
        if self.dump_video(filename, meta_data):
            print("download complete")

    def dump_video(self, filename, meta_data):
        """
        Dump a video from videolectures.net
        """
        if os.path.exists(filename):
            if self.opts.overwrite is True and self.opts.resume is False:
                os.remove(filename)
            elif self.opts.overwrite is False and self.opts.resume is False:
                self.error(DownloadError,
                           ("ERROR: file already exists. " +
                            "remove it or use `overwrite`"))

        try:
            stdout = open(os.path.devnull, 'w')
            subprocess.call(
                ['rtmpdump', '-h'],
                stdout=stdout,
                stderr=subprocess.STDOUT)
        except (OSError, IOError):
            print('ERROR: rtmpdump could not be run. check the binary path.')
            sys.exit(1)
        finally:
            stdout.close()

        basic_args = [
            'rtmpdump', '-q', '-r', meta_data['streamer'],
            '-y', meta_data['source'],
            '-a', 'vod', '-o', filename,
        ]
        if self.opts.resume is True:
            basic_args.append('-e')

        retval = subprocess.Popen(basic_args)

        while True:
            if retval.poll() is not None:
                break
            if not os.path.exists(filename):
                continue

            previous_size = os.path.getsize(filename)
            display_size = _convert_display_size(previous_size)
            self._to_stdout(self._CLEAR_STDOUT, skip_eol=True)
            self._to_stdout('\r[rtmpdump] {0}'.format(
                display_size),
                skip_eol=True)
            time.sleep(2.0)

        if retval.wait() == 0:
            current_size = os.path.getsize(filename)
            display_size = _convert_display_size(current_size)
            self._to_stdout(self._CLEAR_STDOUT, skip_eol=True)
            self._to_stdout('\r[rtmpdump] {0}'.format(
                display_size))
            return True
        else:
            self.error(DownloadError,
                       ('ERROR: download may be incomplete.' +
                        ' rtmpdump exited with code 1 or 2'))
            return False


class VideoInfoExtractor(object):
    """
    Extract video information from videolectures page
    """
    _VALIDATE_URL = r'^http://videolectures.net'
    _GOOGLE_VIDEO = r'http://video\.google\.com/googleplayer\.swf\?docId'
    _META_TITLE_NAME = r'<meta name="title" content="\s*([^"]*?)\s*" />'
    _ORIG_FILENAME = r'([^\/]+)$'
    _XHR_REQUEST_PATH = r'xhr: .+\(\'(.+)\'\)'

    def __init__(self):
        self.body = ''

    def _to_stderr(self, message):
        """
        Print a message to stderr
        """
        sys.stderr.write(message)

    def error(self, err, message=None):
        """
        Raise error with a given message
        """
        if message is not None:
            self._to_stderr(message)
        raise err(message)

    def get_info(self, url):
        """
        Get video information
        """
        if not self.valid_url(url):
            return False

        # * Refer to the string handling on django's code.
        # https://docs.djangoproject.com/en/dev/topics/python3/
        view_resp = requests.get(url)
        body = view_resp.text.encode('utf8', 'ignore').decode('utf8')

        info = self.extract_info(body)
        info.update(self.extract_streaming_path(body))
        return info

    def get_streaming_meta(self, meta_url):
        """
        Request to meta_url and get metadata for streaming
        """

        # * Refer to the string handling on django's code.
        # https://docs.djangoproject.com/en/dev/topics/python3/
        meta_resp = requests.get(meta_url)
        meta_body = meta_resp.text.encode('utf8', 'ignore').decode('utf8')
        meta = self.extract_streaming_source(meta_body)
        meta.update(self.extract_metadata(meta_body))
        return meta

    def extract_streaming_path(self, body):
        """
        Get streaming path for XHRHttpRequest from view page
        """
        xhr_path_match = re.search(self._XHR_REQUEST_PATH, body)
        if xhr_path_match is not None:
            xhr_path = xhr_path_match.group(1)
        else:
            xhr_path = None
        xhr_url = "http://videolectures.net{0}".format(xhr_path)

        return {'streaming_meta_path': xhr_url}

    def extract_metadata(self, meta_body):
        """
        Extract metadata
        """
        base_pattern = r'<meta name="{0}" content="([^"]*)"\s*/>'
        meta_title = _regex_match_get(base_pattern.format('title'), meta_body)
        meta_part = _regex_match_get(base_pattern.format('part'), meta_body)
        meta_date = _regex_match_get(base_pattern.format('date'), meta_body)
        meta_type = _regex_match_get(base_pattern.format('type'), meta_body)

        return {
            'meta_title': meta_title,
            'meta_part': meta_part,
            'meta_date': meta_date,
            'meta_type': meta_type,
        }

    def extract_streaming_source(self, meta_body):
        """
        Extract streaming source
        """
        rtmp_source_match = re.search((
            r'\s*<video.*\sext="([^"]+)"' +
            r'.*\sstreamer="(rtmp://[^"]+)"' +
            r'\ssrc="([^"]+)"/>'),
            meta_body)
        if rtmp_source_match is not None:
            ext = rtmp_source_match.group(1)
            streamer = rtmp_source_match.group(2)
            rtmp_source = rtmp_source_match.group(3)
        else:
            ext = None
            streamer = None
            rtmp_source = None

        return {
            'ext': ext,
            'streamer': streamer,
            'source': rtmp_source,
        }

    def extract_info(self, body):
        """
        Extract metadata url
        """
        xhr_url_match = re.search(self._XHR_REQUEST_PATH, body)
        if xhr_url_match is not None:
            xhr_url = xhr_url_match.group(1)
        else:
            xhr_url = None

        if xhr_url is not None and xhr_url.endswith('xml'):
            default_filename = xhr_url.split('/')[1]
        else:
            self.error(ExtractionError,
                       "ERROR: can't get default_filename.")

        return {
            'default_filename': default_filename,
            'xhr_url': xhr_url,
        }

    def valid_url(self, url):
        """
        Check given url is valid url in videolectures.net or not.

        Parameters
        ----------
        url: string
            url given by commandline interface.
        """
        return (re.match(VideoInfoExtractor._VALIDATE_URL, url) is not None)
