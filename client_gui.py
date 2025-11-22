import pygame
import utilities as uc

class ClientGUI:
    def __init__(self):
        # vvvvvvvvvvvvvv  Compute grid dimensions from utilities vvvvvvvvv
        self.GRID_WIDTH = uc.MAGNITUDE * uc.BUTTON_WIDTH + (uc.MAGNITUDE - 1) * uc.DIVIDER
        self.GRID_HEIGHT = uc.MAGNITUDE * uc.BUTTON_HEIGHT + (uc.MAGNITUDE - 1) * uc.DIVIDER
        # vvvvvvvvvvvvvv  Padding between the two boards (match client expectation: DIVIDER * 3) 
        self.INTER_GRID_PADDING = uc.DIVIDER * 3

        width = max(1000, self.GRID_WIDTH)
        height = 2 * self.GRID_HEIGHT + uc.DIVIDER + self.INTER_GRID_PADDING

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Client")
        self.clock = pygame.time.Clock()

        # Create buttons for both grids vvvvvvvvvvvvvvvvv
        self.top_buttons = uc.create_buttons(uc.MAGNITUDE, uc.MAGNITUDE)
        self.bottom_buttons = uc.create_buttons(uc.MAGNITUDE, uc.MAGNITUDE)

        # Center both boards horizontally & vertically as a stacked group
        center_x = (width - self.GRID_WIDTH) // 2
        total_stack_h = 2 * self.GRID_HEIGHT + self.INTER_GRID_PADDING
        top_offset_y = max(0, (height - total_stack_h) // 2)
        bottom_offset_y = top_offset_y + self.GRID_HEIGHT + self.INTER_GRID_PADDING

        # Apply offsets to TOP board
        for row in self.top_buttons:
            for button in row:
                button.rect.x += center_x
                button.rect.y += top_offset_y

        # Apply offsets to BOTTOM board
        for row in self.bottom_buttons:
            for button in row:
                button.rect.x += center_x
                button.rect.y += bottom_offset_y



    # Process pygame events and return:
    #   { 'quit': bool, 'top_click': (row, col) | None }
    # Only the TOP grid is interactive.

    # No relevant events in this frame:
    #     {"quit": False, "bottom_click": None}
    # Window close clicked:
    #     {"quit": True, "bottom_click": None}
    # Bottom grid cell clicked (example at row 3, col 5):
    #     {"quit": False, "bottom_click": (3, 5)}
   
    # checks for events, button down or close-game.
    def process_events(self) -> dict:
        top_click = None
        quit_flag = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_flag = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check TOP grid clicks
                for row in self.top_buttons:
                    for button in row:
                        if button.is_clicked(event.pos):
                            top_click = button.index
                            break
                    if top_click is not None:
                        break
        return {"quit": quit_flag, "top_click": top_click}

    # draw both boards according to their 2d lists and update the window.
    def draw(self, top_matrix: list, bottom_matrix: list) -> None:
        self.clock.tick(60)
        self.window.fill(uc.WHITE)

        # Draw top board
        for row in self.top_buttons:
            for button in row:
                r, c = button.index # row, columns
                button.color = uc.color_for(top_matrix[r][c])
                button.draw(self.window)

        # Draw bottom board
        for row in self.bottom_buttons:
            for button in row:
                r, c = button.index
                button.color = uc.color_for(bottom_matrix[r][c])
                button.draw(self.window)

        pygame.display.flip()

    def shutdown(self) -> None:
        pygame.quit()

