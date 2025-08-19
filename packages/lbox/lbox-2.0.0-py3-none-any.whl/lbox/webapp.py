import sys
import re
import os
import pathlib
import time
import argparse
from datetime import timedelta
from configparser import ConfigParser
from importlib.resources import files, as_file
from typing import Dict, Tuple

import bottle

from .common import expiration_pattern, to_seconds, logging_setup
from .expirator import ExpireTask
from . import version

LOGGER = "LBOX"
LBOX_ROOTDIR_ENV_VAR = "LBOX_ROOTDIR"
DEFAULT_ROOT_DIRECTORY = "/var/www/lbox"


def cli_options(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--config", "-c", metavar="CONFFILE", help="Configuration file")
    return p.parse_args(argv)


lbox = bottle.Bottle()

def get_all_files(topdir: pathlib.Path) -> Dict[str, Tuple[pathlib.Path, float, float, str]]:
    filedict = {}
    for currentdir, dirs, files in topdir.walk():
        dirname = str(currentdir)
        match = re.search(expiration_pattern, dirname, re.IGNORECASE)
        if not match:
            continue

        secs = to_seconds(int(match.group(1)), match.group(2))
        for filename in files:
            if not filename.startswith("."):
                file = currentdir / filename
                stat = file.stat()
                filedict[file.name] = (file, stat.st_mtime, secs, human_size(stat.st_size))

    return filedict


def human_size(size):
    units = ["KB", "MB", "GB", "TB"]
    n = size
    lastu = "bytes"
    for u in units:
        lastn = n
        n = n / 1024
        if n < 1:
            return "{0:.2f} {1}".format(lastn, lastu)
        lastu = u
    else:
        return "{0:.2f} {1}".format(n, lastu)


@lbox.get("/file/<filename>")
def download(filename):
    all_files = get_all_files(lbox.config["rootdir"])
    try:
        filepath, mtime, ttl, size = all_files[filename]
    except KeyError:
        abort(404, f"We don't have {filename} [any longer]")
    return bottle.static_file(filepath.name, root=str(filepath.parent), download=True)


@lbox.get("/file/")
def list():
    filelst = []
    all_files = get_all_files(lbox.config["rootdir"])
    now = time.time()
    for file, mtime, ttl, sizestr in all_files.values():
        time_left = mtime + ttl - now
        filelst.append( (file.name, sizestr, time_left) )
    return dict(files=sorted(filelst))

def send_resource(resdir, filename):
    f = files("lbox.appfiles").joinpath(resdir, filename)
    with as_file(f) as fpath:
        return bottle.static_file(fpath.name, root=str(fpath.parent))

@lbox.get("/css/<filename>")
def sendcss(filename):
    return send_resource("css", filename)

@lbox.get("/html/<filename>")
def sendhtml(filename):
    return send_resource("html", filename)

@lbox.get("/js/<filename>")
def sendjs(filename):
    return send_resource("js", filename)

@lbox.get("/favicon.ico")
def favicon():
    return send_resource("html", "favicon-32x32.png")

@lbox.get("/version")
def get_version():
    return dict(version=version());

@lbox.get("/")
def mainpage():
    return send_resource("html", "index.html")

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    log = logging_setup(LOGGER)

    rootdir = pathlib.Path(os.getenv(LBOX_ROOTDIR_ENV_VAR, DEFAULT_ROOT_DIRECTORY))
    if not rootdir.is_dir():
        log.error("Bad root directory '%s'", rootdir)
        return 1

    lbox.config["rootdir"] = rootdir
    ExpireTask(rootdir, logger=log).go()
    bottle.run(app=lbox, server='bjoern', host="0.0.0.0", port=8080)
    #bottle.run(app=lbox, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
