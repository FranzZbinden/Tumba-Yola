# Server
# Created: 12/23/2025
# Last Modified:

import socket
from Utilities import server_utilities as uc
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
        conn, addr = s.accept()
        print("Connected to:", addr)

        with manager_lock:
            room, player_index, status = manager.matchmake(conn, board_size=10, ship_lengths=(3, 4, 5, 6))
            room_id = room.room_id

        conn.sendall(f"ROOM {room_id} PLAYER {player_index}\n".encode())

        # If matched, notify both players that the game can start
        if status == "OK":
            try:
                host = room.clients[0]
                joiner = room.clients[1]
                if host is not None:
                    host.sendall(b"OPPONENT_JOINED\n")
                if joiner is not None:
                    joiner.sendall(b"OPPONENT_JOINED\n")
            except Exception:
                pass


