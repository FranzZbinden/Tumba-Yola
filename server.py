import socket
from _thread import *
import sys
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

ipAddress = os.getenv("IP")

server = ipAddress
# A better way to get ip address (not hardcoded)
# server = socket.gethostbyname(socket.gethostname())
port = 5555     # Port to send packets 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IP v4 adress


# Try if port is available to use
try:
    s.bind((server,port))

except socket.error as e: 
    str(e)

s.listen(2) # For opening the port, the number inside the parameter is the limit of users connected to the server
print("Waiting for connection, server started...")

# from string to tuple
def read_pos(str):
    str = str.split(",")
    return int(str[0]), int(str[1])


def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])


pos = [(0,0), (100,100)]

def threaded_client(conn, player):
    conn.send(str.encode(make_pos(pos[player])))
    reply = ""
    while True:
        try:
            data = conn.recv(2048).decode() # 2048 Bits are sent for each package, the less the faster
            pos[player] = read_pos(data)

            reply = ""

            if not data:
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = pos[0]
                else:
                    reply = pos[1]

                print("Received: ", data)
                print("Sending: ", reply)

            conn.sendall(str.encode(make_pos(reply)))
        except:
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0
while True: # Looking for conections
    conn, addr = s.accept() # conn object represents who is connected, addr stores the IP adress 
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer +=1

    