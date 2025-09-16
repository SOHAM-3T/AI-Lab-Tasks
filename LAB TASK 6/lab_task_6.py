import time
import sys
sys.setrecursionlimit(10000)

N = 9

max_depth_no_heuristic = 0
current_depth_no_heuristic = 0

max_depth_heuristic = 0
current_depth_heuristic = 0


def print_board(board):
    for r in range(N):
        row = " ".join(str(x) if x != 0 else "_" for x in board[r])
        print(row)
    print()


def is_valid(board, row, col, num):
    # Row & column
    for i in range(N):
        if board[row][i] == num or board[i][col] == num:
            return False
    # 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i][j] == num:
                return False
    return True


# Backjumping without Heuristics
def find_empty_cell(board):
    for r in range(N):
        for c in range(N):
            if board[r][c] == 0:
                return r, c
    return None


def solve_sudoku_backjumping(board):
    global current_depth_no_heuristic, max_depth_no_heuristic
    empty = find_empty_cell(board)
    if not empty:
        return True

    row, col = empty
    current_depth_no_heuristic += 1
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


# Backjumping with Heuristics (MRV + LCV)

def find_mrv_cell(board):
    min_options = 10
    chosen_cell = None
    candidates = []

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
    global current_depth_heuristic, max_depth_heuristic
    mrv_cell = find_mrv_cell(board)
    if not mrv_cell:
        return True

    row, col, possible_values = mrv_cell
    current_depth_heuristic += 1
    max_depth_heuristic = max(max_depth_heuristic, current_depth_heuristic)

    # Least Constraining Value heuristic
    def lcv_value(val):
        conflict = 0
        for r in range(N):
            if board[r][col] == 0 and is_valid(board, r, col, val):
                conflict += 1
        for c in range(N):
            if board[row][c] == 0 and is_valid(board, row, c, val):
                conflict += 1
        return conflict

    possible_values.sort(key=lcv_value, reverse=True)

    for num in possible_values:
        board[row][col] = num
        if solve_sudoku_with_heuristics(board):
            current_depth_heuristic -= 1
            return True
        board[row][col] = 0
    current_depth_heuristic -= 1
    return False


# Example Run & Comparison
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

    # --- Without Heuristics ---
    board_copy = [row[:] for row in sudoku_board]
    start = time.time()
    solve_sudoku_backjumping(board_copy)
    end = time.time()
    print("Solved WITHOUT heuristics:")
    print_board(board_copy)
    print(f"Time Taken: {end - start:.6f} sec")
    print(f"Max Recursion Depth (Space Proxy): {max_depth_no_heuristic}\n")

    # --- With Heuristics ---
    board_copy = [row[:] for row in sudoku_board]
    start = time.time()
    solve_sudoku_with_heuristics(board_copy)
    end = time.time()
    print("Solved WITH heuristics:")
    print_board(board_copy)
    print(f"Time Taken: {end - start:.6f} sec")
    print(f"Max Recursion Depth (Space Proxy): {max_depth_heuristic}\n")
