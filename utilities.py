import button as btn
import random as rdm

BUTTON_WIDTH, BUTTON_HEIGHT = 45, 45
DIVIDER = 10
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MAGNITUDE = 10

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