# Utilities to be used on the server
# Created on 12/23/2025
# Last Modified:

import socket
import sys
import random as rdm


# Get local ip 
def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_probe:
            s_probe.connect(("8.8.8.8", 80))
            return s_probe.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


# Enhanced bind funcion
def bind_safe(s: socket.socket, local_ip:str ,port: int) -> None:
    try:
        s.bind((local_ip,port))
    except socket.error as e: 
        print(f"Bind failed on {local_ip}:{port} -> {e}")
        sys.exit(1)

# Uses defauld magnitude set above
def create_matrix(magnitude: int=10, fill: int=0) -> list: 
    return [[fill]*magnitude for _ in range(magnitude)]

# Sends board to the given connection
def send_matrix(conn, matrix):
    try:
        matrix_str = uc.matrix_to_string(matrix)
        conn.sendall(f"matrix|{matrix_str}\n".encode("utf-8"))
    except:
        pass

# Places multiple ships on a NEW board.
# - Board values: 0 = empty, 1 = ship (placed randomly)
# - Returns: (board, fleet) where fleet is a list of ship dictionaries.
def generate_fleet(magnitude: int = 10, ship_lengths=(3, 4, 5, 6), fill: int = 0):
    board = create_matrix(magnitude, fill)
    fleet = []

    for length in ship_lengths:
        ship = place_ship_randomly(board, length)
        fleet.append(ship)

    return board, fleet

    # Places a ship of given length on the board.
    # Returns a list-of-lists like: [[(r,c)], [(r,c)], ...]
    # Also returns start, end, and direction.
def place_ship_randomly(board, length):
    size = len(board)

    while True:
        orientation = rdm.choice(["H", "V"])

        if orientation == "H":
            row = rdm.randint(0, size - 1)
            col = rdm.randint(0, size - length)
            coords = [[(row, col + i)] for i in range(length)]
        else:
            row = rdm.randint(0, size - length)
            col = rdm.randint(0, size - 1)
            coords = [[(row + i, col)] for i in range(length)]

        # Collision check
        if all(board[r][c] == 0 for [(r, c)] in coords):

            # Place the ship
            for [(r, c)] in coords:
                board[r][c] = 1

            return {
                "coords": coords,              # list of lists of tuples (len = cantidad de botonoes por barco)
                "start": coords[0],
                "end": coords[-1],
                "dir": "horizontal" if orientation == "H" else "vertical"
            }
