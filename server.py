import socket
from _thread import *
import threading
import sys
from Utilities import utilities as uc
from Utilities import server_utilities as ucs

server = ucs.get_local_ip()
port = 5555     

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IP v4 adress / socket object

# Try if port is available to use
try:
    s.bind((server,port))
except socket.error as e: 
    print(f"Bind failed on {server}:{port} -> {e}")
    sys.exit(1)

s.listen(2) 
print(f"Server started on {server}:{port}. Waiting for connection...")

# Initialize per-player matrices and fleets 
matrices, fleets = uc.init_matrices_and_fleets()
current_turn = 0                      # 0 = player 1, 1 = player 2
lock = threading.Lock()
clients = []                          # Store all connected clients
conn_to_player = {}                   # Map each connection to its player id
hit_counts = {0: 0, 1: 0}             # Successful hits per player (attacks landed on opponent)
TOTAL_SHIP_CELLS = 18                 
free_players = [0, 1]                 # Available player slots (reuse on reconnect)


def reset_game_state():
    global matrices, fleets, current_turn, hit_counts
    matrices, fleets = uc.init_matrices_and_fleets()
    current_turn = 0
    hit_counts = {0: 0, 1: 0}

def send_matrix(conn, matrix):
    try:
        matrix_str = uc.matrix_to_string(matrix)
        conn.sendall(f"matrix|{matrix_str}\n".encode("utf-8"))
    except:
        pass

def threaded_client(conn, player):
    global current_turn     

    # Register connection
    with lock:
        clients.append(conn)
        conn_to_player[conn] = player
    broadcast_turn()

    # Send a welcome/ack line
    conn.sendall(f"ack|You are player: {player}\n".encode("utf-8"))
    print(f"Player {player} connected.")

        # Send initial fleet and matrix to this client
    with lock:
        # Send fleet payload for processing by the client
        try:
            fleet_json = uc.normalize_fleet_for_wire(fleets[player])
            conn.sendall(f"fleet|{fleet_json}\n".encode("utf-8"))
        except Exception as e:
            conn.sendall(f"error|Fleet unavailable: {e}\n".encode("utf-8"))
        send_matrix(conn, matrices[player])

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

                    broadcast_needed = False
                    with lock:
                            try:
                                # Update ONLY the opponent's matrix
                                opponent = 1 - player
                                new_val = uc.apply_attack_to_cell(matrices[opponent], pos)  # 2 (miss -> blue) or 3 (hit -> red)
                                print(f"Player {player} pressed {pos}")
                                current_turn = 1 - current_turn  # Change turn
                                broadcast_needed = True

                                outcome = "hit" if new_val == 3 else "miss"
                                conn.sendall(f"update|{outcome}|{pos[0]},{pos[1]}\n".encode("utf-8"))

                                # Track hits and check winner
                                if new_val == 3:
                                    hit_counts[player] += 1
                                    if hit_counts[player] >= TOTAL_SHIP_CELLS:
                                        conn.sendall(b"win|You won\n")

                                # Send updated matrix to the opponent (so their client updates)
                                for c in clients:
                                    if conn_to_player.get(c) == opponent:
                                        send_matrix(c, matrices[opponent])
                                        break
                            except ValueError as e:
                                conn.sendall(f"error|{e}\n".encode("utf-8"))

                    # broadcast outside the lock to avoid deadlocking (broadcast_turn uses the same lock)
                    if broadcast_needed:
                        broadcast_turn()


                elif t == "name":
                    # Optionally store/display name; acknowledge for now
                    conn.sendall(b"ack|ok\n")

                else:
                    conn.sendall(b"error|Unknown type\n")

        except:
            break

    with lock:
        if conn in clients:
            clients.remove(conn)
        if conn in conn_to_player:
            del conn_to_player[conn]
        if player not in free_players and player in (0, 1):
            free_players.append(player)
        # If everyone disconnected, reset state for next game
        if len(clients) == 0:
            free_players[:] = [0, 1]
            reset_game_state()
    
    print(f"Connection lost with {player}")
    conn.close()

def broadcast_turn():
    # Snapshot to avoid holding lock during network I/O
    with lock:
        msg = f"turn|{current_turn}\n".encode("utf-8")
        targets = list(clients)
    for c in targets:
        try:
            c.sendall(msg)
        except:
            pass

# main loop
while True:
    print("waiting for players")
    conn, addr = s.accept() # blocks until recives client connection
    print("Connected to:", addr)

    # Assign an available slot (0/1). If full, reject connection.
    with lock:
        if free_players:
            player_id = free_players.pop(0)
        else:
            player_id = None
    if player_id is None:
        try:
            conn.sendall(b"error|Server full (2 players max)\n")
        except:
            pass
        conn.close()
        continue

    start_new_thread(threaded_client, (conn, player_id))

