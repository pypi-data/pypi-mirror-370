import logging

logger = logging.getLogger("api_exception")

# If the user has not set a level (default is NOTSET), set it to WARNING
# This prevents excessive INFO logs unless explicitly configured by the user
if logger.level == logging.NOTSET:
    logger.setLevel(logging.WARNING)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def add_file_handler(path: str, level=logging.INFO):
    """
    Add a file handler to also write logs to a file.

    Parameters
    ----------
    path : str
        File path where logs will be written.
    level : int, optional
        Logging level for this handler (default: INFO).

    Usage
    -----
    >>> from api_exception.logger import add_file_handler, logger
    >>> add_file_handler("api_exception.log", level=logging.DEBUG)
    >>> logger.warning("This will be logged to both console and file")
    >>> logger.info("This INFO log will also be written to the file"
    """
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(level)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)