import socket
import threading

# Part #1 ===========(Pick the port & server)===============================

HEADER = 64
PORT = 5050
            # "getIpFrom(getComputerName)"
SERVER = socket.gethostbyname(socket.gethostname()) # Gets the server local IP address 
ADDR = (SERVER,PORT)    # When port & IP addr initlialized, make a tuple for binding into server 

# Part #2 ===========(Pick the socket & binde socket with address)===========

# Create new socket & specifing the type of addres for the socket
# socket = makeSocket(with type IPv4, stream data in there)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Sets the Ip version and type of (data transfer)?
server.bind(ADDR)   # add IP address and port into server

def handle_client(conn, addr):  # concurrently run each client
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode


# Function for start function of waiting for conections, then passing them to handle_client() in new thread
def start():    # Handle new connections
    server.listen()
    while True:
        conn, addr = server.accept()    # server.accept() waits for conection, then store them in (object of client, address&port)
        thread = threading.Thread(target=handle_client, args=(conn,addr))   # Starts thread and pass connection to handle_client() and the arguments passed to it: (conn,addr)
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")   # Tells how many threads are active (clients)

print("[STARTING] server is starting...")
start()

# 28:28