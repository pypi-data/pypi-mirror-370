import logging

log = logging.getLogger(__name__)

class ColorFormatter(logging.Formatter):
    red = "\033[91m"
    orange = "\033[33m"
    reset = "\033[0m"
    
    prefix = "[%(levelname)s] (%(name)s)"
    suffix = "%(message)s"

    FORMATS = {
        logging.WARNING: f"{orange}{prefix}{reset} {suffix}",
        logging.ERROR: f"{red}{prefix}{reset} {suffix}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def configure_logger(log: logging.Logger):
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(ColorFormatter())
    log.addHandler(consoleHandler)
    log.propagate = False