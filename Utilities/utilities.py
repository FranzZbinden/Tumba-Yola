from . import button as btn
import random as rdm
import json
import os

# Boards data
BUTTON_WIDTH, BUTTON_HEIGHT = 30, 30
DIVIDER = 1 # space between
MAGNITUDE = 10 # length -> (x,y)
MUSIC ="source_files/audio/pirate_7.mp3"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
OCEAN_BLUE = (0, 88, 171)
RED = (255, 0, 0)
GREY = (200, 200, 200)

# Uses defauld magnitude set above
def create_matrix() -> list: 
    return [[0]*MAGNITUDE for _ in range(MAGNITUDE)]

# From collapsed string -> 2d List
def string_to_matrix(s: str) -> list:
    return [list(map(int, row.split(','))) for row in s.split(';')]

# From 2d List to collapsed string
def matrix_to_string(matrix: list) -> str:
    return ';'.join(','.join(map(str, row)) for row in matrix)

# From tuple position to str position
def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])


def check_cell_val(matrix: list, position: tuple) -> bool: # (helper)
    return matrix[position[0]][position[1]] == 1

# Takes a matrix & position(tuple(x,y)) and activate cell (for testing, unused)
def assign_activation_to_cell(matrix: list, position: tuple):
    if check_cell_val(matrix, position):
        raise ValueError(f"Cell at {position} is already occupied.")
    else:
        matrix[position[0]][position[1]] = 1

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

# Returns color based on value 
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
def generate_fleet(board, ship_lengths=(3,4,5,6)):
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

# prints on terminal formated fleet
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

# Convert generate_fleet to a compact JSON
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


# Scales down the image and smooth it
def _load_scaled_image(candidate_paths: list, width: int, height: int):
    import pygame  # local import to avoid GUI dependency on server
    last_err = None
    for path in candidate_paths:
        try:
            raw = pygame.image.load(path)

            # If the image has an alpha channel, preserve it.
            # Otherwise, treat the background color (top-left pixel) as transparent (colorkey).
            has_alpha = raw.get_masks()[3] != 0
            if has_alpha:
                img = raw.convert_alpha()
                return pygame.transform.smoothscale(img, (width, height))

            img = raw.convert()
            try:
                key = img.get_at((0, 0))
                img.set_colorkey(key, pygame.RLEACCEL)
            except Exception:
                pass

            scaled = pygame.transform.smoothscale(img, (width, height))
            try:
                scaled.set_colorkey(key, pygame.RLEACCEL)
            except Exception:
                pass
            return scaled
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
        os.path.join("source_files", "sprites", "horizontal", "{[.png"),
        os.path.join("source_files", "sprites", "horizontal", "{[.PNG"),
        os.path.join("source_files", "sprites", "{[.png"),
        os.path.join("source_files", "sprites", "{[.PNG"),
        # legacy
        os.path.join("source_files", "sprites", "horizontal", "{[.jpeg"),
        os.path.join("source_files", "sprites", "{[.jpeg"),
    ]
    horiz_start_destroyed_paths = [
        os.path.join("source_files", "sprites", "horizontal", "{[(destroyed).png"),
        os.path.join("source_files", "sprites", "horizontal", "{[(destroyed).PNG"),
        os.path.join("source_files", "sprites", "{[(destroyed).png"),
        os.path.join("source_files", "sprites", "{[(destroyed).PNG"),
        # legacy (if present)
        os.path.join("source_files", "sprites", "horizontal", "{[(destroyed).jpeg"),
        os.path.join("source_files", "sprites", "{[(destroyed).jpeg"),
    ]
    horiz_mid_paths = [
        os.path.join("source_files", "sprites", "horizontal", "l_l_l.png"),
        os.path.join("source_files", "sprites", "horizontal", "l_l_l.PNG"),
        os.path.join("source_files", "sprites", "l_l_l.png"),
        os.path.join("source_files", "sprites", "l_l_l.PNG"),
        # legacy
        os.path.join("source_files", "sprites", "horizontal", "l_l_l.jpeg"),
        os.path.join("source_files", "sprites", "l_l_l.jpeg"),
    ]
    horiz_mid_destroyed_paths = [
        os.path.join("source_files", "sprites", "horizontal", "l_l_l(destroyed).png"),
        os.path.join("source_files", "sprites", "horizontal", "l_l_l(destroyed).PNG"),
        os.path.join("source_files", "sprites", "l_l_l(destroyed).png"),
        os.path.join("source_files", "sprites", "l_l_l(destroyed).PNG"),
        # legacy
        os.path.join("source_files", "sprites", "horizontal", "l_l_l(destroyed).jpeg"),
        os.path.join("source_files", "sprites", "l_l_l(destroyed).jpeg"),
    ]
    horiz_end_paths = [
        os.path.join("source_files", "sprites", "horizontal", "]}.png"),
        os.path.join("source_files", "sprites", "horizontal", "]}.PNG"),
        os.path.join("source_files", "sprites", "]}.png"),
        os.path.join("source_files", "sprites", "]}.PNG"),
        # legacy
        os.path.join("source_files", "sprites", "horizontal", "]}.jpeg"),
        os.path.join("source_files", "sprites", "]}.jpeg"),
    ]
    horiz_end_destroyed_paths = [
        os.path.join("source_files", "sprites", "horizontal", "]}(destroyed).png"),
        os.path.join("source_files", "sprites", "horizontal", "]}(destroyed).PNG"),
        os.path.join("source_files", "sprites", "]}(destroyed).png"),
        os.path.join("source_files", "sprites", "]}(destroyed).PNG"),
        # legacy
        os.path.join("source_files", "sprites", "horizontal", "]}(destroyed).jpeg"),
        os.path.join("source_files", "sprites", "]}(destroyed).jpeg"),
    ]

    vert_start_paths = [
        os.path.join("source_files", "sprites", "vertical", "^.png"),
        os.path.join("source_files", "sprites", "vertical", "^.PNG"),
        os.path.join("source_files", "sprites", "^.png"),
        os.path.join("source_files", "sprites", "^.PNG"),
        # legacy
        os.path.join("source_files", "sprites", "vertical", "^.jpeg"),
        os.path.join("source_files", "sprites", "^.jpeg"),
    ]
    vert_start_destroyed_paths = [
        os.path.join("source_files", "sprites", "vertical", "^(destroyed).png"),
        os.path.join("source_files", "sprites", "vertical", "^(destroyed).PNG"),
        os.path.join("source_files", "sprites", "^(destroyed).png"),
        os.path.join("source_files", "sprites", "^(destroyed).PNG"),
        # legacy
        os.path.join("source_files", "sprites", "vertical", "^(destroyed).jpeg"),
        os.path.join("source_files", "sprites", "^(destroyed).jpeg"),
    ]
    vert_mid_paths = [
        os.path.join("source_files", "sprites", "vertical", "lEl.png"),
        os.path.join("source_files", "sprites", "vertical", "lEl.PNG"),
        os.path.join("source_files", "sprites", "lEl.png"),
        os.path.join("source_files", "sprites", "lEl.PNG"),
        # legacy
        os.path.join("source_files", "sprites", "vertical", "lEl.jpeg"),
        os.path.join("source_files", "sprites", "lEl.jpeg"),
    ]
    vert_mid_destroyed_paths = [
        os.path.join("source_files", "sprites", "vertical", "lEl(destroyed).png"),
        os.path.join("source_files", "sprites", "vertical", "lEl(destroyed).PNG"),
        os.path.join("source_files", "sprites", "lEl(destroyed).png"),
        os.path.join("source_files", "sprites", "lEl(destroyed).PNG"),
        # legacy
        os.path.join("source_files", "sprites", "vertical", "lEl(destroyed).jpeg"),
        os.path.join("source_files", "sprites", "lEl(destroyed).jpeg"),
    ]
    vert_end_paths = [
        os.path.join("source_files", "sprites", "vertical", "v.png"),
        os.path.join("source_files", "sprites", "vertical", "v.PNG"),
        os.path.join("source_files", "sprites", "v.png"),
        os.path.join("source_files", "sprites", "v.PNG"),
        # legacy
        os.path.join("source_files", "sprites", "vertical", "v.jpeg"),
        os.path.join("source_files", "sprites", "v.jpeg"),
    ]
    vert_end_destroyed_paths = [
        os.path.join("source_files", "sprites", "vertical", "v(destroyed).png"),
        os.path.join("source_files", "sprites", "vertical", "v(destroyed).PNG"),
        os.path.join("source_files", "sprites", "v(destroyed).png"),
        os.path.join("source_files", "sprites", "v(destroyed).PNG"),
        # legacy
        os.path.join("source_files", "sprites", "vertical", "v(destroyed).jpeg"),
        os.path.join("source_files", "sprites", "v(destroyed).jpeg"),
    ]

    # makes boat sprites at scale smooth
    sprites = {
        "horizontal": {
            "start": _load_scaled_image(horiz_start_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "mid": _load_scaled_image(horiz_mid_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "end": _load_scaled_image(horiz_end_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "start_destroyed": _load_scaled_image(horiz_start_destroyed_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "mid_destroyed": _load_scaled_image(horiz_mid_destroyed_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "end_destroyed": _load_scaled_image(horiz_end_destroyed_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
        },
        "vertical": {
            "start": _load_scaled_image(vert_start_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "mid": _load_scaled_image(vert_mid_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "end": _load_scaled_image(vert_end_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "start_destroyed": _load_scaled_image(vert_start_destroyed_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "mid_destroyed": _load_scaled_image(vert_mid_destroyed_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
            "end_destroyed": _load_scaled_image(vert_end_destroyed_paths, BUTTON_WIDTH, BUTTON_HEIGHT),
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
            # Optional: also clear sprite variants
            if hasattr(b, "normal_image"):
                b.normal_image = None
            if hasattr(b, "destroyed_image"):
                b.destroyed_image = None

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
            destroyed_img = sprites.get(direction, {}).get(f"{part}_destroyed")
            if img is None:
                continue
            btn = button_grid[r][c]
            if hasattr(btn, "image"):
                btn.normal_image = img
                btn.destroyed_image = destroyed_img
                btn.image = img


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


#  Return the NEW value of the first cell that changed, or None if no change.
def first_changed_value(old_m: list, new_m: list) -> int | None:
    for r in range(len(new_m)):
        for c in range(len(new_m[r])):
            if old_m[r][c] != new_m[r][c]:
                return new_m[r][c]
    return None