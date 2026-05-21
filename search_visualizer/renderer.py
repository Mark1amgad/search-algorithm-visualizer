"""Pygame rendering engine for the search algorithm visualizer."""

import pygame

# ============================================================
# Color Scheme - Professional dark theme
# ============================================================
class Colors:
    # Background
    WINDOW_BG = (30, 30, 46)
    SIDEBAR_BG = (45, 45, 65)
    SIDEBAR_BORDER = (60, 60, 90)

    # Grid cells
    CELL_EMPTY = (69, 71, 90)
    CELL_WALL = (100, 100, 130)
    CELL_GRID_LINE = (55, 55, 75)

    # Algorithm visualization
    CELL_VISITED = (68, 138, 201)       # Blue
    CELL_FRONTIER = (241, 196, 83)      # Yellow/amber
    CELL_CURRENT = (0, 206, 209)        # Cyan
    CELL_PATH = (129, 199, 132)         # Green

    # Special cells
    CELL_START = (102, 187, 106)        # Green
    CELL_GOAL = (239, 83, 80)           # Red
    CELL_START_BORDER = (56, 142, 60)
    CELL_GOAL_BORDER = (198, 40, 40)

    # Text
    TEXT_PRIMARY = (224, 224, 224)
    TEXT_SECONDARY = (160, 160, 180)
    TEXT_ACCENT = (129, 199, 132)
    TEXT_DIM = (100, 100, 120)

    # UI elements
    BUTTON_BG = (60, 60, 85)
    BUTTON_HOVER = (75, 75, 105)
    BUTTON_ACTIVE = (100, 181, 246)
    BUTTON_TEXT = (224, 224, 224)
    BUTTON_TEXT_ACTIVE = (30, 30, 46)

    # Metrics
    METRIC_BG = (38, 38, 55)
    METRIC_LABEL = (160, 160, 180)
    METRIC_VALUE = (224, 224, 224)
    METRIC_HIGHLIGHT = (100, 181, 246)

    # Status
    STATUS_RUNNING = (241, 196, 83)
    STATUS_FOUND = (102, 187, 106)
    STATUS_NOT_FOUND = (239, 83, 80)
    STATUS_IDLE = (160, 160, 180)


# ============================================================
# Grid Renderer
# ============================================================
class GridRenderer:
    """Renders the search grid and algorithm visualization state."""

    def __init__(self, grid, cell_size=24, offset_x=20, offset_y=60):
        self.grid = grid
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.gap = 1  # Gap between cells

    @property
    def grid_pixel_width(self):
        return self.grid.cols * (self.cell_size + self.gap)

    @property
    def grid_pixel_height(self):
        return self.grid.rows * (self.cell_size + self.gap)

    def pixel_to_grid(self, px, py):
        """Convert pixel coordinates to grid (row, col). Returns None if out of bounds."""
        col = (px - self.offset_x) // (self.cell_size + self.gap)
        row = (py - self.offset_y) // (self.cell_size + self.gap)
        if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
            # Check if within cell bounds (not in gap)
            cell_x = self.offset_x + col * (self.cell_size + self.gap)
            cell_y = self.offset_y + row * (self.cell_size + self.gap)
            if cell_x <= px < cell_x + self.cell_size and cell_y <= py < cell_y + self.cell_size:
                return (row, col)
        return None

    def draw(self, surface, state=None):
        """Draw the grid with optional algorithm state overlay."""
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                x = self.offset_x + col * (self.cell_size + self.gap)
                y = self.offset_y + row * (self.cell_size + self.gap)
                pos = (row, col)

                # Determine cell color (priority: current > path > start/goal > frontier > visited > wall > empty)
                color = self._get_cell_color(pos, state)

                pygame.draw.rect(surface, color, (x, y, self.cell_size, self.cell_size))

                # Draw special markers for start and goal
                if pos == self.grid.start:
                    self._draw_marker(surface, x, y, "S", Colors.CELL_START_BORDER)
                elif pos == self.grid.goal:
                    self._draw_marker(surface, x, y, "G", Colors.CELL_GOAL_BORDER)

    def _get_cell_color(self, pos, state):
        """Determine cell color based on grid state and algorithm state."""
        row, col = pos

        # Current node (highest priority)
        if state and state.current == pos and not state.finished:
            return Colors.CELL_CURRENT

        # Path
        if state and pos in state.path:
            return Colors.CELL_PATH

        # Start and Goal (show before visited overlay)
        if pos == self.grid.start:
            return Colors.CELL_START
        if pos == self.grid.goal:
            return Colors.CELL_GOAL

        # Frontier
        if state and pos in state.frontier:
            return Colors.CELL_FRONTIER

        # Visited
        if state and pos in state.visited:
            return Colors.CELL_VISITED

        # Wall
        if self.grid.is_wall(row, col):
            return Colors.CELL_WALL

        # Empty
        return Colors.CELL_EMPTY

    def _draw_marker(self, surface, x, y, letter, border_color):
        """Draw a letter marker on a cell."""
        font = pygame.font.SysFont("Arial", max(10, self.cell_size - 8), bold=True)
        text = font.render(letter, True, border_color)
        text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
        surface.blit(text, text_rect)

    def draw_header(self, surface, algorithm_name):
        """Draw the header bar above the grid."""
        font = pygame.font.SysFont("Arial", 22, bold=True)
        title = font.render("Search Algorithm Visualizer", True, Colors.TEXT_PRIMARY)
        surface.blit(title, (self.offset_x, 15))

        font_small = pygame.font.SysFont("Arial", 16)
        algo_text = font_small.render(f"Selected: {algorithm_name}", True, Colors.TEXT_ACCENT)
        surface.blit(algo_text, (self.offset_x + 380, 20))

    def draw_legend(self, surface, x, y):
        """Draw a compact color legend."""
        font = pygame.font.SysFont("Arial", 12)
        items = [
            (Colors.CELL_START, "Start"),
            (Colors.CELL_GOAL, "Goal"),
            (Colors.CELL_VISITED, "Visited"),
            (Colors.CELL_FRONTIER, "Frontier"),
            (Colors.CELL_CURRENT, "Current"),
            (Colors.CELL_PATH, "Path"),
            (Colors.CELL_WALL, "Wall"),
        ]
        cx = x
        for color, label in items:
            pygame.draw.rect(surface, color, (cx, y, 12, 12))
            text = font.render(label, True, Colors.TEXT_SECONDARY)
            surface.blit(text, (cx + 16, y - 1))
            cx += 16 + text.get_width() + 12
