import socket
from dotenv import load_dotenv
import os

load_dotenv()
ip = os.getenv("IP") or "127.0.0.1" #ip for testing

class Socket_:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ip
        self.port = 5555
        self.addr = (self.server, self.port)
        self._buf = bytearray()
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
