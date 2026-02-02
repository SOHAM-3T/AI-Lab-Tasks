import random
import math
import time
import tracemalloc
from typing import List, Tuple, Optional, Callable, Iterable
import statistics
import pandas as pd

# Small utility
def argmin(items: Iterable, key: Callable):
    best_item = None
    best_val = None
    for it in items:
        val = key(it)
        if best_val is None or val < best_val:
            best_item, best_val = it, val
    return best_item, best_val

# Class for 8 Queens
class EightQueens:
    def __init__(self, n: int = 8, seed: Optional[int] = None):
        self.n = n
        self.rng = random.Random(seed)

    def random_state(self) -> List[int]:
        return [self.rng.randrange(self.n) for _ in range(self.n)]

    def heuristic(self, state: List[int]) -> int:
        conflicts = 0
        n = self.n
        for c1 in range(n):
            r1 = state[c1]
            for c2 in range(c1 + 1, n):
                r2 = state[c2]
                if r1 == r2 or abs(r1 - r2) == abs(c1 - c2):
                    conflicts += 1
        return conflicts

    def best_neighbor(self, state: List[int]) -> Tuple[List[int], int]:
        n = self.n
        current_h = self.heuristic(state)
        best = (state, current_h)
        for c in range(n):
            original_row = state[c]
            for r in range(n):
                if r == original_row:
                    continue
                neighbor = state.copy()
                neighbor[c] = r
                h = self.heuristic(neighbor)
                if h < best[1]:
                    best = (neighbor, h)
        return best

    def hill_climb(self, start: Optional[List[int]] = None, max_steps: int = 1000) -> Tuple[List[int], int, int]:
        state = start if start is not None else self.random_state()
        h = self.heuristic(state)
        steps = 0
        while steps < max_steps and h > 0:
            steps += 1
            neighbor, h2 = self.best_neighbor(state)
            if h2 < h:
                state, h = neighbor, h2
            else:
                break  # local minimum / plateau
        return state, h, steps

    def random_restart(self, max_restarts: int = 100, max_steps: int = 1000) -> Tuple[List[int], int, int, int]:
        best_state = None
        best_h = math.inf
        total_steps = 0
        restarts = 0
        for r in range(max_restarts):
            restarts += 1
            start = self.random_state()
            state, h, steps = self.hill_climb(start, max_steps)
            total_steps += steps
            if h < best_h:
                best_state, best_h = state, h
            if best_h == 0:
                break
        return best_state, best_h, restarts, total_steps

# Class for 8 puzzle
class EightPuzzle:
    GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    NEIGHBOR_DELTAS = {
        0: (1, 3),
        1: (-1, 1, 3),
        2: (-1, 3),
        3: (-3, 1, 3),
        4: (-3, -1, 1, 3),
        5: (-3, -1, 3),
        6: (-3, 1),
        7: (-3, -1, 1),
        8: (-3, -1),
    }

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)

    @staticmethod
    def manhattan(state: Tuple[int, ...]) -> int:
        dist = 0
        for idx, tile in enumerate(state):
            if tile == 0:
                continue
            goal_idx = tile - 1
            x1, y1 = divmod(idx, 3)
            x2, y2 = divmod(goal_idx, 3)
            dist += abs(x1 - x2) + abs(y1 - y2)
        return dist

    def neighbors(self, state: Tuple[int, ...]) -> List[Tuple[int, ...]]:
        i0 = state.index(0)
        neigh = []
        for d in self.NEIGHBOR_DELTAS[i0]:
            j = i0 + d
            s = list(state)
            s[i0], s[j] = s[j], s[i0]
            neigh.append(tuple(s))
        return neigh

    @staticmethod
    def is_solvable(state: Tuple[int, ...]) -> bool:
        arr = [x for x in state if x != 0]
        inv = 0
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if arr[i] > arr[j]:
                    inv += 1
        return inv % 2 == 0

    def random_state(self, scramble_moves: int = 50) -> Tuple[int, ...]:
        state = self.GOAL
        for _ in range(scramble_moves):
            state = self.rng.choice(self.neighbors(state))
        return state

    def hill_climb(
        self,
        start: Optional[Tuple[int, ...]] = None,
        max_steps: int = 1000,
        sideways_limit: int = 20,
    ) -> Tuple[Tuple[int, ...], int, int, bool]:
        current = start if start is not None else self.random_state()
        h = self.manhattan(current)
        steps = 0
        sideways = 0
        while steps < max_steps and h > 0:
            steps += 1
            neigh = self.neighbors(current)
            best, best_h = argmin(neigh, key=self.manhattan)
            if best_h < h:
                current, h = best, best_h
                sideways = 0
            elif best_h == h and sideways < sideways_limit:
                current, h = best, best_h
                sideways += 1
            else:
                break
        return current, h, steps, (h == 0)

    def random_restart(
        self,
        max_restarts: int = 100,
        max_steps: int = 2000,
        sideways_limit: int = 30,
        scramble_moves: int = 50,
    ) -> Tuple[Tuple[int, ...], int, int, int, bool]:
        best_state = None
        best_h = math.inf
        total_steps = 0
        restarts = 0
        solved = False
        for _ in range(max_restarts):
            restarts += 1
            start = self.random_state(scramble_moves)
            assert self.is_solvable(start)
            state, h, steps, reached = self.hill_climb(start, max_steps, sideways_limit)
            total_steps += steps
            if h < best_h:
                best_state, best_h = state, h
            if reached:
                solved = True
                break
        return best_state, best_h, restarts, total_steps, solved

# Class for Travelling Salesman
class TSP:
    def __init__(self, coords: List[Tuple[float, float]], seed: Optional[int] = None):
        self.coords = coords
        self.n = len(coords)
        self.rng = random.Random(seed)
        self.dist = [[0.0] * self.n for _ in range(self.n)]
        for i in range(self.n):
            xi, yi = coords[i]
            for j in range(i + 1, self.n):
                xj, yj = coords[j]
                d = math.hypot(xi - xj, yi - yj)
                self.dist[i][j] = self.dist[j][i] = d

    def tour_length(self, tour: List[int]) -> float:
        n = self.n
        total = 0.0
        for i in range(n):
            a = tour[i]
            b = tour[(i + 1) % n]
            total += self.dist[a][b]
        return total

    def random_tour(self) -> List[int]:
        tour = list(range(self.n))
        self.rng.shuffle(tour)
        return tour

    def two_opt_swap(self, tour: List[int], i: int, k: int) -> List[int]:
        return tour[:i] + list(reversed(tour[i:k + 1])) + tour[k + 1:]

    def best_2opt_neighbor(self, tour: List[int]) -> Tuple[List[int], float]:
        best = (tour, self.tour_length(tour))
        n = self.n
        current_len = best[1]
        for i in range(n - 1):
            for k in range(i + 1, n):
                neighbor = self.two_opt_swap(tour, i, k)
                L = self.tour_length(neighbor)
                if L < current_len:
                    current_len = L
                    best = (neighbor, L)
        return best

    def hill_climb(self, start: Optional[List[int]] = None, max_steps: int = 1000) -> Tuple[List[int], float, int]:
        tour = self.random_tour() if start is None else start
        length = self.tour_length(tour)
        steps = 0
        while steps < max_steps:
            steps += 1
            neigh, L = self.best_2opt_neighbor(tour)
            if L < length:
                tour, length = neigh, L
            else:
                break
        return tour, length, steps

    def random_restart(self, max_restarts: int = 50, max_steps: int = 1000) -> Tuple[List[int], float, int, int]:
        best_tour = None
        best_len = math.inf
        total_steps = 0
        restarts = 0
        for _ in range(max_restarts):
            restarts += 1
            start = self.random_tour()
            tour, L, steps = self.hill_climb(start, max_steps)
            total_steps += steps
            if L < best_len:
                best_tour, best_len = tour, L
        return best_tour, best_len, restarts, total_steps


def measure_function(fn: Callable, *args, **kwargs):
    tracemalloc.start()
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"result": result, "time_s": t1 - t0, "peak_kb": peak / 1024.0}


def run_comparison_1run(problem_name: str, hill_fn: Callable, rr_fn: Callable, trials: int = 10):
    hill_stats = []
    for _ in range(trials):
        m = measure_function(hill_fn)
        hill_stats.append(m)

    hill_times = [h["time_s"] for h in hill_stats]
    hill_peaks = [h["peak_kb"] for h in hill_stats]
    hill_results = [h["result"] for h in hill_stats]

    rrm = measure_function(rr_fn)
    rr_result = rrm["result"]

    summary = {"problem": problem_name}

    summary["HC_trials"] = trials
    summary["HC_time_mean_s"] = statistics.mean(hill_times)
    summary["HC_time_std_s"] = statistics.pstdev(hill_times) if trials > 1 else 0.0
    summary["HC_peak_mean_kb"] = statistics.mean(hill_peaks)

    hc_values = []
    hc_steps = []
    hc_solved_count = 0
    for res in hill_results:
        if isinstance(res, tuple) and len(res) >= 3:
            value = res[1]  # h or length
            steps = res[2]
            hc_values.append(value)
            hc_steps.append(steps)
            if len(res) >= 4 and isinstance(res[3], bool) and res[3]:
                hc_solved_count += 1
        else:
            hc_values.append(None)
            hc_steps.append(None)

    summary["HC_value_mean"] = statistics.mean(hc_values) if hc_values else None
    summary["HC_value_best"] = min(hc_values) if hc_values else None
    summary["HC_steps_mean"] = statistics.mean(hc_steps) if hc_steps else None
    summary["HC_solved_count"] = hc_solved_count

    summary["RR_time_s"] = rrm["time_s"]
    summary["RR_peak_kb"] = rrm["peak_kb"]

    if isinstance(rr_result, tuple):
        try:
            summary["RR_value"] = rr_result[1]
        except Exception:
            summary["RR_value"] = None
        try:
            summary["RR_restarts"] = rr_result[2]
        except Exception:
            summary["RR_restarts"] = None
        try:
            summary["RR_steps"] = rr_result[3]
        except Exception:
            summary["RR_steps"] = None
        # for puzzle solved flag
        if len(rr_result) >= 5:
            summary["RR_solved"] = rr_result[4]
        else:
            summary["RR_solved"] = None
    else:
        summary["RR_value"] = None
        summary["RR_restarts"] = None
        summary["RR_steps"] = None
        summary["RR_solved"] = None

    return summary

if __name__ == "__main__":
    random_seed = 42

    # Eight-Queens
    q = EightQueens(n=8, seed=random_seed)
    def q_hill():
        return q.hill_climb(start=None, max_steps=2000)
    def q_rr():
        return q.random_restart(max_restarts=200, max_steps=2000)
    q_summary = run_comparison_1run("8-Queens", q_hill, q_rr, trials=20)

    # Eight-Puzzle
    p = EightPuzzle(seed=random_seed)
    def p_hill():
        start = p.random_state(scramble_moves=50)
        return p.hill_climb(start=start, max_steps=2000, sideways_limit=50)
    def p_rr():
        return p.random_restart(max_restarts=200, max_steps=2000, sideways_limit=50, scramble_moves=50)
    p_summary = run_comparison_1run("8-Puzzle", p_hill, p_rr, trials=20)

    # TSP (n=20 for moderate difficulty)
    rng = random.Random(random_seed)
    coords = [(rng.random(), rng.random()) for _ in range(20)]
    tsp = TSP(coords, seed=random_seed)
    def t_hill():
        return tsp.hill_climb(start=None, max_steps=2000)
    def t_rr():
        return tsp.random_restart(max_restarts=100, max_steps=2000)
    t_summary = run_comparison_1run("TSP(20)", t_hill, t_rr, trials=10)

    summaries = [q_summary, p_summary, t_summary]

    # a clean comparison table
    header = [
        "problem",
        "HC_trials",
        "HC_value_mean",
        "HC_value_best",
        "HC_steps_mean",
        "HC_solved_count",
        "HC_time_mean_s",
        "HC_peak_mean_kb",
        "RR_value",
        "RR_restarts",
        "RR_steps",
        "RR_solved",
        "RR_time_s",
        "RR_peak_kb",
    ]


    df = pd.DataFrame(summaries)
    print("\n\n Summary:")
    print(df[header].to_string(index=False))
