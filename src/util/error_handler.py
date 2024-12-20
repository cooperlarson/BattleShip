import functools
import traceback
import os
import signal
import psutil
import time
import socket

from src.util.logger import Logger


class ErrorHandler:
    def __init__(self, logger=None):
        self.logger = logger or Logger(log_file="general.log")
        self.dump_logs = False

    def log_error(self, error, context):
        error_msg = f"Error in {context}: {repr(error)}"
        self.logger.error(error_msg)
        self.logger.error(traceback.format_exc())

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                self.handle_error(e, func.__name__, *args, **kwargs)
                return self.recovery_action(func, e, *args, **kwargs)
        return wrapper

    def handle_error(self, error, context, *args, **kwargs):
        self.log_error(error, context)

    def recovery_action(self, func, error, *args, **kwargs):
        pass


class ServerErrorHandler(ErrorHandler):
    def __init__(self, logger=None):
        super().__init__(logger or Logger(log_file="server.log"))

    def handle_error(self, error, context, *args, **kwargs):
        super().handle_error(error, context)

    def recovery_action(self, func, error, *args, **kwargs):
        if isinstance(error, OSError) and error.errno == 48:  # Address already in use
            port = kwargs.get('port')
            if port:
                self.logger.info(f"Port {port} is already in use. Attempting to kill process on this port...")
                self._kill_process_on_port(port)
                self.logger.info("Retrying to start server...")
                if 'self' in kwargs and hasattr(kwargs['self'], 'sock'):
                    kwargs['self'].close_socket()
                return func(*args, **kwargs)
            else:
                self.logger.error("Port number is missing, cannot perform recovery.")
        else:
            self.logger.info("Attempting general server recovery...")

    @staticmethod
    def _kill_process_on_port(port):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.laddr.port == port:
                            os.kill(proc.ppid(), signal.SIGKILL)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
        except Exception as e:
            print(f"Failed to kill process on port {port}: {e}")


class ClientErrorHandler(ErrorHandler):
    def __init__(self, logger=None):
        super().__init__(logger or Logger(log_file="client.log"))

    def handle_error(self, error, context, *args, **kwargs):
        super().handle_error(error, context)

    def recovery_action(self, func, error, *args, **kwargs):
        self.logger.info("Attempting client recovery...")
        if isinstance(error, (ConnectionRefusedError, BrokenPipeError)):
            time.sleep(2)
            if 'self' in kwargs and hasattr(kwargs['self'], 'sock'):
                kwargs['self'].sock.close()
                kwargs['self'].sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                kwargs['self'].sock.settimeout(2)
                return func(*args, **kwargs)
