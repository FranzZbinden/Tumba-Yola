import socket
from _thread import *
import threading
import sys
from dotenv import load_dotenv, dotenv_values
import os
import utilities as uc

load_dotenv()
server = os.getenv("IP") or "127.0.0.1" # ip for testing
port = 5555     

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IP v4 adress / socket object

# Try if port is available to use
try:
    s.bind((server,port))
except socket.error as e: 
    str(e)

s.listen(2) # For opening the port, the number inside the parameter is the limit of users connected to the server
print("Waiting for connection, server started...")

matrix = uc.create_matrix()
current_turn = 0                      # 0 = player 1, 1 = player 2
lock = threading.Lock()
clients = []                          # Store all connected clients for broadcasting matrices

# Send the current matrix state to all connected clients
def broadcast_matrix():
    
    matrix_str = uc.matrix_to_string(matrix) 
    
    for client_connected in clients[:]:  # sends the matrix to all connected clients on the list clients
        try:
            # Broadcast with type prefix and newline terminator
            client_connected.sendall(f"matrix|{matrix_str}\n".encode("utf-8"))  # Send the matrix line to all clients
        except: # handles connection failure or client disconnected
            if client_connected in clients:
                clients.remove(client_connected)    

# new threadded_client
def threaded_client(conn, player):
    global current_turn     # Modify var in global scope
    
    # Add this client to the clients list
    clients.append(conn)

    # Send a welcome/ack line
    conn.sendall(f"ack|You are player: {player}\n".encode("utf-8"))
    print(f"Player {player} connected.")

        # Send initial matrix to this client
    with lock:
        initial_matrix = uc.matrix_to_string(matrix)
        conn.sendall(f"matrix|{initial_matrix}\n".encode("utf-8"))

    while True:
        try:
            data = conn.recv(2048).decode() # receives up to 2048 bytes, decodes to string
            if not data:    
                print(f"Player {player} desconnected.")
                break

            # Process one or more newline-delimited messages
            for msg in data.splitlines():
                if not msg:
                    continue

                t, sep, payload = msg.partition("|")

                if t == "attack":
                    parts = payload.split(",")
                    if len(parts) != 2:
                        conn.sendall(b"error|Invalid Format\n")
                        continue

                    try:     # Safely access indexes to avoid out of range error
                        pos = (int(parts[0]), int(parts[1]))
                    except ValueError:
                        conn.sendall(b"error|Invalid Coordinates\n")
                        continue

                    with lock:
                        if player == current_turn:
                            try:
                                uc.assign_activation_to_cell(matrix, pos)
                                print(f"Player {player} pressed {pos}")
                                current_turn = 1 - current_turn  # Change turn

                                # Immediate ack to the requester
                                conn.sendall(b"ack|ok\n")

                                # Broadcast updated matrix to all connected clients
                                broadcast_matrix()
                            except ValueError as e:
                                conn.sendall(f"error|{e}\n".encode("utf-8"))
                        else:
                            conn.sendall(b"error|It's not your turn\n")

                elif t == "name":
                    # Optionally store/display name; acknowledge for now
                    conn.sendall(b"ack|ok\n")

                else:
                    conn.sendall(b"error|Unknown type\n")

        except:
            break

    if conn in clients:
        clients.remove(conn)
    
    print(f"Connection lost with {player}")
    conn.close()

# main loop for finding clients
currentPlayer = 0
while True:
    print("waiting for players")
    conn, addr = s.accept() # blocks until recives client connection
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1
