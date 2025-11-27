import socket


class Socket_:
    def __init__(self, server_ip: str, port: int = 5555):
        if not server_ip:
            raise ValueError("server_ip is required")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.port = port
        self.addr = (self.server, self.port)
        self._buf = bytearray()
        self._last_fleet_json = None
        self.connect()


    def connect(self):
        try:        # TO VERIFY LATER, temporary
            print(f"Attempting to connect to {self.addr} ...")
            self.client.settimeout(5)
            self.client.connect(self.addr)
            self.client.settimeout(None)
            print("Connected! Waiting for welcome message ...")
            # Optionally receive an initial line (ack or matrix). Caller may ignore.
            try:
                return self.client.recv(2048).decode()
            except Exception:
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

    def get_matrix(self) -> str | None:
        try:
            self.client.setblocking(False)  # Dont wait for data
            # Accumulate any available data and return the latest matrix line if present
            while True:
                i = self._buf.find(b"\n")
                if i == -1:
                    chunk = self.client.recv(4096)
                    if not chunk:
                        return None
                    self._buf.extend(chunk)
                    continue
                # Extract one line and check if it is a matrix
                line = self._buf[:i].decode("utf-8")
                del self._buf[:i+1]
                if line.startswith("fleet|"):
                    # Cache fleet for consumers
                    self._last_fleet_json = line.split("|", 1)[1]
                    # Continue scanning for matrix
                    if len(self._buf) == 0:
                        return None
                    continue
                if line.startswith("matrix|"):
                    return line.split("|", 1)[1]
                # ignore non-matrix lines here
                # Loop again in case multiple lines are buffered
                if len(self._buf) == 0:
                    return None
        except BlockingIOError:
            # No data available yet, return empty or last known state
            return None
        except Exception as e:
            print("Receive failed:", e)
            return None
        finally:
            # Restore blocking mode
            self.client.setblocking(True)
    
    # Sends strings (in this case matrices)
    def send(self, data) -> str | None:
        try:
            # Ensure we send a complete line and receive exactly one reply line
            self.client.sendall((data + "\n").encode("utf-8"))
            reply = self._recv_line()
            return reply
        except socket.error as e: 
            print(e)
            return None

    def get_fleet(self) -> str | None:
        """
        Non-blocking retrieval of fleet JSON payload if available.
        Returns cached payload once, then clears it.
        """
        if self._last_fleet_json is not None:
            payload = self._last_fleet_json
            self._last_fleet_json = None
            return payload
        try:
            self.client.setblocking(False)
            while True:
                i = self._buf.find(b"\n")
                if i == -1:
                    chunk = self.client.recv(4096)
                    if not chunk:
                        return None
                    self._buf.extend(chunk)
                    continue
                line = self._buf[:i].decode("utf-8")
                del self._buf[:i+1]
                if line.startswith("fleet|"):
                    return line.split("|", 1)[1]
                # Put back matrix lines for get_matrix to consume
                if line.startswith("matrix|"):
                    self._buf[:0] = f"{line}\n".encode("utf-8")
                    return None
                if len(self._buf) == 0:
                    return None
        except BlockingIOError:
            return None
        except Exception as e:
            print("Receive failed:", e)
            return None
        finally:
            self.client.setblocking(True)
