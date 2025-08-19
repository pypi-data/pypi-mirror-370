import logging
import logging.config
from configparser import NoSectionError

expiration_pattern = r"(\d+)\s*(\w+)"

def to_seconds(num, timeunits):
    mults = dict(s=1, m=60, h=3600, d=3600*24)
    try:
        multiplier = mults[timeunits[0].lower()]
    except KeyError:
        return num;
    return num * multiplier


# def dirscan(directory: pahtlib.Path, ) -> Any:
    # pass


def logging_setup(logger):
    cfg = { "version": 1,
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "stream": "ext://sys.stderr"
                    },
                },
            "loggers": {logger: {"level": "DEBUG", "handlers": ["stdout"]}}
            }

    try:
        logging.config.dictConfig(cfg)
    except (ValueError, TypeError, AttributeError, ImportError):
        log = logging.getLogger(__file__)
        log.warning("Could not configure logging.", exc_info=True)
        return log

    log = logging.getLogger(logger)
    return log
