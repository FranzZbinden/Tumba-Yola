import socket
from _thread import *
import threading
import sys
from dotenv import load_dotenv, dotenv_values
import os

load_dotenv()

server = os.getenv("IP")

# A better way to get ip address (not hardcoded)
# server = socket.gethostbyname(socket.gethostname())
port = 5555     # Port to send packets 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IP v4 adress / socket object

# Try if port is available to use
try:
    s.bind((server,port))

except socket.error as e: 
    str(e)

s.listen(2) # For opening the port, the number inside the parameter is the limit of users connected to the server
print("Waiting for connection, server started...")

# From string to tuple position
def read_pos(stri: str):
    stri = stri.split(",")
    return int(str[0]), int(str[1])

# from tuple position to str position for socket
def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])

# acces matrix Method
#   O(1)
#   (4,4)
#   list = [4,4]
#   value = list_name[list[0]]list[1]]

# (helper) Returns true if the position is already ocupied by 1
def check_cell_val(matrix: list, position: tuple) -> bool:
    return matrix[position[0]][position[1]] == 1


def assign_activation_to_cell(matrix: list, position: tuple):
    if check_cell_val(matrix, position):
        raise ValueError(f"Cell at {position} is already occupied.")
        # TO-DO (handle error correctly)
    else:
        matrix[position[0]][position[1]] = 1


matrix = [[0]*3 for _ in range(3)]    # creates the 10 * 10 matrix
current_turn = 0                      # 0 = player 1, 1 = player 2
lock = threading.Lock()               # To protect turn and matrtrix?
clients = []                          # Store all connected clients for broadcasting matrices

def matrix_to_string(matrix: list) -> str:
    return ';'.join(','.join(map(str, row)) for row in matrix)

def string_to_matrix(s: str) -> list:
    return [list(map(int, row.split(','))) for row in s.split(';')]

# Send the current matrix state to all connected clients
def broadcast_matrix():
    
    matrix_str = matrix_to_string(matrix) 
    
    for client_connected in clients[:]:  # sends the matrix to all connected clients on the list clients
        try:
            client_connected.sendall(str.encode(matrix_str))  # Send the matrix string with scandall (ensures all is sent)
        except: # handles connection failure or client disconnected
            if client_connected in clients:
                clients.remove(client_connected)    

# new threadded_client
def threaded_client(conn, player):
    global current_turn     # Modify var in global scope
    
    # Add this client to the clients list
    clients.append(conn)

    conn.send(str.encode(f"You are player: {player}"))
    print(f"Player {player} connected.")

    while True:
        try:
            data = conn.recv(2048).decode() # receives up to 2048 bytes, decodes to string (tuple), 
            if not data:    # if connection closed
                print(f"Player {player} desconnected.")
                break

            #waits for connection in (rows,column)
            parts = data.split(",")
            if len(parts) != 2:
                conn.send(str.encode("Invalid Format"))
                continue

            try:     # Safely access indexes to avoid out of range error
                pos = (int(parts[0]), int(parts[1]))
            except ValueError:
                conn.send(str.encode("Invalid Cordenates"))
                continue

            with lock:
                if player == current_turn:
                    try:
                        assign_activation_to_cell(matrix, pos)
                        print(f"Player {player} pressed {pos}")
                        reply = f"Movement accepted."
                        current_turn = 1 - current_turn  # Change turn
                        
                        # Broadcast updated matrix to all connected clients
                        broadcast_matrix()
                    except ValueError as e:
                        reply = str(e)
                else:
                    reply = "It's not your turn"

            conn.sendall(str.encode(reply))

        except:
            break
    
    # remove client from the list when they disconnect ?
    if conn in clients:
        clients.remove(conn)
    
    print(f"Connection lost with {player}")
    conn.close()
    currentPlayer -= 1


# main loop for finding clients
currentPlayer = 0
while True:
    conn, addr = s.accept() # blocks until recives client connection
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1






# pos = [(0,0), (100,100)]

# def threaded_client(conn, player):
#     conn.send(str.encode(make_pos(pos[player])))
#     reply = ""
#     while True:
#         try:
#             data = conn.recv(2048).decode() # 2048 Bits are sent for each package, the less the faster
#             pos[player] = read_pos(data)

#             reply = ""

#             if not data:
#                 print("Disconnected")
#                 break
#             else:
#                 if player == 1:
#                     reply = pos[0]
#                 else:
#                     reply = pos[1]

#                 print("Received: ", data)
#                 print("Sending: ", reply)

#             conn.sendall(str.encode(make_pos(reply)))
#         except:
#             break

#     print("Lost connection")
#     conn.close()

# currentPlayer = 0
# while True: # Looking for conections
#     conn, addr = s.accept() # conn object represents who is connected, addr stores the IP adress 
#     print("Connected to:", addr)

#     start_new_thread(threaded_client, (conn, currentPlayer))
#     currentPlayer +=1

    