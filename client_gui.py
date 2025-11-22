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
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 50)

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

    # checks for events, button down or close-game.
    def process_events(self) -> dict:
        return uc.process_top_click_events(self.top_buttons)

    # draw both boards according to their 2d lists and update the window.
    def draw(self, top_matrix: list, bottom_matrix: list) -> None:
        self.clock.tick(60)
        self.window.fill(uc.WHITE)
        # Labels (Enemy)
        enemy_surf = self.font.render("Enemy", True, uc.BLACK)
        self.window.blit(enemy_surf, (10, 10))

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

