import socket 

HOST = "127.0.0.1"

PORT = 55555

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # no need for closing socket because of with 
    s.bind((HOST,PORT))
    s.listen()
    conn,addr = s.accept() # blocking


    with conn: # open single socket connection and read data
        print(f"Connected by {addr}")
        while True: 
            data = conn.recv(1024) # blocking
            if not data:   # empty packet -> close conn
                break   # when closing connection, close loop -> 
            conn.sendall(data)