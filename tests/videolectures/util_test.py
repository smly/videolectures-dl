# -*- coding: utf-8 -*-
import requests
import nose.tools
from mock import patch

from videolectures.util import (
    VideoInfoExtractor,
    VideoDownloader,
    DownloadError,
    ExtractionError)


def _build_response_object(fixture_path):
    r = requests.Response()
    r.status_code = 200
    r._content = _get_fixture(fixture_path)
    return r


def _get_fixture(fixture_path):
    with open(fixture_path, 'r') as f:
        # Read fixture content as a bytes object, not a unicode object
        html = f.read().encode()

    return html


class TestVideoDownloader(object):
    """
    Unit test for VideoDownloader
    """
    def test_error(self):
        with nose.tools.assert_raises(DownloadError):
            downloader = VideoDownloader({})
            downloader.error(DownloadError)

        with nose.tools.assert_raises(ExtractionError):
            downloader = VideoDownloader({})
            downloader.error(ExtractionError)

    def test_run(self):
        pass

    def test_dump_video(self):
        pass


class TestVideoInfoExtractor(object):
    """
    Unit test for VideoInfoExtractor
    """
    def test_valid_url(self):
        url_case1 = 'http://videolectures.net/test'
        url_case2 = 'http://videolectures.org/test'
        extractor = VideoInfoExtractor()

        assert extractor.valid_url(url_case1) is True
        assert extractor.valid_url(url_case2) is False

    def test_extract_info(self):
        fixture_path = "tests/resource/fixture_view.html"
        resp = _build_response_object(fixture_path)
        body = resp.text.encode('utf8', 'ignore').decode('utf8')

        extractor = VideoInfoExtractor()
        info = extractor.extract_info(body)

        assert info['default_filename'] == 'icml09_leskovec_msain'
        assert info['xhr_url'] == (
            "/icml09_leskovec_msain/video/1/smil.xml")

    def test_get_info(self):
        """
        test of VideoInfoExtractor.get_info
        """
        url = "http://videolectures.net/icml09_leskovec_msain/"
        fixture_path = "tests/resource/fixture_view.html"

        with patch.object(requests, 'get') as mocked_get:
            mocked_get.return_value = _build_response_object(fixture_path)

            extractor = VideoInfoExtractor()
            info = extractor.get_info(url)

        assert info['default_filename'] == 'icml09_leskovec_msain'
        assert info['xhr_url'] == (
            "/icml09_leskovec_msain/video/1/smil.xml")
        assert info['streaming_meta_path'] == (
            "http://videolectures.net/icml09_leskovec_msain/video/1/smil.xml")

    def test_extract_streaming_path(self):
        fixture_path = "tests/resource/fixture_view.html"
        resp = _build_response_object(fixture_path)
        body = resp.text.encode('utf8', 'ignore').decode('utf8')

        extractor = VideoInfoExtractor()
        meta = extractor.extract_streaming_path(body)

        assert meta['streaming_meta_path'] == (
            "http://videolectures.net/icml09_leskovec_msain/video/1/smil.xml")

    def test_extract_metadata(self):
        fixture_path = "tests/resource/fixture_meta.html"
        resp = _build_response_object(fixture_path)
        body = resp.text.encode('utf8', 'ignore').decode('utf8')

        extractor = VideoInfoExtractor()
        meta = extractor.extract_metadata(body)
        assert meta['meta_title'] == (
            "Modeling Social and Information Networks: " +
            "Opportunities for Machine Learning")
        assert meta['meta_type'] == 'Tutorial'
        assert meta['meta_part'] == '1'
        assert meta['meta_date'] == 'June 14, 2009'

    def test_extract_streaming_meta(self):
        fixture_path = "tests/resource/fixture_meta.html"

        with patch.object(requests, 'get') as mocked_get:
            mocked_get.return_value = _build_response_object(fixture_path)

            extractor = VideoInfoExtractor()
            info = extractor.get_streaming_meta("dummy_url")

        assert info['streamer'] == (
            "rtmp://hydro2.videolectures.net/vod")
        assert info['source'] == (
            "flv:v005/a8/vctm755bsql5ualqwsqxvpcsdfbes3bt.flv")
