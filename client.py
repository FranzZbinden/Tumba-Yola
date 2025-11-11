import pygame
from socket_ import Socket_
import button as btn
import utilities as uc

# Screen Size
WIDTH, HEIGHT = 700, 700
# BLACK = (0, 0, 0)
# WHITE = (255, 255, 255)

window = pygame.display.set_mode((WIDTH, HEIGHT))    
pygame.display.set_caption("Client")

clientNumber = 0 
buttons = uc.create_buttons(uc.MAGNITUDE, uc.MAGNITUDE)
updated_matrix = uc.create_matrix()

def main():
    global updated_matrix
    run = True
    n = Socket_()
    clock = pygame.time.Clock()

    while run: 
        clock.tick(60) 
        window.fill(uc.WHITE)

        # TO-DO: define protocol for reciving data from socket for name, points, matrices...
        updated_str_matrix = n.get_matrix() # <- refactor get_matrix to get_data (and then redirect data)

        if updated_str_matrix: 
            updated_matrix = uc.string_to_matrix(updated_str_matrix)

        for event in pygame.event.get():    # Closes client if event is quit
            if event.type == pygame.QUIT:
                run = False
                
            # Iterates matrix for pressed button, if pressed: send tuple -> server [O(n)]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for row in buttons:
                    for button in row:
                        if button.is_clicked(event.pos):
                            print(f"Button {button.index} clicked") # return the 2d index
                            pos_str = uc.make_pos(button.index)  # "row, col"
                            reply = n.send(f"attack|{pos_str}")     # sends typed command to server
                            print(f"Server response: {reply}")

        # Update button colors and draw
        for row in buttons:
            for button in row:
                row_idx, col_idx = button.index
                button.color = uc.WHITE if updated_matrix[row_idx][col_idx] == 0 else uc.BLACK
                button.draw(window)

        pygame.display.flip()
    pygame.quit()
main()