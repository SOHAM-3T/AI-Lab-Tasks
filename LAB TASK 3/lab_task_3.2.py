import heapq
import math

goal_state = [[1, 2, 3],
              [4, 5, 6],
              [7, 8, 0]]

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
                goal_x = (val - 1) // 3
                goal_y = (val - 1) % 3
                dist += abs(i - goal_x) + abs(j - goal_y)
    return dist

def neighbors(state):
    x, y = find_blank(state)
    moves = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = [row[:] for row in state]
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            moves.append(new_state)
    return moves

def astar(start):
    start_t = to_tuple(start)
    start_h = manhattan(start)

    # heap items: (f, g, state, path_list)
    heap = []
    path = []
    heapq.heappush(heap, (start_h, 0, start,path))

    best_g = {start_t: 0}

    while heap:
        f, g, state, path = heapq.heappop(heap)
        st_t = to_tuple(state)

        # stale entry check
        if g != best_g.get(st_t, g):
            continue

        if state == goal_state:
            return path + [state]

        for nb in neighbors(state):
            nb_t = to_tuple(nb)
            new_g = g + 1
            if new_g < best_g.get(nb_t, math.inf):
                best_g[nb_t] = new_g
                new_h = manhattan(nb)
                new_f = new_g + new_h
                heapq.heappush(heap, (new_f, new_g, nb, path + [state]))

    return None

def rbfs(start, max_nodes=1000000):
    start_t = to_tuple(start)
    nodes_visited = [0]

    def rbfs_recursive(state, path_set, path_list, g, f_limit):
        nodes_visited[0] += 1
        if nodes_visited[0] > max_nodes:
            return None, math.inf

        f_state = g + manhattan(state)
        if f_state > f_limit:
            return None, f_state

        if state == goal_state:
            return path_list + [state], f_state

        # build successors: [f, state, g]
        successors = []
        for nb in neighbors(state):
            nb_t = to_tuple(nb)
            if nb_t in path_set:
                continue
            new_g = g + 1
            f_nb = new_g + manhattan(nb)
            successors.append([f_nb, nb, new_g])

        if not successors:
            return None, math.inf

        while True:
            successors.sort(key=lambda x: x[0])
            best_f, best_state, best_g = successors[0]

            if best_f > f_limit:
                return None, best_f

            alt = successors[1][0] if len(successors) > 1 else math.inf

            path_set.add(to_tuple(best_state))
            result, result_f = rbfs_recursive(best_state, path_set, path_list + [state], best_g, min(f_limit, alt))
            path_set.remove(to_tuple(best_state))

            successors[0][0] = result_f

            if result is not None:
                return result, result_f
            # otherwise loop and try again with updated f-values

    solution, _ = rbfs_recursive(start, set([start_t]), [], 0, manhattan(start))
    return solution

# helper to show moves (which tile moved each step)
def moves_from_solution(solution):
    if not solution:
        return []
    moves = []
    for a, b in zip(solution, solution[1:]):
        ax, ay = find_blank(a)
        bx, by = find_blank(b)
        moved_tile = a[bx][by]
        moves.append(moved_tile)
    return moves

# -------------------
# Example usage
# -------------------
if __name__ == "__main__":
    start = [[1, 2, 3],
             [4, 0, 6],
             [7, 5, 8]]

    print("Start:")
    for r in start: print(r)
    print("Goal:")
    for r in goal_state: print(r)
    print("----\nRunning A* ...")
    a_res = astar(start)
    if a_res:
        print(f"A* found solution of cost {len(a_res)-1}")
        for s in a_res:
            for row in s: print(row)
            print("-----")
        print("Moves (tiles moved):", moves_from_solution(a_res))
    else:
        print("A* found no solution")

    print("\nRunning RBFS ...")
    r_res = rbfs(start)
    if r_res:
        print(f"RBFS found solution of cost {len(r_res)-1}")
        for s in r_res:
            for row in s: print(row)
            print("-----")
        print("Moves (tiles moved):", moves_from_solution(r_res))
    else:
        print("RBFS found no solution")
