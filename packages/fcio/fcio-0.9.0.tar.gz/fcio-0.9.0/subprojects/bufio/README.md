# bufio

This library provides a thin buffering layer on top of the unified Unix I/O model. It connects a TCP stream (as server
or client), Unix standard streams, or files and buffers all I/O operations. An interface very similar to stdio has been
implemented with additional support for polling.

## Installation

Requires `meson` and `ninja` to build.

Run `make` to compile the library.

Run `make test` to run unit tests.

