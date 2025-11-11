import heapq, math, time, tracemalloc, pandas as pd

goal_state = [[1,2,3],[4,5,6],[7,8,0]]

def to_tuple(state):
    return tuple(tuple(row) for row in state)

def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return None

def manhattan(state):
    dist = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                goal_x = (val-1)//3
                goal_y = (val-1)%3
                dist += abs(i-goal_x) + abs(j-goal_y)
    return dist

def neighbors(state):
    x, y = find_blank(state)
    moves = []
    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    for dx, dy in directions:
        nx, ny = x+dx, y+dy
        if 0<=nx<3 and 0<=ny<3:
            new_state = [row[:] for row in state]
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            moves.append(new_state)
    return moves

# A*
def astar(start):
    tracemalloc.start()
    t0 = time.perf_counter()
    nodes_expanded = 0
    open_set = []
    start_h = manhattan(start)
    heapq.heappush(open_set, (start_h, 0, start_h, start, []))  # (f, g, h, state, path)
    visited = set()
    best_g = {to_tuple(start): 0}

    solution = None
    while open_set:
        f,g,h,state,path = heapq.heappop(open_set)
        tup = to_tuple(state)
        if g != best_g.get(tup, g):
            continue
        nodes_expanded += 1
        if state == goal_state:
            solution = path + [state]
            break
        visited.add(tup)
        for nb in neighbors(state):
            nt = to_tuple(nb)
            new_g = g + 1
            if nt in visited and new_g >= best_g.get(nt, math.inf):
                continue
            if new_g < best_g.get(nt, math.inf):
                best_g[nt] = new_g
                new_h = manhattan(nb)
                new_f = new_g + new_h
                heapq.heappush(open_set, (new_f, new_g, new_h, nb, path+[state]))
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_kb = peak/1024.0
    time_s = t1 - t0
    if solution is None:
        return {"solution": None, "nodes": nodes_expanded, "time": time_s, "peak_kb": peak_kb, "cost": None}
    cost = len(solution)-1
    return {"solution": solution, "nodes": nodes_expanded, "time": time_s, "peak_kb": peak_kb, "cost": cost}

#RBFS
def rbfs(start):
    tracemalloc.start()
    t0 = time.perf_counter()
    nodes_expanded = 0

    def rbfs_recursive(state, path_set, path_list, g, f_limit):
        nonlocal nodes_expanded
        nodes_expanded += 1
        f = g + manhattan(state)
        if state == goal_state:
            return path_list + [state], 0

        successors = []
        for nb in neighbors(state):
            tnb = to_tuple(nb)
            if tnb in path_set:
                continue
            new_g = g+1
            h = manhattan(nb)
            f_cost = max(new_g + h, f)
            successors.append([f_cost, nb, new_g, h])

        if not successors:
            return None, math.inf

        while True:
            successors.sort(key=lambda x: x[0])
            best = successors[0]
            best_f, best_state, best_g, best_h = best
            if best_f > f_limit:
                return None, best_f
            alt = successors[1][0] if len(successors) > 1 else math.inf
            path_set.add(to_tuple(best_state))
            result, best_f_new = rbfs_recursive(best_state, path_set, path_list+[state], best_g, min(f_limit, alt))
            path_set.remove(to_tuple(best_state))
            successors[0][0] = best_f_new
            if result is not None:
                return result, 0

    start_set = set([to_tuple(start)])
    solution, _ = rbfs_recursive(start, start_set, [], 0, math.inf)
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_kb = peak/1024.0
    time_s = t1 - t0
    if solution is None:
        return {"solution": None, "nodes": nodes_expanded, "time": time_s, "peak_kb": peak_kb, "cost": None}
    cost = len(solution)-1
    return {"solution": solution, "nodes": nodes_expanded, "time": time_s, "peak_kb": peak_kb, "cost": cost}

def moves_from_solution(solution):
    if not solution:
        return []
    moves = []
    for a,b in zip(solution, solution[1:]):
        ax, ay = find_blank(a)
        bx, by = find_blank(b)
        moved_tile = a[bx][by]
        moves.append(moved_tile)
    return moves

if __name__ == "__main__":
    start = [[1,2,3],
             [4,0,6],
             [7,5,8]]

    a_res = astar(start)
    rbfs_res = rbfs(start)

    # A*
    print("A* Solution:")
    if a_res["solution"]:
        for s in a_res["solution"]:
            for row in s:
                print(row)
            print("-----")
    print(f"Nodes Expanded: {a_res['nodes']}")
    print(f"Time Taken: {a_res['time']:.6f} s")
    print(f"Peak Memory: {a_res['peak_kb']:.2f} KB")
    print(f"Solution Cost: {a_res['cost']}")
    print(f"Moves: {moves_from_solution(a_res['solution'])}")

    #RBFS
    print("\nRBFS Solution:")
    if rbfs_res["solution"]:
        for s in rbfs_res["solution"]:
            for row in s:
                print(row)
            print("-----")
    print(f"Nodes Expanded: {rbfs_res['nodes']}")
    print(f"Time Taken: {rbfs_res['time']:.6f} s")
    print(f"Peak Memory: {rbfs_res['peak_kb']:.2f} KB")
    print(f"Solution Cost: {rbfs_res['cost']}")
    print(f"Moves: {moves_from_solution(rbfs_res['solution'])}")

    df = pd.DataFrame([
        {"Algorithm": "A*", "Time_s": a_res["time"], "Nodes_expanded": a_res["nodes"],
         "Peak_memory_KB": a_res["peak_kb"], "Solution_cost": a_res["cost"]},
        {"Algorithm": "RBFS", "Time_s": rbfs_res["time"], "Nodes_expanded": rbfs_res["nodes"],
         "Peak_memory_KB": rbfs_res["peak_kb"], "Solution_cost": rbfs_res["cost"]}
    ])

    print("\nComparison Table:")
    print(df.to_string(index=False))
