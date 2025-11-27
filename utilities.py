import button as btn
import random as rdm
import json
import os

# Boards
BUTTON_WIDTH, BUTTON_HEIGHT = 50, 50
DIVIDER = 1
MAGNITUDE = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREY = (200, 200, 200)


def create_matrix() -> list: 
    return [[0]*MAGNITUDE for _ in range(MAGNITUDE)]

# From collapsed string to 2d List
def string_to_matrix(s: str) -> list:
    return [list(map(int, row.split(','))) for row in s.split(';')]

# From 2d List to collapsed string
def matrix_to_string(matrix: list) -> str:
    return ';'.join(','.join(map(str, row)) for row in matrix)

# From tuple position to str position
def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])

# Handle matrix, Returns True if given cell == 1
def check_cell_val(matrix: list, position: tuple) -> bool: # (helper)
    return matrix[position[0]][position[1]] == 1


def assign_activation_to_cell(matrix: list, position: tuple):
    if check_cell_val(matrix, position):
        raise ValueError(f"Cell at {position} is already occupied.")
        # TO-DO (handle error correctly)
    else:
        matrix[position[0]][position[1]] = 1


def apply_attack_to_cell(matrix: list, position: tuple) -> int:
    row, col = position
    current = matrix[row][col]
    if current == 0:
        matrix[row][col] = 2
        return 2
    if current == 1:
        matrix[row][col] = 3
        return 3
    if current in (2, 3):
        raise ValueError(f"Cell at {position} already attacked.")
    raise ValueError(f"Invalid cell value {current} at {position}.")

# Create grid of buttons
def create_buttons(rows: int, cols: int) -> list:
    buttons = []
    for vertical_index in range(rows):
        row = []
        for horizontal_index in range(cols):
            x = horizontal_index * (BUTTON_WIDTH + DIVIDER) # x, y = cordinates in pixels
            y = vertical_index * (BUTTON_HEIGHT + DIVIDER) 
            row.append(btn.Button(vertical_index, horizontal_index, x, y, BUTTON_WIDTH, BUTTON_HEIGHT)) 
        buttons.append(row)
    return buttons

# Function to print the matrix nicely
def print_matrix(matrix):
    for row in matrix:
        print(' '.join(str(x) for x in row))

# # Generates random activation points inside a matrix
# def random_activ_matrix(matrix: list, cell_ammount: int):
#     activated = 0
#     while activated < cell_ammount:
#         x_rand = rdm.randint(0,MAGNITUDE-1)
#         y_rand = rdm.randint(0,MAGNITUDE-1)
#         if not check_cell_val(matrix, (x_rand,y_rand)):
#             matrix[x_rand][y_rand] = 1
#             activated += 1


def generate_random_ships(size=10, ships=[5, 4, 3, 3, 2]):
    # Initialize matrix
    matrix = [[0 for _ in range(size)] for _ in range(size)]

    for ship_len in ships:
        placed = False
        while not placed:
            orientation = rdm.choice(['H', 'V'])
            if orientation == 'H':
                row = rdm.randint(0, size - 1)
                col = rdm.randint(0, size - ship_len)
                # Check if the cells are free
                if all(matrix[row][col + i] == 0 for i in range(ship_len)):
                    for i in range(ship_len):
                        matrix[row][col + i] = 1
                    placed = True
            else:  # Vertical
                row = rdm.randint(0, size - ship_len)
                col = rdm.randint(0, size - 1)
                if all(matrix[row + i][col] == 0 for i in range(ship_len)):
                    for i in range(ship_len):
                        matrix[row + i][col] = 1
                    placed = True

    return matrix

#    Create a dictionary with keys: (row, col)
#    Values of each keys are boolean
def create_cell_state_map(size: int = MAGNITUDE) -> dict:
    return {(row, col): False for row in range(size) for col in range(size)}

#    Set the given (row, col) key in the hash -> True
def set_cell_attacked(cell_state_map: dict, position: tuple) -> None:
    if position not in cell_state_map:
        raise KeyError(f"Invalid cell position: {position}")
    cell_state_map[position] = True


def color_for(value: int):
    if value == 0:
        return WHITE
    if value == 1:
        return BLACK
    if value == 2:
        return BLUE
    if value == 3:
        return RED
    return GREY


# checks for events, button down or close-game.
def process_top_click_events(top_buttons) -> dict:
    import pygame  # local import for safety in non-GUI contexts
    top_click = None
    quit_flag = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_flag = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check TOP grid clicks
            for row in top_buttons:
                for button in row:
                    if button.is_clicked(event.pos):
                        top_click = button.index
                        break
                if top_click is not None:
                    break
    return {"quit": quit_flag, "top_click": top_click}



# Places multiple ships on the board.
# Returns a list of ship dictionaries.
def generate_fleet(board, ship_lengths):
    fleet = []

    for length in ship_lengths:
        ship = place_ship_randomly(board, length)
        fleet.append(ship)

    return fleet

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

def print_fleet(list_example):
    print("\n=== SHIPS IN BOARD ===")

    for i, ship in enumerate(list_example):
        print(f"\nShip{i+1}:")
        print(f"Direction:{ship['dir']}")
        print(f"Start:{ship['start']}")
        print(f"End:{ship['end']}")
        print(f"Coords:")
        for c in ship["coords"]:
            print(f"{c}")


# Convert generate_fleet return (list of ship dicts) to a compact JSON
# with integer coords, suitable for sending over the socket in one line.
def normalize_fleet_for_wire(fleet_obj: list) -> str:
    ships_out = []
    for ship in fleet_obj:
        # coords is a list of lists with one tuple [(r,c)] in each inner list
        cells = [[r, c] for [(r, c)] in ship.get("coords", [])]
        ships_out.append({
            "cells": cells,
            "start": cells[0] if cells else None,
            "end": cells[-1] if cells else None,
            "dir": ship.get("dir"),
        })
    payload = {"ships": ships_out}
    return json.dumps(payload, separators=(",", ":"))

# ---------- Sprites rendering helpers ------------------

# scale down the image and smooth it
def _load_scaled_image(candidate_paths: list, width: int, height: int):
    import pygame  # local import to avoid GUI dependency on server
    last_err = None
    for path in candidate_paths:
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (width, height))
        except Exception as e:
            last_err = e
            continue
    if last_err:
        raise last_err


    # Returns a dict containing scaled ship part sprites for both orientations.
    # Paths try subfolders first (sprites/horizontal, sprites/vertical), then root sprites/.
def _get_ship_sprites():
    import pygame  # local import

    # Candidate paths: prefer subfolders; fallback to root-level files
    horiz_start_paths = [
        os.path.join("sprites", "horizontal", "{[.jpeg"),
        os.path.join("sprites", "{[.jpeg"),
    ]
    horiz_mid_paths = [
        os.path.join("sprites", "horizontal", "l_l_l.jpeg"),
        os.path.join("sprites", "l_l_l.jpeg"),
    ]
    horiz_end_paths = [
        os.path.join("sprites", "horizontal", "]}.jpeg"),
        os.path.join("sprites", "]}.jpeg"),
    ]

    vert_start_paths = [
        os.path.join("sprites", "vertical", "^.jpeg"),
        os.path.join("sprites", "^.jpeg"),
    ]
    vert_mid_paths = [
        os.path.join("sprites", "vertical", "lEl.jpeg"),
        os.path.join("sprites", "lEl.jpeg"),
    ]
    vert_end_paths = [
        os.path.join("sprites", "vertical", "v.jpeg"),
        os.path.join("sprites", "v.jpeg"),
    ]

    # makes losts of boat sprites at scale smooth
    sprites = {
        "horizontal": {
            "start": _load_scaled_image(horiz_start_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "mid": _load_scaled_image(horiz_mid_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "end": _load_scaled_image(horiz_end_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
        },
        "vertical": {
            "start": _load_scaled_image(vert_start_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "mid": _load_scaled_image(vert_mid_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "end": _load_scaled_image(vert_end_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
        },
    }
    return sprites

    # Assign boat sprites to the corresponding Button.image based on the fleet payload.
    # - surface: pygame Surface (unused here; kept for backward compatibility)
    # - fleet_payload: JSON string (or dict) in the format produced by normalize_fleet_for_wire
    # - button_grid: 2D list of Button objects (for positions/sizes); this function sets Button.image
def procces_boats_sprites(surface, fleet_payload, button_grid) -> None:
    if not fleet_payload:
        return
    import pygame  # local import
    try:
        fleet = fleet_payload if isinstance(fleet_payload, dict) else json.loads(fleet_payload)
    except Exception:
        return
    sprites = _get_ship_sprites()

    # Clear any previous images
    for row in button_grid:
        for b in row:
            if hasattr(b, "image"):
                b.image = None

    ships = fleet.get("ships", [])
    for ship in ships:
        direction = ship.get("dir", "horizontal")
        cells = ship.get("cells", [])
        if not cells:
            continue
        n = len(cells)
        for i, cell in enumerate(cells):
            # cell is [row, col]
            try:
                r, c = int(cell[0]), int(cell[1])
            except Exception:
                continue
            if r < 0 or c < 0 or r >= len(button_grid) or c >= len(button_grid[0]):
                continue
            part = "mid"
            if i == 0:
                part = "start"
            elif i == n - 1:
                part = "end"
            img = sprites.get(direction, {}).get(part)
            if img is None:
                continue
            btn = button_grid[r][c]
            if hasattr(btn, "image"):
                btn.image = img


# Get ip for server
def get_local_ip() -> str:
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_probe:
            s_probe.connect(("8.8.8.8", 80))
            return s_probe.getsockname()[0]
    except Exception:
        try:
            import socket
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


# Build initial matrices and fleets for two players (for serverS)
def init_matrices_and_fleets():
    matrices = {}
    fleets = {}
    for pid in (0, 1):
        matrix = create_matrix()
        fleet = generate_fleet(matrix, [3, 4, 5, 6])
        matrices[pid] = matrix
        fleets[pid] = fleet
    return matrices, fleets
