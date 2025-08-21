[![PyPI](https://img.shields.io/pypi/v/readerlet.svg)](https://pypi.org/project/readerlet/)
[![Tests](https://github.com/pavzari/readerlet/workflows/Test/badge.svg)](https://github.com/pavzari/readerlet/actions?query=workflow%3ATest)

A CLI utility for extracting readable content from web pages. Converts web articles to clean HTML or plain text using [mozilla/readability](https://github.com/mozilla/readability). Extracted content can be packaged into EPUB or printed to stdout.

Includes Send to Kindle integration via the [stkclient](https://github.com/maxdjohnson/stkclient), allowing sending created EPUB articles directly to your Kindle device for offline reading.

## Installation

Install using `uv` or `pip`:

    uv tool install readerlet
    pip install readerlet

Note that this utility requires Node.js.

For convenience, the [nodejs-bin](https://github.com/samwillis/nodejs-pypi) package containing node binary & npm can be installed optionally as an extra dependency:

    uv tool install 'readerlet[node]'
    pip install 'readerlet[node]'

## Usage

For help, run:

    readerlet --help

The `readerlet send` packages web content as EPUB file and sends it to your Kindle. This feature stores credentials locally.

    readerlet send <url>

To send local file instead:

    readerlet send <path/to/local/file>

The `extract` command extracts content from URL and outputs an EPUB file to specified directory if used with `-e` flag:

    readerlet extract <url> -e <output-dir>
    readerlet extract https://example.com -e .

To print the extracted content to stdout as html or just text:

    readerlet extract <url> -o html
    readerlet extract <url> -o text

Both `extract` and `send` commands accept `-i` and `-h` flags that remove image-related elements and hyperlinks from content.

Remove hyperlinks:

    readerlet extract <url> -h
    readerlet send <url> -h

Remove images and hyperlinks:

    readerlet extract <url> -i -h -o html
    readerlet send <url> -i -h

## Authentication

Authentication is handled automatically when you first use the `readerlet send` command. If your credentials expire, you will be prompted to log in again.

The `readerlet kindle-login` command is also available for manually authenticating or switching between Amazon accounts.

## Development

First checkout the code. Then create a new virtual environment:

    cd readerlet
    python -m venv venv
    source venv/bin/activate

Install the dependencies and dev/test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
