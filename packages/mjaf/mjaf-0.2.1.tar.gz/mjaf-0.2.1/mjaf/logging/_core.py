import logging
import logging.handlers
import pathlib
import sys
from typing import Annotated

from mjaf._utils.constants import LOG_LEVEL

log = logging.getLogger(__name__)


# TODO: add options to use this
class Logger:
    """
    https://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting
    Writes the output from the print function to logs while still printing it to terminal
    """  # noqa E501

    def __init__(self, file):
        self.terminal = sys.stdout
        self.log = open(file, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def close(self):
        self.log.close()
        sys.stdout = open('/dev/stdout', 'w')

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass


class CustomFormatter(logging.Formatter):
    def __init__(self, *args, do_color=False, **kwargs):
        self.do_color = do_color

        super().__init__(*args, **kwargs)

    COLORS_BY_LEVEL = {
        logging.DEBUG: '34',  # Green
        logging.INFO: '26',  # Blue
        logging.WARNING: '220',  # Yellow
        logging.ERROR: '208',  # Orange
        logging.CRITICAL: '124',  # Red
    }

    def color_format(self, start_escape_code, end_escape_code):
        return (
            f"|0| %(asctime)s"
            f" |1| {start_escape_code}%(levelname)-8s{end_escape_code}"
            f" |2| %(name)s"
            f" |3| %(module)s:%(lineno)s %(funcName)s :: %(message)s"
        )

    def format(self, record: logging.LogRecord) -> str:
        start_escape_code = ''
        end_escape_code = ''

        if self.do_color:
            start_escape_code += (
                '\033[1;38;5;'
                + self.COLORS_BY_LEVEL[record.levelno]
                + 'm'
            )
            end_escape_code = '\033[m'

        formatter = logging.Formatter(
            self.color_format(
                start_escape_code,
                end_escape_code,
            ),
        )
        return formatter.format(record)


def reset_loggers_recursively(parent_logger_name):
    """
    Remove all handlers from a logger and all its child loggers.

    Args:
        parent_logger_name: Name of the parent logger (e.g., 'app')
    """
    def _reset_logger(logger):
        """Helper to remove all handlers from a single logger."""
        log.debug(f'clean: {logger.name}')
        logger.setLevel(logging.NOTSET)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    # Clean the parent logger
    _reset_logger(logging.getLogger(parent_logger_name))

    # Find and clean all child loggers

    prefix = (
        parent_logger_name
        + '.' if parent_logger_name else ''
    )

    for name, logger_obj in list(logging.Logger.manager.loggerDict.items()):
        if name.startswith(prefix) and isinstance(logger_obj, logging.Logger):
            _reset_logger(logger_obj)


def set_handlers(
    logger_name: str = '',
    level: str | None = None,
    path: pathlib.Path | str | None = None,
    rotation_size: Annotated[int, 'MB'] = 10,
    rotations: int = 5,
    log_print_statements=False,
):

    level = level or LOG_LEVEL

    logger = logging.getLogger(logger_name)

    # start from scratch
    reset_loggers_recursively(logger_name)

    if path is not None:
        path = pathlib.Path(path).resolve()

        file_handler = logging.handlers.RotatingFileHandler(
            path,
            maxBytes=1000**2 * rotation_size,
            backupCount=rotations,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            CustomFormatter(do_color=False),
        )

        logger.addHandler(file_handler)

    # >>> Prints to terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(
        CustomFormatter(do_color=True),
    )
    # <<<

    logger.addHandler(stream_handler)

    # "specifies the lowest-severity log message a logger will handle"
    logger.setLevel(level)

    log.info('Logging configured successfully')
    log.info(f'{level=}')
    if path is not None:
        log.info(f'Logging to {path}')

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical(
            'Uncaught exception',
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = handle_exception
