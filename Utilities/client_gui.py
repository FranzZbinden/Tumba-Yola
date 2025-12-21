import pygame, sys, time
from . import utilities as uc
from pathlib import Path

class ClientGUI:
    def __init__(self):
        # vvvvvvvvvvvvvv  Compute grid dimensions from utilities vvvvvvvvv
        self.GRID_WIDTH = uc.MAGNITUDE * uc.BUTTON_WIDTH + (uc.MAGNITUDE - 1) * uc.DIVIDER
        self.GRID_HEIGHT = uc.MAGNITUDE * uc.BUTTON_HEIGHT + (uc.MAGNITUDE - 1) * uc.DIVIDER
        # vvvvvvvvvvvvvv  Padding between the two boards (match client expectation: DIVIDER * 3) 
        self.INTER_GRID_PADDING = uc.DIVIDER * 3

        # Make window width close to grid width (with a small margin), not a fixed large minimum
        width_margin = 260
        width = max(400, self.GRID_WIDTH + width_margin)
        height = 2 * self.GRID_HEIGHT + uc.DIVIDER + self.INTER_GRID_PADDING

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Client")
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 50)

        self._bg_tile = None
        self._miss_sprite = None
        self._hit_sprite = None
        try:
            project_root = Path(__file__).parent.parent
            water_candidates = [
                project_root / "source_files" / "sprites" / "water.png",
                project_root / "source_files" / "sprites" / "water.PNG",
                project_root / "source_files" / "sprites" / "water.jpg",
                project_root / "source_files" / "sprites" / "water.JPG",
            ]
            img = None
            last_err = None
            for p in water_candidates:
                try:
                    img = pygame.image.load(str(p)).convert()
                    break
                except Exception as e:
                    last_err = e
            if img is None and last_err is not None:
                raise last_err
            tile_size = 32
            self._bg_tile = pygame.transform.smoothscale(img, (tile_size, tile_size))
        except Exception:
            self._bg_tile = None

        # Miss marker sprite for top board
        try:
            project_root = Path(__file__).parent.parent
            miss_path = project_root / "source_files" / "sprites" / "pool_float_orange.PNG"
            miss_img = pygame.image.load(str(miss_path)).convert_alpha()
            self._miss_sprite = pygame.transform.smoothscale(miss_img, (uc.BUTTON_WIDTH, uc.BUTTON_HEIGHT))
        except Exception:
            self._miss_sprite = None

        # Hit marker sprite for top board
        try:
            project_root = Path(__file__).parent.parent
            hit_path = project_root / "source_files" / "sprites" / "pool_float_red.PNG"
            hit_img = pygame.image.load(str(hit_path)).convert_alpha()
            self._hit_sprite = pygame.transform.smoothscale(hit_img, (uc.BUTTON_WIDTH, uc.BUTTON_HEIGHT))
        except Exception:
            self._hit_sprite = None

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
        self.clock.tick(15)
        if self._bg_tile is not None:
            tw, th = self._bg_tile.get_size()
            ww, wh = self.window.get_size()
            # Tile the image across the whole window
            for y in range(0, wh, th):
                for x in range(0, ww, tw):
                    self.window.blit(self._bg_tile, (x, y))
        else:
            self.window.fill(uc.OCEAN_BLUE)
        # Labels (Enemy)
        enemy_surf = self.font.render("Enemy", True, uc.BLACK)
        self.window.blit(enemy_surf, (10, 10))
        # Label (You) at bottom-right
        you_surf = self.font.render("You", True, uc.BLACK)
        self.window.blit(you_surf, (self.window.get_width() - you_surf.get_width() - 10,
                                     self.window.get_height() - you_surf.get_height() - 10))

        # Draw top board
        for row in self.top_buttons:
            for button in row:
                r, c = button.index # row, columns
                cell_val = top_matrix[r][c]
                # Miss marker on enemy board
                if cell_val == 2 and self._miss_sprite is not None:
                    button.image = self._miss_sprite
                    button.color = None
                # Hit marker on enemy board
                elif cell_val == 3 and self._hit_sprite is not None:
                    button.image = self._hit_sprite
                    button.color = None
                else:
                    # Clear markers if cell changed
                    if getattr(button, "image", None) in (self._miss_sprite, self._hit_sprite):
                        button.image = None
                    button.color = None if cell_val == 0 else uc.color_for(cell_val)
                button.draw(self.window)

        # Draw bottom board
        for row in self.bottom_buttons:
            for button in row:
                r, c = button.index
                cell_val = bottom_matrix[r][c]
                # Miss marker on your board (opponent missed)
                if cell_val == 2 and self._miss_sprite is not None:
                    button.image = self._miss_sprite
                    button.color = None
                    button.draw(self.window)
                    continue

                # Swap ship sprite to destroyed version when hit
                if cell_val == 3 and getattr(button, "destroyed_image", None) is not None:
                    button.image = button.destroyed_image
                elif cell_val == 1 and getattr(button, "normal_image", None) is not None:
                    button.image = button.normal_image
                else:
                    # Clear miss marker if cell changed away from miss
                    if getattr(button, "image", None) is self._miss_sprite:
                        button.image = None
                # If there's a ship sprite on this cell, don't draw a solid color behind it;
                # let the tiled water background show through the sprite's transparent pixels.
                if cell_val in (1, 3) and getattr(button, "image", None) is not None:
                    # Don't paint behind ship sprites (normal or destroyed)
                    button.color = None
                else:
                    # Also avoid painting hit ship cells red; keep background visible
                    if cell_val == 3:
                        button.color = None
                    else:
                        button.color = None if cell_val == 0 else uc.color_for(cell_val)
                # If ship cell was hit, remove sprite so red shows through
                if cell_val == 3 and getattr(button, "destroyed_image", None) is None and hasattr(button, "image"):
                    # Fallback: if no destroyed sprite is available, remove sprite
                    # (background stays visible because we avoid painting red)
                    button.image = None
                button.draw(self.window)

        pygame.display.flip()

    # def music(repeat: int, music_path):
    #     pygame.mixer.init()
    #     pygame.mixer.music.load(music_path) 
    #     pygame.mixer.music.unload()
    #     pygame.mixer.music.play(loops=repeat, start=10, fade_ms=2000)
    #     pygame.mixer.music.rewind()

    #     pygame.mixer.music.stop()
    #     pygame.mixer.music.pause()
    #     pygame.mixer.music.unpause()

    #     pygame.mixer.music.fadeout(1000)

    #     pygame.mixer.music.get_volume()
    #     pygame.mixer.music.set_volume(0.5)

    def shutdown(self) -> None:
        pygame.quit()

