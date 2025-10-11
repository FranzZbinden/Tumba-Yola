import socket
from dotenv import load_dotenv
import os

load_dotenv()

ip = os.dotenv("IP")

class Network:
    def _init_(self):
        self.client = socket.socket(socket.IF_INET, socket.SOCK_STREAM)
        self.server = ip
        self.port = 5555
        self.addr = (self.server, self.port)
        self.id = self.connect()
        print(self.id)

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode() 
        except: 
            pass

