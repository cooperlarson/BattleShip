import json
import logging
import selectors
import struct

from pydantic import BaseModel


class MessageProcessor:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self.request = None

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self._read()
            self._process_request()
        if mask & selectors.EVENT_WRITE:
            self._write()

    def _read(self):
        try:
            data = self.sock.recv(4096)
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")
        except BlockingIOError:
            pass

    def _write(self):
        if self._send_buffer:
            try:
                sent = self.sock.send(self._send_buffer)
                self._send_buffer = self._send_buffer[sent:]
            except BrokenPipeError:
                self.close()

    def _process_request(self):
        if len(self._recv_buffer) < 2:
            return  # Wait until the full header is received

        header_length = struct.unpack(">H", self._recv_buffer[:2])[0]
        if len(self._recv_buffer) < 2 + header_length:
            return  # Wait until the full message is received

        # Decode JSON content
        content_bytes = self._recv_buffer[2:2 + header_length]
        self._recv_buffer = self._recv_buffer[2 + header_length:]
        try:
            self.request = json.loads(content_bytes.decode('utf-8'))
            logging.info(f"Received message: {self.request}")
        except json.JSONDecodeError:
            logging.error("Failed to decode message content")

    def send(self, content):
        if isinstance(content, BaseModel):
            content = content.model_dump_json().encode('utf-8')
        elif isinstance(content, str):
            content = content.encode('utf-8')
        elif not isinstance(content, bytes):
            raise TypeError("Content must be a Pydantic model, str, or bytes")

        message_data = self.create_message(content)
        self._send_buffer += message_data
        self.selector.modify(self.sock, selectors.EVENT_WRITE, data=self)

    @staticmethod
    def create_message(content):
        if not isinstance(content, bytes):
            raise TypeError("Content must be in bytes")

        header_bytes = struct.pack(">H", len(content))
        return header_bytes + content

    def close(self):
        try:
            self.selector.unregister(self.sock)
            self.sock.close()
        except Exception as e:
            logging.error(f"Error closing socket {self.addr}: {e}")
