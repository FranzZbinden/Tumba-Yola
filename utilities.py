import button as btn

BUTTON_WIDTH, BUTTON_HEIGHT = 100, 100
DIVIDER = 10
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
MAGNITUDE = 5

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

# Handle matrix
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
