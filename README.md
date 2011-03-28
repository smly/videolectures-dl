# videolectures-dl

A small command-line program to download videos from videolectures.net.
This program works under both python2 and python3.

## What doesn't work?

* error handling
* try resuming
* messy code

## Usage

    Usage: videolectures-dl [options] video_url
    
    Options:
      -h, --help       print this help text and exit
      -v, --version    print program version and exit
      -w, --overwrite  overwrite an existent file
      -t, --title      use title in filename
      -l, --literal    use literal title in filename

## Requirements

* rtmpdump
* python2 or python3
