import logging


class AbstractIngestion:

    def __init__(self, handler: logging.Handler):
        self.handler = handler

    def attach(self, logger: logging.Logger):
        logger.addHandler(self.handler)

    def detach(self, logger: logging.Logger):
        logger.removeHandler(self.handler)
