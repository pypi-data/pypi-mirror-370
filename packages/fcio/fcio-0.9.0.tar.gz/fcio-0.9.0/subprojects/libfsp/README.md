# fc-stream-processor

This library can be used to process and fcio stream from the DAQ (readout-fc250b) in realtime.
Usual abbreviation is `FSP`.

## Building

`fsp` uses `meson` as build system. Install via `pip` or your local package management system (`apt`, `brew`, etc).

The `Makefile` contains a thin wrapper around meson commands to ease deployment.
Run `make` to build the library and create the build-dir.
Run `make local` to set the install path to `${HOME}/.local`.
Run `make install` to install the library, either in the system or in the above mentioned local directory.
If the library has been installed in this manner, and the `build` dir still exists, running `make uninstall` will remove all installed files.