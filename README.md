# videolectures-dl

[![Build Status](https://api.travis-ci.org/smly/videolectures-dl.png?branch=master)](https://travis-ci.org/smly/videolectures-dl)

A small command-line program to download videos from videolectures.net.

## Requirements

* [rtmpdump][2]
* [requests][3]

  [1]: https://github.com/smly/videolectures-dl/tree/binary "videolectures-dl @ GitHub"
  [2]: http://rtmpdump.mplayerhq.hu/ "RTMPDump"
  [3]: https://pypi.python.org/pypi/requests "requests"

## Installation

    $ git clone http://github.com/smly/videolectures-dl
    $ cd videolectures-dl
    $ python setup.py install

## Usage

    $ videolectures-dl --help
    Usage: videolectures-dl [options] video_url
    
    Options:
      -h, --help       print this help text and exit
      -v, --version    print program version and exit
      -w, --overwrite  overwrite an existent file
      -t, --title      use title in filename

## What doesn't work?

* error handling
* resuming
