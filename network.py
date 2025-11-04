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
        self.pos = self.connect()
        #self.matrix = self.connect()

# TO-DO: get matrix -> string
    def getPos(self):
        return self.pos
    

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode() 
        except: 
            pass

# TO-DO: send data -> get matrix
    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048).decode() 
        except socket.error as e: 
            print(e)



# for testing =======
# n = Network()
# print(n.send("hello"))
# print(n.send("working"))