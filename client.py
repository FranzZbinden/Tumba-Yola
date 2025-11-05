import pygame
from network import Network
import button as btn

# Screen Size
WIDTH, HEIGHT = 700, 700
clientNumber = 0 

BUTTON_WIDTH, BUTTON_HEIGHT = 100, 100
MAGNITUDE = 5
ROWS, COLS = MAGNITUDE, MAGNITUDE
DIVIDER = 10
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

window = pygame.display.set_mode((WIDTH, HEIGHT))    
pygame.display.set_caption("Client")

# handle matrices
def string_to_matrix(s: str) -> list:
    return [list(map(int, row.split(','))) for row in s.split(';')]


def matrix_to_string(matrix: list) -> str:
    return ';'.join(','.join(map(str, row)) for row in matrix)

# from tuple position to str position
def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])


def check_cell_val(matrix: list, position: tuple) -> bool:
    return matrix[position[0]][position[1]] == 1


def assign_activation_to_cell(matrix: list, position: tuple):
    if check_cell_val(matrix, position):
        raise ValueError(f"Cell at {position} is already occupied.")
        # TO-DO (handle error correctly)
    else:
        matrix[position[0]][position[1]] = 1

# Waits for matrix sent from the server
# matrix_str = n.receive_matrix()
# print("Matrix received:", matrix_str)


#=========================================================================
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
# =========================================================================

buttons = create_buttons(ROWS, COLS)

def main():
    run = True
    n = Network()

    clock = pygame.time.Clock()

    matrix = [[0]*COLS for _ in range(ROWS)]    # creates the 10 * 10 matrix

    while run: 
        clock.tick(60)  # Limits fps 

        updated_str_matrix = n.get_matrix()
        if updated_str_matrix:  # Only update if data received bug HERE <--------
            updated_matrix = string_to_matrix(updated_str_matrix)
            matrix = updated_matrix

        window.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for row in buttons:
                    for button in row:
                        if button.is_clicked(event.pos):
                            print(f"Button {button.index} clicked") # return the 2d index
                            pos_str = make_pos(button.index)  # "row,col"
                            reply = n.send(pos_str)
                            print(f"Server response: {reply}")

        
        # Update button colors and draw
        for row in buttons:
            for button in row:
                row_idx, col_idx = button.index
                button.color = WHITE if matrix[row_idx][col_idx] == 0 else BLACK
                button.draw(window)

        pygame.display.flip()
    
    pygame.quit()



main()