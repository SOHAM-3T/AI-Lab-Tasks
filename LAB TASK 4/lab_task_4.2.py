import random
import math

# 8 Queens
def q_random_state(n=8):
    l = []
    for i in range(n):
        l.append(random.randrange(n))
    return l

def q_heuristic(state):
    # number of attacking pairs
    conflicts = 0
    n = len(state)
    for c1 in range(n):
        for c2 in range(c1+1, n):
            r1, r2 = state[c1], state[c2]
            if r1 == r2 or abs(r1 - r2) == abs(c1 - c2):
                conflicts += 1
    return conflicts

def q_best_neighbor(state):
    n = len(state)
    best_state = state[:]
    best_h = q_heuristic(state)
    for c in range(n):
        orig = state[c]
        for r in range(n):
            if r == orig:
                continue
            s = state[:]
            s[c] = r
            h = q_heuristic(s)
            if h < best_h:
                best_h = h
                best_state = s
    return best_state, best_h

def q_hill_climb(n=8, start=None, max_steps=1000):
    if start is not None:
        state = start[:]
    else:
        state = q_random_state(n)

    h = q_heuristic(state)
    steps = 0
    while steps < max_steps and h > 0:
        steps += 1
        nb, nh = q_best_neighbor(state)
        if nh < h:
            state, h = nb, nh
        else:
            break
    return state, h, steps

def q_random_restart(n=8, max_restarts=100, max_steps=1000):
    best_state = None
    best_h = float('inf')
    total_steps = 0
    for i in range(max_restarts):
        state, h, steps = q_hill_climb(n, None,  max_steps)
        total_steps += steps
        if h < best_h:
            best_h = h
            best_state = state
        if best_h == 0:
            return best_state, best_h, i+1, total_steps
    return best_state, best_h, max_restarts, total_steps

# 8 - Puzzle
GOAL_PUZZLE = (1,2,3,4,5,6,7,8,0)

def p_manhattan(state):
    dist = 0
    for idx, tile in enumerate(state):
        if tile == 0: continue
        goal_idx = tile - 1
        x1, y1 = divmod(idx, 3)
        x2, y2 = divmod(goal_idx, 3)
        dist += abs(x1 - x2) + abs(y1 - y2)
    return dist

def p_neighbors(state):
    i0 = state.index(0)
    neighbors = []
    # possible moves from index i0
    for d in (-3, 3, -1, 1):
        j = i0 + d
        if j < 0 or j >= 9:
            continue
        # avoid left/right wrapping
        if d == -1 and i0 % 3 == 0:
            continue
        if d == 1 and i0 % 3 == 2:
            continue
        s = list(state)
        s[i0], s[j] = s[j], s[i0]
        neighbors.append(tuple(s))
    return neighbors

def p_is_solvable(state):
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1
    return inv % 2 == 0

def p_random_state(scramble_moves=50):
    state = GOAL_PUZZLE
    for _ in range(scramble_moves):
        state = random.choice(p_neighbors(state))
    return state

def p_hill_climb(start=None, max_steps=1000, sideways_limit=20):
    current = start if start is not None else p_random_state()
    h = p_manhattan(current)
    steps = 0
    sideways = 0
    while steps < max_steps and h > 0:
        steps += 1
        neighs = p_neighbors(current)
        # choose neighbor with minimum manhattan
        best = min(neighs, key=p_manhattan)
        best_h = p_manhattan(best)
        if best_h < h:
            current, h = best, best_h
            sideways = 0
        elif best_h == h and sideways < sideways_limit:
            current, h = best, best_h
            sideways += 1
        else:
            break
    return current, h, steps, (h == 0)

def p_random_restart(max_restarts=100, max_steps=2000, sideways_limit=30, scramble_moves=50):
    best_state = None
    best_h = float('inf')
    total_steps = 0
    for i in range(max_restarts):
        start = p_random_state(scramble_moves=scramble_moves)
        assert p_is_solvable(start)
        state, h, steps, reached = p_hill_climb(start=start, max_steps=max_steps, sideways_limit=sideways_limit)
        total_steps += steps
        if h < best_h:
            best_h, best_state = h, state
        if reached:
            return best_state, best_h, i+1, total_steps, True
    return best_state, best_h, max_restarts, total_steps, False

def p_moves_from_solution(solution):
    if not solution:
        return []
    moves = []
    for a, b in zip(solution, solution[1:]):
        i0a = a.index(0)
        i0b = b.index(0)
        # tile that moved is the tile now at i0a in a (which moved to blank)
        moved_tile = a[i0b]
        moves.append(moved_tile)
    return moves

#TSP
def t_distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def t_tour_length(tour, coords):
    total = 0.0
    n = len(tour)
    for i in range(n):
        a = tour[i]
        b = tour[(i+1) % n]
        total += t_distance(coords[a], coords[b])
    return total

def t_random_tour(n):
    tour = list(range(n))
    random.shuffle(tour)
    return tour

def t_two_opt_swap(tour, i, k):
    return tour[:i] + list(reversed(tour[i:k+1])) + tour[k+1:]

def t_best_2opt_neighbor(tour, coords):
    best = tour[:]
    best_len = t_tour_length(tour, coords)
    n = len(tour)
    for i in range(n-1):
        for k in range(i+1, n):
            new_tour = t_two_opt_swap(tour, i, k)
            L = t_tour_length(new_tour, coords)
            if L < best_len:
                best_len = L
                best = new_tour
    return best, best_len

def t_hill_climb(coords, start=None, max_steps=1000):
    n = len(coords)
    if start is not None:
        tour = start[:]
    else:
        tour = t_random_tour(n)
    length = t_tour_length(tour, coords)
    steps = 0
    while steps < max_steps:
        steps += 1
        neigh, L = t_best_2opt_neighbor(tour, coords)
        if L < length:
            tour, length = neigh, L
        else:
            break
    return tour, length, steps

def t_random_restart(coords, max_restarts=50, max_steps=1000):
    best_tour = None
    best_len = float('inf')
    total_steps = 0
    for i in range(max_restarts):
        start = t_random_tour(len(coords))
        tour, L, steps = t_hill_climb(coords, start=start, max_steps=max_steps)
        total_steps += steps
        if L < best_len:
            best_len, best_tour = L, tour
    return best_tour, best_len, max_restarts, total_steps


if __name__ == "__main__":
    random.seed(42)

    print("=== 8-Queens (hill-climb + random-restart) ===")
    sol, h, steps = q_hill_climb(n=8, start=None, max_steps=2000)
    print("Hill-climb result h:", h, "steps:", steps, "state:", sol)
    best, best_h, restarts, total_steps = q_random_restart(n=8, max_restarts=200, max_steps=2000)
    print("Random-restart best h:", best_h, "restarts used:", restarts, "total steps:", total_steps)
    if best_h == 0:
        print("Found solution:", best)

    print("\n=== 8-Puzzle (hill-climb + random-restart) ===")
    start_p = p_random_state(scramble_moves=50)
    print("Start state:", start_p)
    final, h, steps, reached = p_hill_climb(start=start_p, max_steps=2000, sideways_limit=30)
    print("Hill-climb result h:", h, "steps:", steps, "reached:", reached)
    best_p, best_h, restarts_p, total_steps_p, solved = p_random_restart(max_restarts=200, max_steps=2000, sideways_limit=30, scramble_moves=50)
    print("Random-restart best h:", best_h, "restarts used:", restarts_p, "total steps:", total_steps_p, "solved:", solved)
    if solved:
        print("Solved state:", best_p)

    print("\n=== TSP (2-opt hill-climb + random-restart) ===")
    # make 8 random coordinates for a small demo
    coords = [(random.random(), random.random()) for _ in range(8)]
    tour, L, steps = t_hill_climb(coords, start=None, max_steps=2000)
    print("Hill-climb tour length:", L, "steps:", steps)
    best_tour, best_len, restarts_t, total_steps_t = t_random_restart(coords, max_restarts=100, max_steps=2000)
    print("Random-restart best length:", best_len, "restarts used:", restarts_t, "total steps:", total_steps_t)
