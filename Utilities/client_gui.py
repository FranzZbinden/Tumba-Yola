import pygame, sys, time
from . import utilities as uc
from pathlib import Path
import math

class ClientGUI:
    def __init__(self):
        # vvvvvvvvvvvvvv  Compute grid dimensions from utilities vvvvvvvvv
        self.MAGNITUDE = uc.MAGNITUDE
        self.DIVIDER = uc.DIVIDER
        self.cell_size = uc.BUTTON_WIDTH  # will be recomputed on resize
        self.GRID_WIDTH = self.MAGNITUDE * self.cell_size + (self.MAGNITUDE - 1) * self.DIVIDER
        self.GRID_HEIGHT = self.MAGNITUDE * self.cell_size + (self.MAGNITUDE - 1) * self.DIVIDER
        # vvvvvvvvvvvvvv  Padding between the two boards (match client expectation: DIVIDER * 3) 
        self.INTER_GRID_PADDING = uc.DIVIDER * 3

        # Make window width close to grid width
        self._width_margin = 260
        self._min_width = max(400, self.GRID_WIDTH + self._width_margin)
        self._min_height = 2 * self.GRID_HEIGHT + uc.DIVIDER + self.INTER_GRID_PADDING

        width = self._min_width
        height = self._min_height

        self.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Client")
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 50)
        self._toast_font = uc.load_jersey10_font(64)
        self._toast_text: str | None = None
        self._toast_color: tuple[int, int, int] = (255, 255, 255)
        self._toast_until_ms: int = 0

        self._bg_tile = None
        self._miss_sprite = None
        self._hit_sprite = None
        self._enemy_icon = None
        self._you_icon = None
        self._icon_size = (125, 125)  
        self._icon_amp = 6            # pixels (small movement)
        self._icon_speed = 0.45       
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
            self._miss_sprite = pygame.image.load(str(miss_path)).convert_alpha()
        except Exception:
            self._miss_sprite = None

        # Hit marker sprite for top board
        try:
            project_root = Path(__file__).parent.parent
            hit_path = project_root / "source_files" / "sprites" / "pool_float_red.PNG"
            self._hit_sprite = pygame.image.load(str(hit_path)).convert_alpha()
        except Exception:
            self._hit_sprite = None

        # Pelican icons (with coconut)
        try:
            project_root = Path(__file__).parent.parent
            enemy_path_coco = project_root / "source_files" / "sprites" / "pelican_right_coco.png"
            img = pygame.image.load(str(enemy_path_coco)).convert_alpha()
            self._enemy_icon = pygame.transform.smoothscale(img, self._icon_size)
        except Exception:
            self._enemy_icon = None

        try:
            project_root = Path(__file__).parent.parent
            you_path_coco = project_root / "source_files" / "sprites" / "pelican_left_coco.png"
            img = pygame.image.load(str(you_path_coco)).convert_alpha()
            self._you_icon = pygame.transform.smoothscale(img, self._icon_size)
        except Exception:
            self._you_icon = None

        # Create buttons for both grids vvvvvvvvvvvvvvvvv
        self.top_buttons = uc.create_buttons(uc.MAGNITUDE, uc.MAGNITUDE)
        self.bottom_buttons = uc.create_buttons(uc.MAGNITUDE, uc.MAGNITUDE)

        # Initial layout
        self._apply_window_size(width, height)

    def _compute_cell_size(self, width: int, height: int) -> int:
        # Reserve some space for edge icons and breathing room
        margin_x = max(40, self._icon_size[0] + 15)
        margin_y = 24

        # Available width for one grid
        avail_w = max(1, width - 2 * margin_x)

        # Available height for two stacked grids + padding
        grids_space = max(1, height - 2 * margin_y - self.INTER_GRID_PADDING)

        # Use a square cell size that fits both constraints
        by_w = (avail_w - (self.MAGNITUDE - 1) * self.DIVIDER) // self.MAGNITUDE
        by_h = ((grids_space // 2) - (self.MAGNITUDE - 1) * self.DIVIDER) // self.MAGNITUDE
        return max(10, int(min(by_w, by_h)))

    def _apply_window_size(self, width: int, height: int) -> None:
        # Recompute cell size + derived grid dimensions for this window size
        self.cell_size = self._compute_cell_size(width, height)
        self.GRID_WIDTH = self.MAGNITUDE * self.cell_size + (self.MAGNITUDE - 1) * self.DIVIDER
        self.GRID_HEIGHT = self.MAGNITUDE * self.cell_size + (self.MAGNITUDE - 1) * self.DIVIDER

        # Update all button rect sizes
        for grid in (self.top_buttons, self.bottom_buttons):
            for row in grid:
                for button in row:
                    button.rect.width = self.cell_size
                    button.rect.height = self.cell_size

        self._layout_buttons(width, height)

    # Reposition the two button grids to keep them centered in the current window.
    def _layout_buttons(self, width: int, height: int) -> None:
        # Center both boards horizontally & vertically as a stacked group
        center_x = (width - self.GRID_WIDTH) // 2
        total_stack_h = 2 * self.GRID_HEIGHT + self.INTER_GRID_PADDING
        top_offset_y = max(0, (height - total_stack_h) // 2)
        bottom_offset_y = top_offset_y + self.GRID_HEIGHT + self.INTER_GRID_PADDING

        # Apply offsets to TOP board
        step_x = self.cell_size + self.DIVIDER
        step_y = self.cell_size + self.DIVIDER
        for row in self.top_buttons:
            for button in row:
                r, c = button.index
                button.rect.x = c * step_x + center_x
                button.rect.y = r * step_y + top_offset_y

        # Apply offsets to BOTTOM board 
        for row in self.bottom_buttons:
            for button in row:
                r, c = button.index
                button.rect.x = c * step_x + center_x
                button.rect.y = r * step_y + bottom_offset_y

    # Handle user resizing the window.
    def handle_resize(self, width: int, height: int) -> None:
        width = max(int(width), int(self._min_width))
        height = max(int(height), int(self._min_height))
        self.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self._apply_window_size(width, height)

    # Return ("top", (r,c)) or None (bottom board is read-only / non-interactive)
    def _hovered_button(self, pos: tuple[int, int]):
        for row in self.top_buttons:
            for button in row:
                if button.rect.collidepoint(pos):
                    return ("top", button.index)
        return None

    # Darken the hovered cell 
    def _draw_hover_overlay(self, rect: pygame.Rect, alpha: int = 55) -> None:
        if rect.width <= 0 or rect.height <= 0:
            return
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, max(0, min(255, int(alpha)))))
        self.window.blit(overlay, rect.topleft)

    def show_toast(self, text: str, duration_ms: int = 1000, color: tuple[int, int, int] = (60, 220, 90)) -> None:
        self._toast_text = text
        self._toast_color = color
        self._toast_until_ms = pygame.time.get_ticks() + max(0, int(duration_ms))

    # checks for events, button down or close-game.
    def process_events(self) -> dict:
        events = uc.process_top_click_events(self.top_buttons)
        events["hover"] = self._hovered_button(pygame.mouse.get_pos())
        return events

    # draw both boards according to their 2d lists and update the window.
    def draw(self, top_matrix: list, bottom_matrix: list) -> None:
        self.clock.tick(15)
        hover = self._hovered_button(pygame.mouse.get_pos())
        if self._bg_tile is not None:
            tw, th = self._bg_tile.get_size()
            ww, wh = self.window.get_size()
            # Tile the image across the whole window
            for y in range(0, wh, th):
                for x in range(0, ww, tw):
                    self.window.blit(self._bg_tile, (x, y))
        else:
            self.window.fill(uc.OCEAN_BLUE)
        # Pelican icons (Enemy/You)
        #   x = A * sin(wt)
        #   y = A * sin(wt) * cos(wt) = (A/2) * sin(2wt)
        t = pygame.time.get_ticks() / 1000.0
        w = 2 * math.pi * self._icon_speed
        dx = int(self._icon_amp * math.sin(w * t))
        dy = int((self._icon_amp / 2) * math.sin(2 * w * t))
        edge_pad = 0
        if self._enemy_icon is not None:
            self.window.blit(self._enemy_icon, (edge_pad + dx, edge_pad + dy))
        if self._you_icon is not None:
            ww, wh = self.window.get_size()
            self.window.blit(self._you_icon, (ww - self._you_icon.get_width() - edge_pad - dx,
                                              wh - self._you_icon.get_height() - edge_pad - dy))

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
                if hover == ("top", button.index):
                    self._draw_hover_overlay(button.rect)

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

        # Toast overlay "YOUR TURN"
        now_ms = pygame.time.get_ticks()
        if self._toast_text and now_ms < self._toast_until_ms:
            label = self._toast_font.render(self._toast_text, True, self._toast_color)
            padding_x, padding_y = 18, 10
            rect = label.get_rect()
            rect.centerx = self.window.get_width() // 2
            rect.top = 12

            bg = pygame.Surface((rect.width + padding_x * 2, rect.height + padding_y * 2), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            bg_rect = bg.get_rect()
            bg_rect.centerx = rect.centerx
            bg_rect.centery = rect.centery
            self.window.blit(bg, bg_rect.topleft)
            self.window.blit(label, rect.topleft)
        elif self._toast_text and now_ms >= self._toast_until_ms:
            self._toast_text = None

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

