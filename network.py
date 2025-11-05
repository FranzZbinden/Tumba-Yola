import socket
from dotenv import load_dotenv
import os

load_dotenv()
ip = os.getenv("IP")

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ip
        self.port = 5555
        self.addr = (self.server, self.port)
        self.connect()


    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode() 
        except: 
            pass

    def get_matrix(self) -> str:
        try:
            self.client.setblocking(False)  # Dont wait for data
            data = self.client.recv(4096).decode()
            return data
        except BlockingIOError:
            # No data available yet, return empty or last known state
            return None
        except Exception as e:
            print("Receive failed:", e)
            return None
    
    # Sends strings (in this case matrices)
    def send(self, data) -> str:
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048).decode() 
        except socket.error as e: 
            print(e)



# for testing =======
# n = Network()
# print(n.send("hello"))
# print(n.send("working"))