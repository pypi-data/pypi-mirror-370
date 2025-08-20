import logging

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class ClientBlockPublisher:
    _instance = None  # Class variable to hold the single instance
    beams_ref: dict = None
    pipes: dict = None

    def __new__(cls, beam_ref: dict):
        if cls._instance is None:
            cls._instance = super(ClientBlockPublisher, cls).__new__(cls)
            # Initialize the instance once
            cls.beams_ref = beam_ref
            cls.pipes = {}
        return cls._instance

    @classmethod
    async def publish_message(cls, channel: str, message: bytes):
        """
        Publishes a message to a given channel.
        """
        try:
            if cls.pipes.get(channel) is None:
                beam_channel = cls.beams_ref[channel]
                cls.pipes[channel] = beam_channel[1]

            cls.pipes[channel].send(message)
        except KeyError:
            logger.warning(f"Tried to send message to already disconnected beacon {channel}.")
