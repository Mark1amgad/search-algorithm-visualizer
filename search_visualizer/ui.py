"""Sidebar UI panel, buttons, metrics, and theory overlay for the visualizer."""

import pygame
from .renderer import Colors
from .theory import ALGORITHM_INFO, ALGORITHM_LIST


# ============================================================
# Button
# ============================================================
class Button:
    """A clickable button with optional keyboard hint label."""

    def __init__(self, rect, label, key_hint=None, active=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.key_hint = key_hint
        self.active = active

    def draw(self, surface, hover=False):
        if self.active:
            bg = Colors.BUTTON_ACTIVE
            text_color = Colors.BUTTON_TEXT_ACTIVE
        elif hover:
            bg = Colors.BUTTON_HOVER
            text_color = Colors.TEXT_PRIMARY
        else:
            bg = Colors.BUTTON_BG
            text_color = Colors.BUTTON_TEXT

        pygame.draw.rect(surface, bg, self.rect, border_radius=5)
        pygame.draw.rect(surface, Colors.SIDEBAR_BORDER, self.rect, 1, border_radius=5)

        font = pygame.font.SysFont("Arial", 13, bold=bool(self.active))
        text_surf = font.render(self.label, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)

        if self.key_hint:
            hint_font = pygame.font.SysFont("Arial", 10)
            hint_color = Colors.BUTTON_TEXT_ACTIVE if self.active else Colors.TEXT_DIM
            hint_surf = hint_font.render(self.key_hint, True, hint_color)
            surface.blit(hint_surf, (self.rect.x + 6, self.rect.centery - hint_surf.get_height() // 2))
            text_rect.centerx = self.rect.centerx + 8

        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ============================================================
# Sidebar Panel
# ============================================================
class SidebarPanel:
    """Full sidebar: algorithm selection, speed, actions, metrics, comparison, theory."""

    ALGO_NAMES = ALGORITHM_LIST  # ["BFS","DFS","DLS","IDS","UCS","Greedy","A*"]
    SPEED_LEVELS = [500, 200, 100, 60, 40, 25, 15, 10, 5, 1]  # ms per animation step

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected_algo_idx = 0
        self.speed_idx = 4          # default: 40 ms (medium)
        self.theory_visible = False
        self.comparison_results = []
        self._build_layout()

    # ----------------------------------------------------------
    # Layout construction
    # ----------------------------------------------------------
    def _build_layout(self):
        x = self.x + 8
        w = self.width - 16
        cy = 54  # running cursor y

        # ---- Algorithm buttons ----
        self.algo_buttons = []
        for i, name in enumerate(self.ALGO_NAMES):
            btn = Button(
                rect=(x, cy, w, 28),
                label=name,
                key_hint=str(i + 1),
                active=(i == self.selected_algo_idx),
            )
            self.algo_buttons.append(btn)
            cy += 32

        cy += 10

        # ---- Speed bar ----
        self._speed_section_y = cy
        self._speed_bar_x = x + 38
        self._speed_bar_w = w - 76
        self.btn_spd_down = Button(rect=(x, cy, 34, 26), label="◀")
        self.btn_spd_up   = Button(rect=(x + w - 34, cy, 34, 26), label="▶")
        cy += 40

        # ---- Action buttons ----
        cy += 4
        self._controls_y = cy
        self.btn_run         = Button(rect=(x, cy, w, 30), label="Run / Pause",  key_hint="SPC")
        cy += 34
        self.btn_reset       = Button(rect=(x, cy, w, 28), label="Reset",        key_hint="R")
        cy += 32
        self.btn_clear       = Button(rect=(x, cy, w, 28), label="Clear Path",   key_hint="C")
        cy += 32
        self.btn_maze_rand   = Button(rect=(x, cy, w, 28), label="Random Maze",  key_hint="M")
        cy += 32
        self.btn_maze_perf   = Button(rect=(x, cy, w, 28), label="Perfect Maze", key_hint="P")
        cy += 32
        self.btn_compare     = Button(rect=(x, cy, w, 28), label="Compare All",  key_hint="F")
        cy += 32
        self.btn_theory      = Button(rect=(x, cy, w, 28), label="Theory",       key_hint="T")
        cy += 36

        # ---- Exit button ----
        self.btn_exit        = Button(rect=(x, cy, w, 26), label="Exit",          key_hint="Q")
        cy += 34

        # ---- Metrics section ----
        self._metrics_y = cy

        # ---- All interactive buttons (for hover) ----
        self._all_buttons = (
            self.algo_buttons
            + [self.btn_spd_down, self.btn_spd_up,
               self.btn_run, self.btn_reset, self.btn_clear,
               self.btn_maze_rand, self.btn_maze_perf,
               self.btn_compare, self.btn_theory, self.btn_exit]
        )

    # ----------------------------------------------------------
    # Properties
    # ----------------------------------------------------------
    @property
    def selected_algo_name(self):
        return self.ALGO_NAMES[self.selected_algo_idx]

    @property
    def speed_ms(self):
        return self.SPEED_LEVELS[self.speed_idx]

    # ----------------------------------------------------------
    # Public mutators
    # ----------------------------------------------------------
    def select_algorithm(self, idx):
        self.selected_algo_idx = idx
        for i, btn in enumerate(self.algo_buttons):
            btn.active = (i == idx)

    def increase_speed(self):
        self.speed_idx = min(self.speed_idx + 1, len(self.SPEED_LEVELS) - 1)

    def decrease_speed(self):
        self.speed_idx = max(self.speed_idx - 1, 0)

    # ----------------------------------------------------------
    # Input
    # ----------------------------------------------------------
    def handle_click(self, pos):
        """Process a click on the sidebar. Returns an action string or None."""
        for i, btn in enumerate(self.algo_buttons):
            if btn.is_clicked(pos):
                self.select_algorithm(i)
                return f"select_algo:{i}"

        if self.btn_spd_down.is_clicked(pos):
            self.decrease_speed()
            return "speed_change"
        if self.btn_spd_up.is_clicked(pos):
            self.increase_speed()
            return "speed_change"

        if self.btn_run.is_clicked(pos):     return "run_pause"
        if self.btn_reset.is_clicked(pos):   return "reset"
        if self.btn_clear.is_clicked(pos):   return "clear_path"
        if self.btn_maze_rand.is_clicked(pos):  return "maze_random"
        if self.btn_maze_perf.is_clicked(pos):  return "maze_perfect"
        if self.btn_compare.is_clicked(pos): return "compare"

        if self.btn_theory.is_clicked(pos):
            self.theory_visible = not self.theory_visible
            return "theory_toggle"

        if self.btn_exit.is_clicked(pos):
            return "exit"

        return None

    # ----------------------------------------------------------
    # Drawing
    # ----------------------------------------------------------
    def draw(self, surface, algo_state=None, app_state_name="IDLE"):
        mouse = pygame.mouse.get_pos()

        # Background + left border
        pygame.draw.rect(surface, Colors.SIDEBAR_BG,
                         (self.x, self.y, self.width, self.height))
        pygame.draw.line(surface, Colors.SIDEBAR_BORDER,
                         (self.x, 0), (self.x, self.height), 2)

        # Title
        self._draw_section_header(surface, "ALGORITHM", self.x + 8, 36)

        # Algorithm buttons
        for btn in self.algo_buttons:
            btn.draw(surface, hover=btn.is_clicked(mouse))

        # Speed
        self._draw_section_header(surface, "SPEED", self.x + 8, self._speed_section_y - 18)
        self.btn_spd_down.draw(surface, hover=self.btn_spd_down.is_clicked(mouse))
        self.btn_spd_up.draw(surface, hover=self.btn_spd_up.is_clicked(mouse))
        self._draw_speed_bar(surface)

        # Controls
        self._draw_section_header(surface, "CONTROLS", self.x + 8, self._controls_y - 18)
        self.btn_run.draw(surface, hover=self.btn_run.is_clicked(mouse))
        self.btn_reset.draw(surface, hover=self.btn_reset.is_clicked(mouse))
        self.btn_clear.draw(surface, hover=self.btn_clear.is_clicked(mouse))
        self.btn_maze_rand.draw(surface, hover=self.btn_maze_rand.is_clicked(mouse))
        self.btn_maze_perf.draw(surface, hover=self.btn_maze_perf.is_clicked(mouse))
        self.btn_compare.draw(surface, hover=self.btn_compare.is_clicked(mouse))
        self.btn_theory.draw(surface, hover=self.btn_theory.is_clicked(mouse))

        # Exit (separator line above)
        pygame.draw.line(surface, Colors.SIDEBAR_BORDER,
                         (self.x + 8, self.btn_exit.rect.y - 6),
                         (self.x + self.width - 8, self.btn_exit.rect.y - 6), 1)
        self.btn_exit.draw(surface, hover=self.btn_exit.is_clicked(mouse))

        # Metrics
        self._draw_metrics(surface, algo_state, app_state_name, self._metrics_y)

        # Comparison results
        if self.comparison_results:
            comp_y = self._metrics_y + 158
            self._draw_comparison(surface, comp_y)

    def _draw_section_header(self, surface, text, x, y):
        font = pygame.font.SysFont("Arial", 10, bold=True)
        surf = font.render(text, True, Colors.TEXT_DIM)
        surface.blit(surf, (x, y))
        pygame.draw.line(surface, Colors.SIDEBAR_BORDER,
                         (x, y + 13), (self.x + self.width - 8, y + 13), 1)

    def _draw_speed_bar(self, surface):
        bx = self._speed_bar_x
        bw = self._speed_bar_w
        by = self._speed_section_y
        bh = 26
        total = len(self.SPEED_LEVELS)
        seg = bw // total

        for i in range(total):
            sx = bx + i * seg
            color = Colors.BUTTON_ACTIVE if i <= self.speed_idx else Colors.BUTTON_BG
            pygame.draw.rect(surface, color, (sx + 1, by + 5, seg - 2, bh - 10), border_radius=2)

        font = pygame.font.SysFont("Arial", 10)
        lbl = f"{self.SPEED_LEVELS[self.speed_idx]} ms/step"
        s = font.render(lbl, True, Colors.TEXT_SECONDARY)
        surface.blit(s, (bx + bw // 2 - s.get_width() // 2, by + bh + 1))

    def _draw_metrics(self, surface, state, app_state_name, y):
        self._draw_section_header(surface, "LIVE METRICS", self.x + 8, y)
        y += 18

        status_palette = {
            "IDLE":      Colors.STATUS_IDLE,
            "RUNNING":   Colors.STATUS_RUNNING,
            "PAUSED":    Colors.STATUS_RUNNING,
            "FINISHED":  Colors.STATUS_FOUND,
            "NOT_FOUND": Colors.STATUS_NOT_FOUND,
            "COMPARING": Colors.STATUS_RUNNING,
        }
        status_color = status_palette.get(app_state_name, Colors.STATUS_IDLE)

        box = pygame.Rect(self.x + 8, y, self.width - 16, 128)
        pygame.draw.rect(surface, Colors.METRIC_BG, box, border_radius=4)

        rows = [
            ("Algorithm",     self.selected_algo_name),
            ("Status",        app_state_name),
            ("Explored",      str(state.nodes_explored) if state else "—"),
            ("Path Length",   str(len(state.path))      if (state and state.path) else "—"),
            ("Time",          f"{state.elapsed_ms:.1f} ms" if state else "—"),
        ]

        f_lbl = pygame.font.SysFont("Arial", 11)
        f_val = pygame.font.SysFont("Arial", 12, bold=True)

        for i, (label, value) in enumerate(rows):
            ry = y + 6 + i * 24
            lbl_s = f_lbl.render(label, True, Colors.METRIC_LABEL)
            surface.blit(lbl_s, (self.x + 14, ry))

            vc = status_color if label == "Status" else Colors.METRIC_VALUE
            val_s = f_val.render(value, True, vc)
            surface.blit(val_s, (self.x + self.width - 14 - val_s.get_width(), ry))

    def _draw_comparison(self, surface, y):
        self._draw_section_header(surface, "COMPARISON", self.x + 8, y)
        y += 18

        f = pygame.font.SysFont("Arial", 11)
        fb = pygame.font.SysFont("Arial", 11, bold=True)

        # Column x positions
        cx = [self.x + 10, self.x + 68, self.x + 116, self.x + 172]
        for i, h in enumerate(["Algo", "Nodes", "Path", "ms"]):
            surface.blit(fb.render(h, True, Colors.TEXT_DIM), (cx[i], y))
        y += 15
        pygame.draw.line(surface, Colors.SIDEBAR_BORDER,
                         (self.x + 8, y), (self.x + self.width - 8, y), 1)
        y += 4

        found = [r for r in self.comparison_results if r["found"]]
        best_path  = min((r["path_length"]    for r in found), default=None)
        best_nodes = min((r["nodes_explored"] for r in found), default=None)

        for r in self.comparison_results:
            vals = [
                r["algorithm"],
                str(r["nodes_explored"]),
                str(r["path_length"]) if r["found"] else "✗",
                f"{r['time_ms']:.1f}",
            ]
            for i, v in enumerate(vals):
                is_best = (
                    (i == 2 and r["found"] and r["path_length"]    == best_path)  or
                    (i == 1 and r["found"] and r["nodes_explored"] == best_nodes)
                )
                c = Colors.TEXT_ACCENT if is_best else (
                    Colors.STATUS_NOT_FOUND if (i == 2 and not r["found"]) else Colors.TEXT_SECONDARY
                )
                surface.blit(f.render(v, True, c), (cx[i], y))
            y += 15


# ============================================================
# Theory Overlay
# ============================================================
class TheoryOverlay:
    """Full-screen dimmed overlay showing algorithm theory details."""

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.pw = 680
        self.ph = 400

    def draw(self, surface, algo_name):
        if algo_name not in ALGORITHM_INFO:
            return
        info = ALGORITHM_INFO[algo_name]

        # Dim
        dim = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        dim.fill((0, 0, 15, 170))
        surface.blit(dim, (0, 0))

        # Panel
        px = (self.screen_w - self.pw) // 2
        py = (self.screen_h - self.ph) // 2
        pygame.draw.rect(surface, Colors.SIDEBAR_BG,
                         (px, py, self.pw, self.ph), border_radius=10)
        pygame.draw.rect(surface, Colors.BUTTON_ACTIVE,
                         (px, py, self.pw, self.ph), 2, border_radius=10)

        f_title = pygame.font.SysFont("Arial", 19, bold=True)
        f_head  = pygame.font.SysFont("Arial", 12, bold=True)
        f_body  = pygame.font.SysFont("Arial", 12)
        f_hint  = pygame.font.SysFont("Arial", 10)

        y = py + 18

        # Title
        title_s = f_title.render(f"{algo_name}  —  {info['full_name']}", True, Colors.BUTTON_ACTIVE)
        surface.blit(title_s, (px + 20, y))
        y += 30

        # Description
        for line in self._wrap(info["description"], f_body, self.pw - 40):
            surface.blit(f_body.render(line, True, Colors.TEXT_PRIMARY), (px + 20, y))
            y += 19
        y += 6

        pygame.draw.line(surface, Colors.SIDEBAR_BORDER,
                         (px + 20, y), (px + self.pw - 20, y), 1)
        y += 10

        # Key idea
        surface.blit(f_head.render("Key Idea:", True, Colors.TEXT_ACCENT), (px + 20, y))
        for line in self._wrap(info["key_idea"], f_body, self.pw - 130):
            surface.blit(f_body.render(line, True, Colors.TEXT_PRIMARY), (px + 110, y))
            y += 19
        y += 8

        # Properties table
        table = [
            ("Complete:",    info["complete"]),
            ("Optimal:",     info["optimal"]),
            ("Time:",        info["time_complexity"]),
            ("Space:",       info["space_complexity"]),
            ("Notation:",    info["b"]),
        ]
        for label, value in table:
            surface.blit(f_head.render(label, True, Colors.METRIC_LABEL), (px + 20, y))
            surface.blit(f_body.render(value, True, Colors.TEXT_PRIMARY), (px + 130, y))
            y += 21

        # Dismiss hint
        hint_s = f_hint.render("Press  T  or  ESC  to close", True, Colors.TEXT_DIM)
        surface.blit(hint_s, (px + self.pw // 2 - hint_s.get_width() // 2, py + self.ph - 24))

    @staticmethod
    def _wrap(text, font, max_w):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines
