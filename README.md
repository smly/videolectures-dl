# videolectures-dl

[(This is the source code branch, if you are looking for a compiled windows binary, click here.)][1]

A small command-line program to download videos from videolectures.net.
This program works under both python2 and python3.

  [1]: https://github.com/smly/videolectures-dl/tree/binary "videolectures-dl @ GitHub"

## Usage

    Usage: videolectures-dl [options] video_url
    
    Options:
      -h, --help       print this help text and exit
      -v, --version    print program version and exit
      -w, --overwrite  overwrite an existent file
      -t, --title      use title in filename
      -l, --literal    use literal title in filename

## What doesn't work?

* error handling
* try resuming
* messy code

## Requirements

* rtmpdump
* python2 or python3
