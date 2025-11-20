import pygame
from socket_ import Socket_
import button as btn
import utilities as uc

# Screen Size and grid layout
GRID_WIDTH = uc.MAGNITUDE * uc.BUTTON_WIDTH + (uc.MAGNITUDE - 1) * uc.DIVIDER  # Width size of one board< -> buttons + DIVIDER gaps
GRID_HEIGHT = uc.MAGNITUDE * uc.BUTTON_HEIGHT + (uc.MAGNITUDE - 1) * uc.DIVIDER  # Height size of one board< -> buttons + DIVIDER gaps
INTER_GRID_PADDING = uc.DIVIDER * 3  # padding in between boards is the defauld devider of buttons X 3
WIDTH, HEIGHT = max(700, GRID_WIDTH), 2 * GRID_HEIGHT + uc.DIVIDER + INTER_GRID_PADDING  # adjust window size acording to padding and buttons sizes

window = pygame.display.set_mode((WIDTH, HEIGHT))    
pygame.display.set_caption("Client")

clientNumber = 0 
top_buttons = uc.create_buttons(uc.MAGNITUDE, uc.MAGNITUDE) 
bottom_buttons = uc.create_buttons(uc.MAGNITUDE, uc.MAGNITUDE)
for row in bottom_buttons:
    for button in row:
        button.rect.y += GRID_HEIGHT + uc.DIVIDER + INTER_GRID_PADDING
top_matrix = uc.create_matrix() # <<<<<<<-------------------- TOP MATRIX ---------------------<<<<<<
bottom_matrix = uc.create_matrix() # <<<<<<<-------------------- botton MATRIX ---------------------<<<<<<

def main():
    global top_matrix, bottom_matrix
    run = True
    n = Socket_()
    clock = pygame.time.Clock()

    while run: 
        clock.tick(60) 
        window.fill(uc.WHITE)

        # TO-DO: define protocol for reciving data from socket for name, points, matrices...
        updated_str_matrix = n.get_matrix() # <- refactor get_matrix to get_data (and then redirect data)

        if updated_str_matrix: 
            bottom_matrix = uc.string_to_matrix(updated_str_matrix)

        for event in pygame.event.get():    # Closes client if event is quit
            if event.type == pygame.QUIT:
                run = False
                
            # Iterates bottom matrix for pressed button, if pressed: send tuple -> server [O(n)]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for row in bottom_buttons:
                    for button in row:
                        if button.is_clicked(event.pos):
                            print(f"Button {button.index} clicked") # return the 2d index
                            pos_str = uc.make_pos(button.index)  # "row, col"
                            reply = n.send(f"attack|{pos_str}")     # sends typed command to server
                            print(f"Server response: {reply}")

        # Update and draw top grid
        for row in top_buttons:
            for button in row:
                row_idx, col_idx = button.index
                button.color = uc.WHITE if top_matrix[row_idx][col_idx] == 0 else uc.BLACK
                button.draw(window)

        # Update and draw bottom grid (active)
        for row in bottom_buttons:
            for button in row:
                row_idx, col_idx = button.index
                button.color = uc.WHITE if bottom_matrix[row_idx][col_idx] == 0 else uc.BLACK
                button.draw(window)

        pygame.display.flip()
    pygame.quit()
main()