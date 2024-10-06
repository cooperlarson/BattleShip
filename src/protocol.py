import selectors
import json
import struct


class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None

    def _set_selector_events_mask(self, mode):
        events = selectors.EVENT_READ if mode == "r" else selectors.EVENT_WRITE
        self.selector.modify(self.sock, events, data=self)

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
                if not self._send_buffer:
                    self.close()
            except BlockingIOError:
                pass

    def _json_encode(self, obj):
        return json.dumps(obj).encode('utf-8')

    def _json_decode(self, json_bytes):
        return json.loads(json_bytes.decode('utf-8'))

    def _create_message(self, content):
        content_bytes = self._json_encode(content)
        jsonheader = {
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader)
        message = struct.pack(">H", len(jsonheader_bytes)) + jsonheader_bytes + content_bytes
        return message

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()
        if self._jsonheader_len is None:
            self.process_protoheader()
        if self._jsonheader_len is not None and self.jsonheader is None:
            self.process_jsonheader()
        if self.jsonheader and self.request is None:
            self.process_request()

    def write(self):
        if self.request and not self._send_buffer:
            response = {"result": "ok"}
            message = self._create_message(response)
            self._send_buffer += message
        self._write()

    def close(self):
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(f"Error: {e}")
        try:
            self.sock.close()
        except OSError as e:
            print(f"Error: {e}")
        finally:
            self.sock = None

    def process_protoheader(self):
        if len(self._recv_buffer) >= 2:
            self._jsonheader_len = struct.unpack(">H", self._recv_buffer[:2])[0]
            self._recv_buffer = self._recv_buffer[2:]

    def process_jsonheader(self):
        if len(self._recv_buffer) >= self._jsonheader_len:
            self.jsonheader = self._json_decode(self._recv_buffer[:self._jsonheader_len])
            self._recv_buffer = self._recv_buffer[self._jsonheader_len:]

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if len(self._recv_buffer) >= content_len:
            self.request = self._json_decode(self._recv_buffer[:content_len])
            self._recv_buffer = self._recv_buffer[content_len:]
            print(f"Received request: {self.request} from {self.addr}")
            self._set_selector_events_mask("w")
