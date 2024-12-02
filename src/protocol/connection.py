import json
import logging
import selectors
import struct

from pydantic import BaseModel

from src.protocol.response_schemas import NameChangeResponse


class Connection:
    def __init__(self, selector, sock, addr):
        self.id = f"{addr[0]}:{addr[1]}"
        self.name = None
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
                logging.debug(f"Received {len(data)} bytes from {self.addr}")
            else:
                raise RuntimeError("Peer closed connection.")
        except BlockingIOError:
            pass
        except RuntimeError as e:
            logging.error(f"Read error on {self.addr}: {e}")
            self.close()

    def _write(self):
        if self._send_buffer:
            try:
                # Send data from the buffer
                sent = self.sock.send(self._send_buffer)
                self._send_buffer = self._send_buffer[sent:]  # Trim sent data
            except BrokenPipeError:
                logging.error("Broken pipe; closing connection.")
                self.close()
                return

            # If buffer is empty, switch back to EVENT_READ
            if not self._send_buffer:
                logging.debug(f"Buffer empty for {self.addr}; switching to EVENT_READ.")
                self.selector.modify(self.sock, selectors.EVENT_READ, data=self)

    def _process_request(self):
        while len(self._recv_buffer) >= 2:
            header_length = struct.unpack(">H", self._recv_buffer[:2])[0]
            if len(self._recv_buffer) < 2 + header_length:
                break
            content_bytes = self._recv_buffer[2:2 + header_length]
            self._recv_buffer = self._recv_buffer[2 + header_length:]
            try:
                self.request = json.loads(content_bytes.decode('utf-8'))
                logging.info(f"Received message: {self.request}")
            except json.JSONDecodeError:
                logging.error("Failed to decode message content")

    def send(self, content):
        if isinstance(content, BaseModel):
            content = content.json().encode('utf-8')
        elif isinstance(content, str):
            content = content.encode('utf-8')
        elif not isinstance(content, bytes):
            raise TypeError("Content must be a Pydantic model, str, or bytes")

        # Add content to the buffer
        message_data = self.create_message(content)
        self._send_buffer += message_data

        if self._send_buffer:
            try:
                sent = self.sock.send(self._send_buffer)
                self._send_buffer = self._send_buffer[sent:]  # Remove sent data
                logging.debug(f"Sent {sent} bytes to {self.addr}")
            except BrokenPipeError:
                logging.error("Broken pipe; closing connection.")
                self.close()
            except Exception as e:
                logging.error(f"Error sending data to {self.addr}: {e}")
                self.close()

        if not self._send_buffer:
            self.selector.modify(self.sock, selectors.EVENT_READ, data=self)

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
            logging.info(f"Closed connection to {self.addr}")
        except Exception as e:
            logging.error(f"Error closing socket {self.addr}: {e}")

    def set_name(self, msg):
        if 'user' in msg:
            self.name = msg['user']
            logging.info(f"Set name for {self.id} to {self.name}")
            self.send(NameChangeResponse(name=self.name, user=self.name, success=True))
        else:
            logging.warning(f"Invalid name set request from {self.id}")
            self.send(NameChangeResponse(name=None, success=False))
