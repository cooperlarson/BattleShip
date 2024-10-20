import logging
from io import StringIO


class Logger:
    def __init__(self, name='Logger'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.buffer = StringIO()
        self.handler = logging.StreamHandler(self.buffer)
        self.handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)

    def get_logs(self):
        return self.buffer.getvalue()

    def clear(self):
        self.buffer.truncate(0)
        self.buffer.seek(0)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def __getattr__(self, attr):
        return getattr(self.logger, attr)
