import logging


def setup_logging(args):
    levels = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }
    logging.basicConfig(level=levels[min(args.verbose or 0, 3)])
