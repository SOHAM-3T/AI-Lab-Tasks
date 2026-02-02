import random
import math
from typing import List, Tuple, Optional, Callable, Iterable

def argmin(items: Iterable, key: Callable):
    best_item = None
    best_val = None
    for it in items:
        val = key(it)
        if best_val is None or val < best_val:
            best_item, best_val = it, val
    return best_item, best_val


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

    def hill_climb(self, start: List[int], max_steps: int = 1000) -> Tuple[List[int], int, int]:
        state = start
        h = self.heuristic(state)
        steps = 0
        while steps < max_steps:
            steps += 1
            neighbor, h2 = self.best_neighbor(state)
            if h2 < h:
                state, h = neighbor, h2
            else:
                break  # Local minimum / plateau
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
        # 3x3 puzzle solvable iff inversion count is even
        return inv % 2 == 0

    def random_state(self, scramble_moves: int = 50) -> Tuple[int, ...]:
        state = self.GOAL
        for _ in range(scramble_moves):
            state = self.rng.choice(self.neighbors(state))
        return state

    def hill_climb(
        self,
        start: Tuple[int, ...],
        max_steps: int = 1000,
        sideways_limit: int = 20,
    ) -> Tuple[Tuple[int, ...], int, int, bool]:
        """Return (state, h, steps, reached_goal)."""
        current = start
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
                break  # local minimum/plateau
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


class TSP:
    def __init__(self, coords: List[Tuple[float, float]], seed: Optional[int] = None):
        self.coords = coords
        self.n = len(coords)
        self.rng = random.Random(seed)
        # Precompute distance matrix for speed
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


if __name__ == "__main__":
    print("--- 8-Queens (Random-Restart Hill Climbing) ---")
    q = EightQueens(n=8, seed=42)
    sol, h, restarts, steps = q.random_restart(max_restarts=100, max_steps=2000)
    print(f"Best heuristic: {h}; restarts: {restarts}; total steps: {steps}")
    print("Solution state (row per column):", sol)

    print("\n--- 8-Puzzle (Random-Restart Hill Climbing) ---")
    p = EightPuzzle(seed=42)
    state, h, restarts, steps, solved = p.random_restart(
        max_restarts=50, max_steps=5000, sideways_limit=50, scramble_moves=60
    )
    print(f"Best heuristic: {h}; solved: {solved}; restarts: {restarts}; total steps: {steps}")
    print("State:", state)

    print("\n--- TSP (Random-Restart Hill Climbing with 2-opt) ---")
    rng = random.Random(42)
    coords = [(rng.random(), rng.random()) for _ in range(30)]
    tsp = TSP(coords, seed=42)
    tour, L, restarts, steps = tsp.random_restart(max_restarts=30, max_steps=2000)
    print(f"Best tour length: {L:.4f}; restarts: {restarts}; total steps: {steps}")
    print("Tour:", tour)
