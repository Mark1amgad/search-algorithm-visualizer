"""Main entry point and application loop for the Search Algorithm Visualizer."""

import sys
import pygame
from enum import Enum, auto

from search_visualizer.grid import Grid
from search_visualizer.algorithms import (
    AlgorithmState, ALGORITHMS, run_algorithm_to_completion,
)
from search_visualizer.renderer import GridRenderer, Colors
from search_visualizer.ui import SidebarPanel, TheoryOverlay
from search_visualizer.theory import ALGORITHM_LIST

# ============================================================
# Configuration
# ============================================================
WINDOW_WIDTH  = 1300
WINDOW_HEIGHT = 730
FPS           = 60

GRID_ROWS     = 25
GRID_COLS     = 40
CELL_SIZE     = 24
GRID_OFFSET_X = 20
GRID_OFFSET_Y = 60

SIDEBAR_X     = 1045
SIDEBAR_W     = WINDOW_WIDTH - SIDEBAR_X

DLS_DEPTH     = 15
ANIM_EVENT    = pygame.USEREVENT + 1
WINDOW_TITLE  = "Search Algorithm Visualizer"


# ============================================================
# App State
# ============================================================
class AppState(Enum):
    IDLE      = auto()
    RUNNING   = auto()
    PAUSED    = auto()
    FINISHED  = auto()
    NOT_FOUND = auto()
    COMPARING = auto()


# ============================================================
# Application
# ============================================================
class App:
    """Main application class — owns the loop, events, and state machine."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock  = pygame.time.Clock()

        # Core data
        self.grid       = Grid(rows=GRID_ROWS, cols=GRID_COLS)
        self.algo_state = AlgorithmState()
        self.generator  = None
        self.app_state  = AppState.IDLE

        # Renderers
        self.grid_renderer = GridRenderer(
            self.grid,
            cell_size=CELL_SIZE,
            offset_x=GRID_OFFSET_X,
            offset_y=GRID_OFFSET_Y,
        )
        self.sidebar        = SidebarPanel(x=SIDEBAR_X, y=0,
                                           width=SIDEBAR_W, height=WINDOW_HEIGHT)
        self.theory_overlay = TheoryOverlay(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Mouse / drag state
        self.mouse_drawing  = False
        self.mouse_erasing  = False
        self.last_drag_cell = None
        self.drag_start_key = False   # S held → drag start
        self.drag_goal_key  = False   # G held → drag goal

        self._set_anim_timer()

    # ----------------------------------------------------------
    # Timer helpers
    # ----------------------------------------------------------
    def _set_anim_timer(self):
        pygame.time.set_timer(ANIM_EVENT, self.sidebar.speed_ms)

    def _stop_anim_timer(self):
        pygame.time.set_timer(ANIM_EVENT, 0)

    # ----------------------------------------------------------
    # Algorithm lifecycle
    # ----------------------------------------------------------
    def _start_algorithm(self):
        self.algo_state = AlgorithmState()
        name    = self.sidebar.selected_algo_name
        algo_fn = ALGORITHMS[name]

        if name == "DLS":
            self.generator = algo_fn(
                self.grid, self.grid.start, self.grid.goal,
                self.algo_state, max_depth=DLS_DEPTH,
            )
        else:
            self.generator = algo_fn(
                self.grid, self.grid.start, self.grid.goal,
                self.algo_state,
            )

        self.app_state = AppState.RUNNING
        self._set_anim_timer()

    def _advance_one_step(self):
        """Called on every animation timer tick."""
        if self.generator is None or self.app_state != AppState.RUNNING:
            return
        try:
            next(self.generator)
            if self.algo_state.finished:
                self._stop_anim_timer()
                self.app_state = (
                    AppState.FINISHED if self.algo_state.found else AppState.NOT_FOUND
                )
        except StopIteration:
            self._stop_anim_timer()
            self.app_state = (
                AppState.FINISHED if self.algo_state.found else AppState.NOT_FOUND
            )

    def _run_pause(self):
        if self.app_state == AppState.IDLE:
            self._start_algorithm()
        elif self.app_state == AppState.RUNNING:
            self.app_state = AppState.PAUSED
            self._stop_anim_timer()
        elif self.app_state == AppState.PAUSED:
            self.app_state = AppState.RUNNING
            self._set_anim_timer()
        elif self.app_state in (AppState.FINISHED, AppState.NOT_FOUND):
            self._clear_path()
            self._start_algorithm()

    def _reset(self):
        self._stop_anim_timer()
        self.grid.reset()
        self.algo_state = AlgorithmState()
        self.generator  = None
        self.app_state  = AppState.IDLE
        self.sidebar.comparison_results = []

    def _clear_path(self):
        self._stop_anim_timer()
        self.algo_state = AlgorithmState()
        self.generator  = None
        self.app_state  = AppState.IDLE

    def _quit(self):
        """Graceful shutdown — stops timer, quits pygame cleanly."""
        self._stop_anim_timer()
        pygame.quit()
        sys.exit()

    def _run_compare(self):
        self._clear_path()
        self.app_state = AppState.COMPARING
        # Render a "comparing…" frame so the user sees feedback
        self._render_frame()
        pygame.display.flip()

        results = []
        for name in ALGORITHM_LIST:
            r = run_algorithm_to_completion(
                name, self.grid, self.grid.start, self.grid.goal,
                dls_depth=DLS_DEPTH,
            )
            results.append(r)

        self.sidebar.comparison_results = results
        self.app_state = AppState.IDLE

    # ----------------------------------------------------------
    # Action dispatcher (from sidebar clicks or keys)
    # ----------------------------------------------------------
    def _handle_action(self, action):
        if action is None:
            return

        if action.startswith("select_algo:"):
            idx = int(action.split(":")[1])
            self.sidebar.select_algorithm(idx)
            if self.app_state not in (AppState.IDLE,):
                self._clear_path()

        elif action == "run_pause":     self._run_pause()
        elif action == "reset":         self._reset()
        elif action == "clear_path":    self._clear_path()
        elif action == "maze_random":
            self._reset()
            self.grid.generate_random_maze()
        elif action == "maze_perfect":
            self._reset()
            self.grid.generate_recursive_maze()
        elif action == "compare":       self._run_compare()
        elif action == "speed_change":  self._set_anim_timer()
        elif action == "theory_toggle": pass  # sidebar already toggled flag
        elif action == "exit":          self._quit()

    # ----------------------------------------------------------
    # Keyboard
    # ----------------------------------------------------------
    def _handle_keydown(self, event):
        key = event.key

        # Algorithm select 1–7
        if pygame.K_1 <= key <= pygame.K_7:
            idx = key - pygame.K_1
            self.sidebar.select_algorithm(idx)
            if self.app_state not in (AppState.IDLE,):
                self._clear_path()
            return

        if key == pygame.K_SPACE:   self._run_pause()
        elif key == pygame.K_r:     self._reset()
        elif key == pygame.K_c:     self._clear_path()
        elif key == pygame.K_m:
            self._reset(); self.grid.generate_random_maze()
        elif key == pygame.K_p:
            self._reset(); self.grid.generate_recursive_maze()
        elif key == pygame.K_f:     self._run_compare()
        elif key == pygame.K_t:
            self.sidebar.theory_visible = not self.sidebar.theory_visible
        elif key == pygame.K_ESCAPE:
            self.sidebar.theory_visible = False
        elif key == pygame.K_q:     self._quit()
        elif key == pygame.K_s:
            self.drag_start_key = True
        elif key == pygame.K_g:
            self.drag_goal_key  = True

    def _handle_keyup(self, event):
        if event.key == pygame.K_s:
            self.drag_start_key = False
        if event.key == pygame.K_g:
            self.drag_goal_key  = False

    # ----------------------------------------------------------
    # Mouse on grid
    # ----------------------------------------------------------
    def _grid_click(self, pos, button):
        """Handle a click or drag-step on the grid area."""
        cell = self.grid_renderer.pixel_to_grid(*pos)
        if cell is None:
            return

        # Move start / goal if modifier key held
        if self.drag_start_key:
            if cell != self.grid.goal:
                self.grid.set_start(*cell)
            return
        if self.drag_goal_key:
            if cell != self.grid.start:
                self.grid.set_goal(*cell)
            return

        # Skip repeat cell during drag
        if cell == self.last_drag_cell:
            return
        self.last_drag_cell = cell

        # Ignore start/goal
        if cell in (self.grid.start, self.grid.goal):
            return

        if button == 1:
            self.grid.set_wall(*cell)
        elif button == 3:
            self.grid.set_empty(*cell)

    # ----------------------------------------------------------
    # Event loop
    # ----------------------------------------------------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()

            elif event.type == ANIM_EVENT:
                self._advance_one_step()

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if pos[0] < SIDEBAR_X:
                    # Grid interaction
                    if event.button == 1:
                        self.mouse_drawing = True
                    elif event.button == 3:
                        self.mouse_erasing = True
                    self.last_drag_cell = None
                    self._grid_click(pos, event.button)
                else:
                    action = self.sidebar.handle_click(pos)
                    self._handle_action(action)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_drawing  = False
                self.mouse_erasing  = False
                self.last_drag_cell = None

            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_drawing and event.pos[0] < SIDEBAR_X:
                    self._grid_click(event.pos, 1)
                elif self.mouse_erasing and event.pos[0] < SIDEBAR_X:
                    self._grid_click(event.pos, 3)
                # Drag start/goal while key held
                elif (self.drag_start_key or self.drag_goal_key) and event.pos[0] < SIDEBAR_X:
                    self._grid_click(event.pos, 1)

    # ----------------------------------------------------------
    # Rendering
    # ----------------------------------------------------------
    def _app_state_label(self):
        labels = {
            AppState.IDLE:      "IDLE",
            AppState.RUNNING:   "RUNNING",
            AppState.PAUSED:    "PAUSED",
            AppState.FINISHED:  "FINISHED",
            AppState.NOT_FOUND: "NOT_FOUND",
            AppState.COMPARING: "COMPARING",
        }
        return labels.get(self.app_state, "IDLE")

    def _render_frame(self):
        self.screen.fill(Colors.WINDOW_BG)

        # Grid — pass algo_state for all non-idle states so metrics stay visible
        show_state = self.algo_state if self.app_state != AppState.IDLE else None
        self.grid_renderer.draw(self.screen, show_state)

        # Status banner on grid after algorithm finishes
        if self.app_state in (AppState.FINISHED, AppState.NOT_FOUND):
            self._draw_status_banner()

        # Header
        self.grid_renderer.draw_header(self.screen, self.sidebar.selected_algo_name)

        # Legend
        legend_y = GRID_OFFSET_Y + self.grid_renderer.grid_pixel_height + 8
        self.grid_renderer.draw_legend(self.screen, GRID_OFFSET_X, legend_y)

        # Keyboard reference (two rows below legend)
        self._draw_key_reference(legend_y + 22)

        # Sidebar
        self.sidebar.draw(
            self.screen,
            algo_state=show_state,
            app_state_name=self._app_state_label(),
        )

        # Theory overlay (on top of everything)
        if self.sidebar.theory_visible:
            self.theory_overlay.draw(self.screen, self.sidebar.selected_algo_name)

    def _draw_status_banner(self):
        """Draw a small result banner centred on the grid area."""
        found = self.algo_state.found
        label = "PATH FOUND" if found else "NO PATH FOUND"
        color  = Colors.STATUS_FOUND if found else Colors.STATUS_NOT_FOUND
        sub    = f"{len(self.algo_state.path)} steps  |  {self.algo_state.nodes_explored} nodes explored" if found else "Try a different algorithm or clear the walls (R)"

        grid_cx = GRID_OFFSET_X + self.grid_renderer.grid_pixel_width  // 2
        banner_y = GRID_OFFSET_Y + self.grid_renderer.grid_pixel_height // 2 - 20

        f_big = pygame.font.SysFont("Arial", 28, bold=True)
        f_sub = pygame.font.SysFont("Arial", 13)

        # Shadow / background pill
        big_surf = f_big.render(label, True, color)
        sub_surf = f_sub.render(sub,   True, Colors.TEXT_SECONDARY)
        pw = max(big_surf.get_width(), sub_surf.get_width()) + 32
        ph = big_surf.get_height() + sub_surf.get_height() + 18
        pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pill.fill((20, 20, 35, 210))
        self.screen.blit(pill, (grid_cx - pw // 2, banner_y))
        pygame.draw.rect(self.screen, color,
                         (grid_cx - pw // 2, banner_y, pw, ph), 2, border_radius=6)

        self.screen.blit(big_surf, (grid_cx - big_surf.get_width() // 2, banner_y + 8))
        self.screen.blit(sub_surf, (grid_cx - sub_surf.get_width() // 2,
                                    banner_y + 10 + big_surf.get_height()))

    def _draw_key_reference(self, y):
        """Draw keyboard shortcuts in two compact rows below the legend."""
        font = pygame.font.SysFont("Arial", 11)
        row1 = ["SPACE:Run/Pause", "R:Reset", "C:Clear", "M:RandMaze", "P:PerfMaze"]
        row2 = ["F:Compare", "T:Theory", "Q:Quit", "1-7:Algo", "S+drag:Start", "G+drag:Goal"]

        for row_idx, row in enumerate([row1, row2]):
            x = GRID_OFFSET_X
            ry = y + row_idx * 14
            for sc in row:
                key, desc = sc.split(":", 1)
                k_surf = font.render(key, True, Colors.BUTTON_ACTIVE)
                d_surf = font.render(f":{desc}  ", True, Colors.TEXT_DIM)
                self.screen.blit(k_surf, (x, ry))
                self.screen.blit(d_surf, (x + k_surf.get_width(), ry))
                x += k_surf.get_width() + d_surf.get_width()
                if x > SIDEBAR_X - 10:
                    break

    # ----------------------------------------------------------
    # Main loop
    # ----------------------------------------------------------
    def run(self):
        while True:
            self._handle_events()
            self._render_frame()
            pygame.display.flip()
            self.clock.tick(FPS)


# ============================================================
# Entry point
# ============================================================
def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
