import argparse
import sys
import time
import os
import pathlib
import re
import threading
import logging
from configparser import ConfigParser

from .common import to_seconds, expiration_pattern, logging_setup

log = logging.getLogger(__file__)


class PeriodicTask(threading.Timer):

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if self.finished.is_set():
                break
            self.function(*self.args, **self.kwargs)


class ExpireTask:

    def __init__(self, rootdir: pathlib.Path, interval: float = 30.0, logger: logging.Logger = None):
        self.log = logger if logger else log
        self.rootdir = rootdir
        self.interval = interval
        self.task = PeriodicTask(self.interval, self.expire_all)

    def go(self):
        self.task.start()

    def expire_entry(self, entry: pathlib.Path, secs: float):
        stat = entry.stat()
        now = time.time()
        if (now - stat.st_mtime) > secs:
            self.log.info(f"Removing '%s'", entry)
            entry.unlink()

    def expire_all(self):
        for currentdir, dirs, files in self.rootdir.walk():
            dirname = str(currentdir)
            match = re.search(expiration_pattern, dirname, re.IGNORECASE)
            if not match:
                continue

            secs = to_seconds(int(match.group(1)), match.group(2))
            for filename in files:
                self.expire_entry(currentdir / filename, secs)
