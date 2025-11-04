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

    # helper for reciving data: str
    def recive_matrix(self) -> str: 
        try:                                        # waits until recived data from server 
            data = self.client.recv(4096).decode()  # <-- from sendall(), it is recived here 
            return data
        except Exception as e:
            print("Receive failed:", e)

    # recive matrix from server to client
    def get_matrix(self) -> str:
        return self.recive_matrix()
    
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