import copy
N = 9

def print_board(board):
    for r in range(N):
        for c in range(N):
            if board[r][c]!=0:
                print(board[r][c], end=' ')
            else:
                print('_', end=' ')
        print()

def is_valid(board, row, col, num):
    for i in range(N):
        if board[row][i] == num or board[i][col] == num:
            return False
    # check 3x3 box
    br, bc = 3 * (row // 3), 3 * (col // 3)
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == num:
                return False
    return True

def find_empty_cell(board):
    for r in range(N):
        for c in range(N):
            if board[r][c] == 0:
                return r, c
    return None

# ---------- BASIC backtracking ----------
def solve_basic(board):
    empty = find_empty_cell(board)
    if not empty:
        return True      # solved
    r, c = empty
    for num in range(1, 10):
        if is_valid(board, r, c, num):
            board[r][c] = num
            if solve_basic(board):
                return True
            board[r][c] = 0
    return False

def candidates(board, row, col):
    return [n for n in range(1, 10) if is_valid(board, row, col, n)]

def find_mrv_cell(board):
    best = None
    best_len = 10
    for r in range(N):
        for c in range(N):
            if board[r][c] != 0:
                continue
            cand = candidates(board, r, c)
            if len(cand) < best_len:
                best_len = len(cand)
                best = (r, c, cand)
                if best_len == 1:
                    return best
    return best

def neighbor_empty_cells(board, row, col):
    neigh = set()
    # row & col
    for i in range(N):
        if board[row][i] == 0 and i != col:
            neigh.add((row, i))
        if board[i][col] == 0 and i != row:
            neigh.add((i, col))
    # box
    br, bc = 3 * (row // 3), 3 * (col // 3)
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == 0 and (i, j) != (row, col):
                neigh.add((i, j))
    return list(neigh)

def lcv_order(board, row, col, cand_list):
    neigh = neighbor_empty_cells(board, row, col)
    scores = []
    for val in cand_list:
        removed = 0
        for (nr, nc) in neigh:
            # compute neighbor's candidates *if* we placed val here
            # a simpler approximation: count if val is in neighbor's current candidates
            if is_valid(board, nr, nc, val):
                # placing val here would *remove* val from neighbor's options
                removed += 1
        scores.append((removed, val))
    scores.sort(key=lambda x: x[0])   # least removed first
    return [v for (_, v) in scores]

# ---------- MRV + LCV backtracking ----------
def solve_mrv_lcv(board):
    mrv = find_mrv_cell(board)
    if not mrv:
        return True   # solved
    r, c, cand = mrv
    # order candidates by LCV
    ordered = lcv_order(board, r, c, cand)
    for num in ordered:
        if is_valid(board, r, c, num):
            board[r][c] = num
            if solve_mrv_lcv(board):
                return True
            board[r][c] = 0
    return False

if __name__ == "__main__":
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    print("Original puzzle:")
    print_board(puzzle)

    # basic solver
    b1 = copy.deepcopy(puzzle)
    ok1 = solve_basic(b1)
    print("Solved by basic backtracking:" if ok1 else "Basic backtracking failed")
    print_board(b1)

    # MRV+LCV solver
    b2 = copy.deepcopy(puzzle)
    ok2 = solve_mrv_lcv(b2)
    print("Solved by MRV+LCV:" if ok2 else "MRV+LCV failed")
    print_board(b2)