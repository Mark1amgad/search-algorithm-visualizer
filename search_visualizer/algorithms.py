"""Search algorithms implemented as step-by-step generators for visualization."""

import time
from collections import deque
from queue import PriorityQueue
import heapq


class AlgorithmState:
    """Tracks the visual state of a running algorithm."""

    def __init__(self):
        self.current = None
        self.visited = set()
        self.frontier = set()
        self.path = []
        self.found = False
        self.finished = False
        self.nodes_explored = 0
        self.start_time = 0
        self.elapsed_ms = 0

    def reset(self):
        self.current = None
        self.visited = set()
        self.frontier = set()
        self.path = []
        self.found = False
        self.finished = False
        self.nodes_explored = 0
        self.start_time = time.time()
        self.elapsed_ms = 0


def _reconstruct_path(parent, start, goal):
    """Reconstruct path from parent map."""
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent.get(node)
    path.reverse()
    return path


def _manhattan_distance(a, b):
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ============================================================
# BFS - Breadth-First Search
# ============================================================
def bfs(grid, start, goal, state):
    """Breadth-First Search - explores level by level."""
    state.reset()
    queue = deque([start])
    discovered = {start}
    parent = {start: None}
    state.frontier = {start}

    while queue:
        current = queue.popleft()
        state.frontier.discard(current)
        state.visited.add(current)
        state.current = current
        state.nodes_explored += 1
        state.elapsed_ms = (time.time() - state.start_time) * 1000

        yield

        if current == goal:
            state.path = _reconstruct_path(parent, start, goal)
            state.found = True
            state.finished = True
            state.elapsed_ms = (time.time() - state.start_time) * 1000
            return

        for neighbor in grid.get_neighbors(current):
            if neighbor not in discovered:
                discovered.add(neighbor)
                queue.append(neighbor)
                state.frontier.add(neighbor)
                parent[neighbor] = current

    state.finished = True
    state.found = False
    state.elapsed_ms = (time.time() - state.start_time) * 1000


# ============================================================
# DFS - Depth-First Search
# ============================================================
def dfs(grid, start, goal, state):
    """Depth-First Search - explores deeply before backtracking."""
    state.reset()
    stack = [start]
    discovered = {start}
    parent = {start: None}
    state.frontier = {start}

    while stack:
        current = stack.pop()
        state.frontier.discard(current)
        state.visited.add(current)
        state.current = current
        state.nodes_explored += 1
        state.elapsed_ms = (time.time() - state.start_time) * 1000

        yield

        if current == goal:
            state.path = _reconstruct_path(parent, start, goal)
            state.found = True
            state.finished = True
            state.elapsed_ms = (time.time() - state.start_time) * 1000
            return

        neighbors = grid.get_neighbors(current)
        for neighbor in reversed(neighbors):
            if neighbor not in discovered:
                discovered.add(neighbor)
                stack.append(neighbor)
                state.frontier.add(neighbor)
                parent[neighbor] = current

    state.finished = True
    state.found = False
    state.elapsed_ms = (time.time() - state.start_time) * 1000


# ============================================================
# DLS - Depth-Limited Search
# ============================================================
def dls(grid, start, goal, state, max_depth=10):
    """Depth-Limited Search - DFS with a depth cutoff."""
    state.reset()
    # Stack entries: (node, depth)
    stack = [(start, 0)]
    discovered = {start}
    parent = {start: None}
    depth_map = {start: 0}
    state.frontier = {start}

    while stack:
        current, depth = stack.pop()
        state.frontier.discard(current)
        state.visited.add(current)
        state.current = current
        state.nodes_explored += 1
        state.elapsed_ms = (time.time() - state.start_time) * 1000

        yield

        if current == goal:
            state.path = _reconstruct_path(parent, start, goal)
            state.found = True
            state.finished = True
            state.elapsed_ms = (time.time() - state.start_time) * 1000
            return

        if depth < max_depth:
            neighbors = grid.get_neighbors(current)
            for neighbor in reversed(neighbors):
                if neighbor not in discovered:
                    discovered.add(neighbor)
                    stack.append((neighbor, depth + 1))
                    state.frontier.add(neighbor)
                    parent[neighbor] = current
                    depth_map[neighbor] = depth + 1

    state.finished = True
    state.found = False
    state.elapsed_ms = (time.time() - state.start_time) * 1000


# ============================================================
# IDS - Iterative Deepening Search
# ============================================================
def ids(grid, start, goal, state, max_iterations=50):
    """Iterative Deepening Search - DLS with increasing depth limits."""
    state.reset()
    total_explored = 0
    all_visited = set()

    for depth_limit in range(max_iterations + 1):
        # Run DLS at this depth
        inner_visited = set()
        stack = [(start, 0)]
        discovered = {start}
        parent = {start: None}

        while stack:
            current, depth = stack.pop()
            inner_visited.add(current)
            state.current = current
            total_explored += 1
            state.nodes_explored = total_explored
            state.visited = all_visited | inner_visited
            state.elapsed_ms = (time.time() - state.start_time) * 1000

            yield

            if current == goal:
                state.path = _reconstruct_path(parent, start, goal)
                state.found = True
                state.finished = True
                state.elapsed_ms = (time.time() - state.start_time) * 1000
                return

            if depth < depth_limit:
                neighbors = grid.get_neighbors(current)
                for neighbor in reversed(neighbors):
                    if neighbor not in discovered:
                        discovered.add(neighbor)
                        stack.append((neighbor, depth + 1))
                        parent[neighbor] = current

        all_visited |= inner_visited
        state.visited = all_visited
        state.frontier = set()

    state.finished = True
    state.found = False
    state.elapsed_ms = (time.time() - state.start_time) * 1000


# ============================================================
# UCS - Uniform Cost Search
# ============================================================
def ucs(grid, start, goal, state):
    """Uniform Cost Search - expands lowest-cost node first."""
    state.reset()
    # (cost, counter, node) - counter breaks ties
    counter = 0
    pq = [(0, counter, start)]
    discovered = {start: 0}
    parent = {start: None}
    state.frontier = {start}

    while pq:
        cost, _, current = heapq.heappop(pq)

        if current in state.visited:
            state.frontier.discard(current)
            continue

        state.frontier.discard(current)
        state.visited.add(current)
        state.current = current
        state.nodes_explored += 1
        state.elapsed_ms = (time.time() - state.start_time) * 1000

        yield

        if current == goal:
            state.path = _reconstruct_path(parent, start, goal)
            state.found = True
            state.finished = True
            state.elapsed_ms = (time.time() - state.start_time) * 1000
            return

        for neighbor in grid.get_neighbors(current):
            new_cost = cost + 1
            if neighbor not in discovered or new_cost < discovered[neighbor]:
                discovered[neighbor] = new_cost
                counter += 1
                heapq.heappush(pq, (new_cost, counter, neighbor))
                state.frontier.add(neighbor)
                parent[neighbor] = current

    state.finished = True
    state.found = False
    state.elapsed_ms = (time.time() - state.start_time) * 1000


# ============================================================
# Greedy Best-First Search
# ============================================================
def greedy(grid, start, goal, state):
    """Greedy Best-First Search - uses heuristic only."""
    state.reset()
    counter = 0
    h = _manhattan_distance(start, goal)
    pq = [(h, counter, start)]
    discovered = {start}
    parent = {start: None}
    state.frontier = {start}

    while pq:
        _, _, current = heapq.heappop(pq)

        if current in state.visited:
            state.frontier.discard(current)
            continue

        state.frontier.discard(current)
        state.visited.add(current)
        state.current = current
        state.nodes_explored += 1
        state.elapsed_ms = (time.time() - state.start_time) * 1000

        yield

        if current == goal:
            state.path = _reconstruct_path(parent, start, goal)
            state.found = True
            state.finished = True
            state.elapsed_ms = (time.time() - state.start_time) * 1000
            return

        for neighbor in grid.get_neighbors(current):
            if neighbor not in discovered:
                discovered.add(neighbor)
                h = _manhattan_distance(neighbor, goal)
                counter += 1
                heapq.heappush(pq, (h, counter, neighbor))
                state.frontier.add(neighbor)
                parent[neighbor] = current

    state.finished = True
    state.found = False
    state.elapsed_ms = (time.time() - state.start_time) * 1000


# ============================================================
# A* Search
# ============================================================
def astar(grid, start, goal, state):
    """A* Search - uses g(n) + h(n) for optimal informed search."""
    state.reset()
    counter = 0
    h = _manhattan_distance(start, goal)
    # (f, counter, node, g)
    pq = [(h, counter, start, 0)]
    discovered = {start: 0}
    parent = {start: None}
    state.frontier = {start}

    while pq:
        f, _, current, g = heapq.heappop(pq)

        if current in state.visited:
            state.frontier.discard(current)
            continue

        state.frontier.discard(current)
        state.visited.add(current)
        state.current = current
        state.nodes_explored += 1
        state.elapsed_ms = (time.time() - state.start_time) * 1000

        yield

        if current == goal:
            state.path = _reconstruct_path(parent, start, goal)
            state.found = True
            state.finished = True
            state.elapsed_ms = (time.time() - state.start_time) * 1000
            return

        for neighbor in grid.get_neighbors(current):
            new_g = g + 1
            if neighbor not in discovered or new_g < discovered[neighbor]:
                discovered[neighbor] = new_g
                h = _manhattan_distance(neighbor, goal)
                f_new = new_g + h
                counter += 1
                heapq.heappush(pq, (f_new, counter, neighbor, new_g))
                state.frontier.add(neighbor)
                parent[neighbor] = current

    state.finished = True
    state.found = False
    state.elapsed_ms = (time.time() - state.start_time) * 1000


# ============================================================
# Algorithm Registry
# ============================================================
ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "DLS": dls,
    "IDS": ids,
    "UCS": ucs,
    "Greedy": greedy,
    "A*": astar,
}


def run_algorithm_to_completion(algo_name, grid, start, goal, dls_depth=10):
    """Run an algorithm to completion and return metrics dict (no animation)."""
    state = AlgorithmState()
    algo_fn = ALGORITHMS[algo_name]

    if algo_name == "DLS":
        gen = algo_fn(grid, start, goal, state, max_depth=dls_depth)
    else:
        gen = algo_fn(grid, start, goal, state)

    for _ in gen:
        pass  # Consume all steps

    return {
        "algorithm": algo_name,
        "nodes_explored": state.nodes_explored,
        "path_length": len(state.path) if state.found else 0,
        "time_ms": round(state.elapsed_ms, 2),
        "found": state.found,
        "path": state.path,
    }
