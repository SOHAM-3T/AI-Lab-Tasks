import time
import sys
import pandas as pd
sys.setrecursionlimit(10000)

N = 9

max_depth_no_heuristic = 0
current_depth_no_heuristic = 0
nodes_no_heuristic = 0

max_depth_heuristic = 0
current_depth_heuristic = 0
nodes_heuristic = 0


def print_board(board):
    for r in range(N):
        row = " ".join(str(x) if x != 0 else "_" for x in board[r])
        print(row)
    print()


def is_valid(board, row, col, num):
    for i in range(N):
        if board[row][i] == num or board[i][col] == num:
            return False
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i][j] == num:
                return False
    return True

def find_empty_cell(board):
    for r in range(N):
        for c in range(N):
            if board[r][c] == 0:
                return r, c
    return None


def solve_sudoku_backjumping(board):
    global current_depth_no_heuristic, max_depth_no_heuristic, nodes_no_heuristic

    empty = find_empty_cell(board)
    if not empty:
        return True

    row, col = empty
    current_depth_no_heuristic += 1
    nodes_no_heuristic += 1
    max_depth_no_heuristic = max(max_depth_no_heuristic, current_depth_no_heuristic)

    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve_sudoku_backjumping(board):
                current_depth_no_heuristic -= 1
                return True
            board[row][col] = 0
    current_depth_no_heuristic -= 1
    return False

def find_mrv_cell(board):
    min_options = 10
    chosen_cell = None

    for r in range(N):
        for c in range(N):
            if board[r][c] == 0:
                possible = [num for num in range(1, 10) if is_valid(board, r, c, num)]
                if len(possible) < min_options:
                    min_options = len(possible)
                    chosen_cell = (r, c, possible)
                if min_options == 1:
                    return chosen_cell
    return chosen_cell


def solve_sudoku_with_heuristics(board):
    global current_depth_heuristic, max_depth_heuristic, nodes_heuristic

    mrv_cell = find_mrv_cell(board)
    if not mrv_cell:
        return True

    row, col, possible_values = mrv_cell
    current_depth_heuristic += 1
    nodes_heuristic += 1
    max_depth_heuristic = max(max_depth_heuristic, current_depth_heuristic)

    # LCV
    def lcv_value(val):
        conflict = 0
        for r in range(N):
            if board[r][col] == 0 and is_valid(board, r, col, val):
                conflict += 1
        for c in range(N):
            if board[row][c] == 0 and is_valid(board, row, c, val):
                conflict += 1
        return conflict

    possible_values.sort(key=lcv_value)

    for num in possible_values:
        board[row][col] = num
        if solve_sudoku_with_heuristics(board):
            current_depth_heuristic -= 1
            return True
        board[row][col] = 0
    current_depth_heuristic -= 1
    return False

def run_without_heuristics(orig_board):
    global max_depth_no_heuristic, current_depth_no_heuristic, nodes_no_heuristic
    max_depth_no_heuristic = 0
    current_depth_no_heuristic = 0
    nodes_no_heuristic = 0

    board_copy = [row[:] for row in orig_board]
    start = time.time()
    solved = solve_sudoku_backjumping(board_copy)
    end = time.time()
    elapsed = end - start
    return {
        "solved": solved,
        "board": board_copy,
        "time_s": elapsed,
        "max_depth": max_depth_no_heuristic,
        "nodes": nodes_no_heuristic,
    }


def run_with_heuristics(orig_board):
    global max_depth_heuristic, current_depth_heuristic, nodes_heuristic
    max_depth_heuristic = 0
    current_depth_heuristic = 0
    nodes_heuristic = 0

    board_copy = [row[:] for row in orig_board]
    start = time.time()
    solved = solve_sudoku_with_heuristics(board_copy)
    end = time.time()
    elapsed = end - start
    return {
        "solved": solved,
        "board": board_copy,
        "time_s": elapsed,
        "max_depth": max_depth_heuristic,
        "nodes": nodes_heuristic,
    }

if __name__ == "__main__":
    sudoku_board = [
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

    print("Original Board:")
    print_board(sudoku_board)

    # without heuristics
    res_no = run_without_heuristics(sudoku_board)
    print("Solved WITHOUT heuristics:" if res_no["solved"] else "No solution found WITHOUT heuristics")
    print_board(res_no["board"])
    print(f"Time Taken: {res_no['time_s']:.6f} sec")
    print(f"Max Recursion Depth (Space Proxy): {res_no['max_depth']}")
    print(f"Recursive Calls (nodes expanded): {res_no['nodes']}\n")

    # with heuristics
    res_yes = run_with_heuristics(sudoku_board)
    print("Solved WITH heuristics:" if res_yes["solved"] else "No solution found WITH heuristics")
    print_board(res_yes["board"])
    print(f"Time Taken: {res_yes['time_s']:.6f} sec")
    print(f"Max Recursion Depth (Space Proxy): {res_yes['max_depth']}")
    print(f"Recursive Calls (nodes expanded): {res_yes['nodes']}\n")

    rows = [
        {
            "Algorithm": "Backjumping (no heuristics)",
            "Solved": res_no["solved"],
            "Time_s": f"{res_no['time_s']:.6f}",
            "MaxDepth": res_no["max_depth"],
            "Nodes": res_no["nodes"],
        },
        {
            "Algorithm": "Backjumping (MRV + LCV)",
            "Solved": res_yes["solved"],
            "Time_s": f"{res_yes['time_s']:.6f}",
            "MaxDepth": res_yes["max_depth"],
            "Nodes": res_yes["nodes"],
        },
    ]

    df = pd.DataFrame(rows)
    print("\nPandas DataFrame view:")
    print(df.to_string(index=False))
