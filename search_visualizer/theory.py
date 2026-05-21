"""Algorithm theory and complexity data for educational overlay."""

ALGORITHM_INFO = {
    "BFS": {
        "full_name": "Breadth-First Search",
        "description": "Explores nodes level by level, guaranteeing the shortest path in unweighted graphs.",
        "complete": "Yes",
        "optimal": "Yes (unweighted)",
        "time_complexity": "O(b^d)",
        "space_complexity": "O(b^d)",
        "key_idea": "Uses a FIFO queue. Expands shallowest unexpanded node first.",
        "b": "b = branching factor, d = depth of shallowest goal",
    },
    "DFS": {
        "full_name": "Depth-First Search",
        "description": "Explores as deep as possible before backtracking. Memory efficient but not optimal.",
        "complete": "No (can loop)",
        "optimal": "No",
        "time_complexity": "O(b^m)",
        "space_complexity": "O(bm)",
        "key_idea": "Uses a LIFO stack. Expands deepest unexpanded node first.",
        "b": "b = branching factor, m = maximum depth",
    },
    "DLS": {
        "full_name": "Depth-Limited Search",
        "description": "DFS with a depth cutoff. Prevents infinite loops but may miss goals beyond the limit.",
        "complete": "No",
        "optimal": "No",
        "time_complexity": "O(b^l)",
        "space_complexity": "O(bl)",
        "key_idea": "DFS that stops expanding at depth l. Cutoff prevents infinite descent.",
        "b": "b = branching factor, l = depth limit",
    },
    "IDS": {
        "full_name": "Iterative Deepening Search",
        "description": "Combines DFS space-efficiency with BFS completeness by gradually increasing depth limits.",
        "complete": "Yes",
        "optimal": "Yes (unweighted)",
        "time_complexity": "O(b^d)",
        "space_complexity": "O(bd)",
        "key_idea": "Repeated DLS with increasing depth. Redundant work is bounded.",
        "b": "b = branching factor, d = depth of shallowest goal",
    },
    "UCS": {
        "full_name": "Uniform Cost Search",
        "description": "Expands the lowest-cost node first. Optimal for any step cost >= 0.",
        "complete": "Yes (cost > 0)",
        "optimal": "Yes",
        "time_complexity": "O(b^(C*/e))",
        "space_complexity": "O(b^(C*/e))",
        "key_idea": "Uses a priority queue ordered by path cost g(n). Like BFS with cost awareness.",
        "b": "C* = optimal cost, e = minimum edge cost",
    },
    "Greedy": {
        "full_name": "Greedy Best-First Search",
        "description": "Expands the node closest to the goal using a heuristic. Fast but not optimal.",
        "complete": "No",
        "optimal": "No",
        "time_complexity": "O(b^m)",
        "space_complexity": "O(b^m)",
        "key_idea": "Uses h(n) only. Prioritizes nodes that appear closest to goal.",
        "b": "b = branching factor, m = maximum depth",
    },
    "A*": {
        "full_name": "A* Search",
        "description": "Combines actual cost g(n) with heuristic h(n). Optimal with admissible heuristic.",
        "complete": "Yes",
        "optimal": "Yes (admissible h)",
        "time_complexity": "O(b^d)",
        "space_complexity": "O(b^d)",
        "key_idea": "Uses f(n) = g(n) + h(n). Best of both worlds: optimal and informed.",
        "b": "b = branching factor, d = depth of solution",
    },
}

ALGORITHM_LIST = ["BFS", "DFS", "DLS", "IDS", "UCS", "Greedy", "A*"]

COMPARISON_ALGORITHMS = ["BFS", "DFS", "A*"]
