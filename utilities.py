import button as btn
import random as rdm

# Boards
BUTTON_WIDTH, BUTTON_HEIGHT = 50, 50
DIVIDER = 5
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


    # Apply an attack to the given cell without overwriting ships blindly.

    # Values:
    #   0 -> white (empty)   -> set to 2 (blue, miss)
    #   1 -> black (ship)    -> set to 3 (red, hit)
    #   2 -> blue (miss)     -> already attacked here (no change, raise)
    #   3 -> red (hit)       -> already attacked here (no change, raise)
    # Returns the new cell value (2 for miss, 3 for hit).
    # Raises ValueError if the cell has already been attacked (2 or 3).
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

# Generates random activation points inside a matrix
def random_activ_matrix(matrix: list, cell_ammount: int):
    activated = 0
    while activated < cell_ammount:
        x_rand = rdm.randint(0,MAGNITUDE-1)
        y_rand = rdm.randint(0,MAGNITUDE-1)
        if not check_cell_val(matrix, (x_rand,y_rand)):
            matrix[x_rand][y_rand] = 1
            activated += 1


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


# Process pygame events and return:
#   { 'quit': bool, 'top_click': (row, col) | None }
# Only the TOP grid is interactive.
#
# No relevant events in this frame:
#     {"quit": False, "bottom_click": None}
# Window close clicked:
#     {"quit": True, "bottom_click": None}
# Bottom grid cell clicked (example at row 3, col 5):
#     {"quit": False, "bottom_click": (3, 5)}
#
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