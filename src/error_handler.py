import functools
import traceback
import os
import signal
import psutil


class ErrorHandler:
    def __init__(self, logger=None):
        self.logger = logger or (lambda msg: print(msg))

    def log_error(self, error, context):
        error_msg = f"Error in {context}: {repr(error)}"
        self.logger(error_msg)
        traceback.print_exc()

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.handle_error(e, func.__name__, *args, **kwargs)
                return self.recovery_action(func, e, *args, **kwargs)
        return wrapper

    def handle_error(self, error, context, *args, **kwargs):
        self.log_error(error, context)

    def recovery_action(self, func, error, *args, **kwargs):
        pass


class ServerErrorHandler(ErrorHandler):
    def handle_error(self, error, context, *args, **kwargs):
        super().handle_error(error, context)

    def recovery_action(self, func, error, *args, **kwargs):
        if isinstance(error, OSError) and error.errno == 48:  # Address already in use
            port = kwargs.get('port')
            if port:
                print(f"Port {port} is already in use. Attempting to kill process on this port...")
                self._kill_process_on_port(port)
                print("Retrying to start server...")
                if 'self' in kwargs and hasattr(kwargs['self'], 'sock'):
                    kwargs['self'].close_socket()
                return func(*args, **kwargs)
            else:
                print("Port number is missing, cannot perform recovery.")
        else:
            print("Attempting general server recovery...")
        return None

    @staticmethod
    def _kill_process_on_port(port):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.laddr.port == port:
                            print(f"Killing process {proc.info['pid']} ({proc.info['name']}) using port {port}")
                            os.kill(proc.info['pid'], signal.SIGKILL)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
        except Exception as e:
            print(f"Failed to kill process on port {port}: {e}")


class ClientErrorHandler(ErrorHandler):
    def handle_error(self, error, context, *args, **kwargs):
        super().handle_error(error, context)

    def recovery_action(self, func, error, *args, **kwargs):
        print("Attempting client recovery...")
        # TODO: implement client recovery logic
        return None
