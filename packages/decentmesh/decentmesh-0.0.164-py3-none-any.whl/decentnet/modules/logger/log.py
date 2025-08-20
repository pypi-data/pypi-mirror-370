import logging

from decentnet.consensus.dev_constants import LOG_LEVEL


def setup_logger(debug: bool, logger):
    if not debug:
        logging.disable(logging.DEBUG)
        return
    try:
        from rich.logging import RichHandler
    except ImportError:
        raise ImportError(
            "Rich not installed. Please install decent mesh with pip install decentnet[cli] to be able to see"
            " log and use cli")
    root = logging.getLogger()
    root.setLevel(logging.FATAL)

    logger.setLevel(LOG_LEVEL)
    logging.basicConfig(
        level=LOG_LEVEL if debug else logging.CRITICAL,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()]
    )
    logging.getLogger('sqlalchemy.engine').addHandler(logging.NullHandler())
    aio_log = logging.getLogger('aiosqlite')
    aio_log.setLevel(logging.CRITICAL)
    aio_log.addHandler(logging.NullHandler())
    logging.getLogger('asyncio').setLevel(logging.WARNING)
