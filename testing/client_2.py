import socket 
HOST = "127.0.0.1" 
PORT = 55555

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # no need for closing socket because of with 
    s.connect((HOST,PORT))  # connected to the server
    s.sendall(b"Hello, World") # -> send in bytes 
    data = s.recv(1024)

print(f"recived {data}")