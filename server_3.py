# Server
# Created: 12/23/2025
# Last Modified:

import socket
from Utilities import server_utilities as uc
from Utilities.room import Room 
from Utilities.room_manager import RoomManager 
import sys
import threading

LOCAL_IP = uc.get_local_ip()
PORT = 55555

manager = RoomManager()
manager_lock = threading.Lock()
Rooms = []


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # no need for closing socket because of with 
    uc.bind_safe(s, LOCAL_IP,PORT)
    s.listen()

    while True:
        print("Waiting for player 1")
        conn1, addr1 = s.accept() # blocks until recives a client connection
        print("Connected to:", addr1)

        with manager_lock:
            room, p0 = manager.create_room(conn1)
            room_id = room.room_id

        conn1.sendall(f"ROOM {room_id} PLAYER 0\n".encode())

        print("Waiting for player 2...")
        conn2, addr2 = s.accept() # blocks until recives a seccond client connection
        print("Connected to:", addr2)

        with manager_lock:
            room, p1, status = manager.join_room(conn2, room_id)

        if status != "OK":
            conn2.sendall(f"ERROR {status}\n".encode())
            conn2.close()
            continue

        conn2.sendall(f"ROOM {room_id} PLAYER 1\n".encode())
        conn1.sendall(b"OPPONENT_JOINED\n")


