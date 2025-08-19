import logging

_logger = logging.getLogger(__name__)


def preprocess(data):
    _logger.log(2, "Test message")
    print(data)
    return data
