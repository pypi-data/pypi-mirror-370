## Lbox - a litterbox clone-ish

This is a self-hosted server that makes you make available files for a limited amount of time.

### Installation

The best way to install this is via `pipx` which will create a virtual environment and manage the dependencies for you:

    pipx install lbox

That will work when the project is available from [Pypi](https://pypi.org), meanwhile from the .tar.gz file as created by the build command `sdist`:

    pipx install lbox-X.Y.tar.gz

Where, of course, X.Y is the version number.

### Building from repo

You should be working on a virtual environment. On your virtual environment install the `build`package:

    python3 -m pip install build

then simply run build, which will create the source distribution (i.e. the .tar.gz file) and the wheel package:

    python3 -m build

### Using Lbox

Lbox scans the directory specified in the environment variable `LBOX_ROOTDIR` for directories with names of the form *number timeunits* e.g. `5 hours`, `2days`, `20m`, etc. And the files under those directories will be deleted after the specified time elapses, being available for download in the meantime. Note that you only need to specify `d`, `m`, `h` and `s` for days, minutes, hours and seconds, respectively. Only the initial matters. Also note that whitespace between the number and the units is optional.

If the `LBOX_ROOTDIR` environment variable is not set, the default folder will be `/var/www/lbox`


#### The lbox server

The `lbox`command is the web server that _publishes_  the files. It will just provide a list of the files along with its size and the time to expiration. Every file can be downloaded from the url ending in `/file/<filename>`, with no additional directory path. No, the server doesn't allow uploading new files, but what's the need for it? Being self hosted, you can always `scp`into the right directories to share.

The lbox server runs by default on port 8080.

To run `lbox`use the command:

    LBOX_ROOTDIR=/path/to/dir lbox

It is recommended that a `systemd`is created to run `lbox` continuously. It is also recommended that `lbox`be run on http behind a reverse proxy that handles the SSL certificate and manages security etc.

### License
This project is released under the MIT license.
