import asyncio
import logging
from collections import deque
from time import sleep

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.metrics_constants import (
    MAX_REQUEST_QUEUE_LEN, REQUEST_MAX_FREQUENCY,
    WAIT_FOR_REQUEST_IN_EMPTY_QUEUE_DELAY)
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class ReqQueue:
    _requeue: deque = None
    item_count: int = 0

    @classmethod
    def append(cls, func):
        if cls._requeue is not None:
            if cls.item_count >= MAX_REQUEST_QUEUE_LEN:
                logger.debug("Metric request was lost, queue too full")
                return
            cls._requeue.append(func)
            cls.item_count += 1

    @classmethod
    def init_queue(cls):
        cls._requeue = deque(maxlen=MAX_REQUEST_QUEUE_LEN)

    @classmethod
    def do_requests(cls, init=True):
        logger.debug("Starting request queue")
        if init:
            cls.init_queue()
        while True:
            try:
                asyncio.run(cls._requeue.pop())
            except IndexError:
                sleep(WAIT_FOR_REQUEST_IN_EMPTY_QUEUE_DELAY)
            else:
                cls.item_count -= 1
                sleep(REQUEST_MAX_FREQUENCY)
