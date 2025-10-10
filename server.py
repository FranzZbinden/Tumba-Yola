import socket
from _thread import *
import sys
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

ipAddress = os.getenv("IP")

server = ipAddress
port = 5555     # Port to send packets 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IP v4 adress


# Try if port is available to use
try:
    s.bind((server,port))

except socket.error as e: 
    str(e)

s.listen(2) # For opening the port, the number inside the parameter is the limit of users connected to the server
print("Waiting for connection, server started...")

def threaded_client(conn):

    reply = ""
    while True:
        try:
            data = conn.recv(2048) # 2048 Bits are sent for each package, the less the faster
            reply = data.decode("utf-8") # The information sent and recived is encoded, its decoded with data.decode()

            if not data:
                print("Disconnected")
                break
            else:
                print("Received: ", reply)
                print("Sending: ", reply)

            conn.sendall(str.encode(reply))
        except:
            break

    pass

while True: # Looking for conections
    conn, addr = s.accept() # conn object represents who is connected, addr stores the IP adress 
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, ))

    