import socket
from collections import deque


class Socket_:
    def __init__(self, server_ip: str, port: int = 5555):
        if not server_ip:
            raise ValueError("server_ip is required")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.port = port
        self.addr = (self.server, self.port)
        self._buf = bytearray()

        # Message queues (filled by _pump/_handle_line)
        self._q_fleet = deque()
        self._q_matrix = deque()
        self._q_turn = deque()
        self._q_win = deque()
        self._q_update = deque()
        self._q_error = deque()
        self._q_ack = deque()

        self.player_id = None
        self.connect()


    def connect(self):
        try:        
            print(f"Attempting to connect to {self.addr} ...")
            self.client.settimeout(5)
            self.client.connect(self.addr)
            self.client.settimeout(None)
            print("Connected! Waiting for welcome message ...")

            # Pump until we see an ack (or connection ends)
            while self.player_id is None:
                self._pump(blocking=True)
                ack = self._pop_left(self._q_ack)
                if ack is None:
                    # If socket closed, stop looping
                    if self._socket_closed():
                        break
                    continue
                # ack payload example: "You are player: 0"
                try:
                    self.player_id = int(ack.split(": ")[1].strip())
                    print(f"You are player {self.player_id}")
                except Exception:
                    # Still return raw ack in case caller wants it
                    pass
                return f"ack|{ack}"

            return None
        except Exception as e:
            print(f"Connection failed: {e}")
            return None


    def _recv_line(self):
        while True:
            i = self._buf.find(b"\n")
            if i != -1:
                line = self._buf[:i].decode("utf-8")
                del self._buf[:i+1]
                return line
            chunk = self.client.recv(4096)
            if not chunk:
                return None
            self._buf.extend(chunk)

    def _socket_closed(self) -> bool:
        # Simple state check; not perfect, but enough to avoid infinite loops in connect().
        try:
            return self.client.fileno() == -1
        except Exception:
            return True

    def _pop_left(self, q: deque):
        return q.popleft() if q else None

    def _pump(self, blocking: bool) -> None:
        """
        Read from the socket into _buf and dispatch all complete newline-delimited messages.

        - blocking=False: do not wait for data (safe for GUI loop)
        - blocking=True: wait for data (useful right after send() / during connect())
        """
        prev_block = self.client.getblocking()
        try:
            self.client.setblocking(blocking)

            # Try to read at least once if blocking; otherwise only if data is ready.
            dispatched_any = False
            while True:
                # Dispatch any complete lines already buffered
                while True:
                    i = self._buf.find(b"\n")
                    if i == -1:
                        break
                    line = self._buf[:i].decode("utf-8", errors="replace")
                    del self._buf[: i + 1]
                    self._handle_line(line)
                    dispatched_any = True

                # In blocking mode, return after we've dispatched at least one message.
                # This prevents connect()/send() from blocking forever.
                if blocking and dispatched_any:
                    return

                # If we are non-blocking and no full line buffered, stop
                if not blocking:
                    try:
                        chunk = self.client.recv(4096)
                    except BlockingIOError:
                        return
                    if not chunk:
                        return
                    self._buf.extend(chunk)
                    # loop to dispatch
                    continue

                # blocking=True: wait for more bytes until at least one line dispatched
                chunk = self.client.recv(4096)
                if not chunk:
                    return
                self._buf.extend(chunk)
                # loop to dispatch newly completed lines
        except (ConnectionAbortedError, ConnectionResetError, OSError):
            return
        finally:
            self.client.setblocking(prev_block)

    def _handle_line(self, line: str) -> None:
        # Ignore empty lines
        if not line:
            return
        t, sep, payload = line.partition("|")
        if not sep:
            # Unknown format
            return

        if t == "ack":
            self._q_ack.append(payload)
            return
        if t == "fleet":
            self._q_fleet.append(payload)
            return
        if t == "matrix":
            self._q_matrix.append(payload)
            return
        if t == "turn":
            try:
                self._q_turn.append(int(payload))
            except Exception:
                pass
            return
        if t == "win":
            self._q_win.append(payload)
            return
        if t == "update":
            # Keep the entire line so client code can parse as before
            self._q_update.append(line)
            return
        if t == "error":
            self._q_error.append(payload)
            return
        # else: ignore unknown types for now


    def get_matrix(self) -> str | None:
        self._pump(blocking=False)
        # Prefer latest matrix if multiple arrived
        if not self._q_matrix:
            return None
        last = None
        while self._q_matrix:
            last = self._q_matrix.popleft()
        return last
    
    # Sends strings (in this case matrices)
    def send(self, data) -> str | None:
        try:
            self.client.sendall((data + "\n").encode("utf-8"))
            # Pump until we get update/error (server might send turn/matrix first)
            while True:
                self._pump(blocking=True)
                upd = self._pop_left(self._q_update)
                if upd is not None:
                    return upd
                err = self._pop_left(self._q_error)
                if err is not None:
                    return f"error|{err}"
                # If nothing yet, keep waiting (blocking pump will wait for bytes)
        except socket.error as e: 
            print(e)
            return None

    # Non-blocking retrieval of fleet JSON payload if available.
    # Returns cached payload once, then clears it.
    def get_fleet(self) -> str | None:
        self._pump(blocking=False)
        return self._pop_left(self._q_fleet)

        # Non-blocking retrieval of a win notification line if available.
        # Returns the payload after 'win|' once, otherwise None.
    def get_win(self) -> str | None:
        self._pump(blocking=False)
        return self._pop_left(self._q_win)

    def get_turn(self) -> int | None:
        self._pump(blocking=False)
        return self._pop_left(self._q_turn)

