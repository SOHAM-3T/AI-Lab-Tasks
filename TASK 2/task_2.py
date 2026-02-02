import heapq
import math

goal_state = [[1,2,3],[4,5,6],[7,8,0]]

# Utility to find blank position
def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return None


# Convert state to tuple for hashing
def to_tuple(state):
    return tuple(tuple(row) for row in state)

# Manhattan Distance heuristic
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

# Generate possible moves
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

def astar(start):
    open_set = []
    heapq.heappush(open_set, (manhattan(start), 0, start, []))  # (f,g,state,path)
    visited = set()

    while open_set:
        f,g,state,path = heapq.heappop(open_set)
        if state == goal_state:
            return path+[state]
        visited.add(to_tuple(state))
        for nb in neighbors(state):
            if to_tuple(nb) not in visited:
                new_g = g+1
                new_f = new_g + manhattan(nb)
                heapq.heappush(open_set,(new_f,new_g,nb,path+[state]))
    return None

def rbfs(start):
    def rbfs_recursive(state, path, g, f_limit):
        f = g + manhattan(state)
        if state == goal_state:
            return path+[state], 0

        successors = []
        for nb in neighbors(state):
            if nb not in path:
                new_g = g+1
                successors.append((max(new_g+manhattan(nb), f), nb, new_g))

        if not successors:
            return None, math.inf

        while True:
            successors.sort(key=lambda x:x[0]) # sort by f
            best_f, best_state, best_g = successors[0]
            if best_f > f_limit:
                return None, best_f
            alt = successors[1][0] if len(successors)>1 else math.inf
            result, best_f_new = rbfs_recursive(best_state, path+[state], best_g, min(f_limit, alt))
            successors[0] = (best_f_new, best_state, best_g)
            if result is not None:
                return result, 0

    solution, _ = rbfs_recursive(start, [], 0, math.inf)
    return solution

if __name__ == "__main__":
    start = [[1,2,3],
             [4,0,6],
             [7,5,8]]

    print("A* Solution:")
    sol = astar(start)
    for s in sol:
        for row in s: print(row)
        print("-----")

    print("\nRBFS Solution:")
    sol2 = rbfs(start)
    for s in sol2:
        for row in s: print(row)
        print("-----")
