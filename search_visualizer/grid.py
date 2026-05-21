"""Grid data structure and maze generation for the search algorithm visualizer."""

import random
from enum import IntEnum


class CellType(IntEnum):
    EMPTY = 0
    WALL = 1


class Grid:
    """2D grid for pathfinding visualization."""

    def __init__(self, rows=25, cols=40):
        self.rows = rows
        self.cols = cols
        self.cells = [[CellType.EMPTY] * cols for _ in range(rows)]
        self.start = (1, 1)
        self.goal = (rows - 2, cols - 2)

    def reset(self):
        """Reset all cells to empty, keep start and goal."""
        self.cells = [[CellType.EMPTY] * self.cols for _ in range(self.rows)]

    def clear_path(self):
        """Reset only walls to empty (for re-running algorithms)."""
        pass  # Walls stay; algorithm visual state is managed separately

    def is_valid(self, row, col):
        """Check if position is within grid bounds."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_wall(self, row, col):
        """Check if position is a wall."""
        if not self.is_valid(row, col):
            return True
        return self.cells[row][col] == CellType.WALL

    def toggle_wall(self, row, col):
        """Toggle wall at position (if not start/goal)."""
        if not self.is_valid(row, col):
            return
        if (row, col) == self.start or (row, col) == self.goal:
            return
        if self.cells[row][col] == CellType.WALL:
            self.cells[row][col] = CellType.EMPTY
        else:
            self.cells[row][col] = CellType.WALL

    def set_wall(self, row, col):
        """Set cell as wall."""
        if self.is_valid(row, col) and (row, col) != self.start and (row, col) != self.goal:
            self.cells[row][col] = CellType.WALL

    def set_empty(self, row, col):
        """Set cell as empty."""
        if self.is_valid(row, col):
            self.cells[row][col] = CellType.EMPTY

    def set_start(self, row, col):
        """Set start position."""
        if self.is_valid(row, col) and not self.is_wall(row, col):
            self.start = (row, col)

    def set_goal(self, row, col):
        """Set goal position."""
        if self.is_valid(row, col) and not self.is_wall(row, col):
            self.goal = (row, col)

    def get_neighbors(self, pos):
        """Get valid non-wall neighbors (4-directional)."""
        row, col = pos
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.is_valid(nr, nc) and not self.is_wall(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    def generate_random_maze(self, wall_density=0.3):
        """Generate random obstacles with guaranteed path potential."""
        self.reset()
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) == self.start or (r, c) == self.goal:
                    continue
                if random.random() < wall_density:
                    self.cells[r][c] = CellType.WALL
        # Ensure start and goal are not blocked
        self.cells[self.start[0]][self.start[1]] = CellType.EMPTY
        self.cells[self.goal[0]][self.goal[1]] = CellType.EMPTY
        # Clear area around start and goal
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            sr, sc = self.start[0] + dr, self.start[1] + dc
            if self.is_valid(sr, sc):
                self.cells[sr][sc] = CellType.EMPTY
            gr, gc = self.goal[0] + dr, self.goal[1] + dc
            if self.is_valid(gr, gc):
                self.cells[gr][gc] = CellType.EMPTY

    def generate_recursive_maze(self):
        """Generate a proper maze using recursive backtracker."""
        self.reset()
        # Fill everything with walls
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c] = CellType.WALL

        # Carve passages using recursive backtracker
        # Only visit odd-numbered cells
        def carve(r, c):
            self.cells[r][c] = CellType.EMPTY
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if (0 < nr < self.rows - 1 and 0 < nc < self.cols - 1
                        and self.cells[nr][nc] == CellType.WALL):
                    # Remove wall between current and neighbor
                    self.cells[r + dr // 2][c + dc // 2] = CellType.EMPTY
                    carve(nr, nc)

        # Start carving from (1,1)
        carve(1, 1)

        # Ensure start and goal are accessible
        sr, sc = self.start
        gr, gc = self.goal
        self.cells[sr][sc] = CellType.EMPTY
        self.cells[gr][gc] = CellType.EMPTY
        # Open neighbors of start/goal if needed
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = sr + dr, sc + dc
            if self.is_valid(nr, nc):
                self.cells[nr][nc] = CellType.EMPTY
            nr, nc = gr + dr, gc + dc
            if self.is_valid(nr, nc):
                self.cells[nr][nc] = CellType.EMPTY
