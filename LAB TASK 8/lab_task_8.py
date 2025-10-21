import time
import math

EMPTY = '.'
X = 'X'
O = 'O'

minimax_nodes = 0
alphabeta_nodes = 0

def print_board(b):
    for i in range(0, 9, 3):
        print(' '.join(b[i:i+3]))
    print()

def winner(b):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b1,c in wins:
        if b[a] != EMPTY and b[a] == b[b1] == b[c]:
            return b[a]
    return None

def is_full(b):
    return all(cell != EMPTY for cell in b)


def score_board(b):
    w = winner(b)
    if w == X: return 1
    if w == O: return -1
    if is_full(b): return 0
    return None


def minimax(b, maximizing):
    global minimax_nodes
    minimax_nodes += 1

    s = score_board(b)
    if s is not None:
        return s, None

    if maximizing:
        best_score = -math.inf
        best_move = None
        for i in range(9):
            if b[i] == EMPTY:
                b[i] = X
                sc, _ = minimax(b, False)
                b[i] = EMPTY
                if sc > best_score:
                    best_score, best_move = sc, i
                    if best_score == 1: break
        return best_score, best_move
    else:
        best_score = math.inf
        best_move = None
        for i in range(9):
            if b[i] == EMPTY:
                b[i] = O
                sc, _ = minimax(b, True)
                b[i] = EMPTY
                if sc < best_score:
                    best_score, best_move = sc, i
                    if best_score == -1: break
        return best_score, best_move

def alphabeta(b, maximizing, alpha, beta):
    global alphabeta_nodes
    alphabeta_nodes += 1

    s = score_board(b)
    if s is not None:
        return s, None

    moves = [4] + [i for i in range(9) if i != 4]

    if maximizing:
        best_score = -math.inf
        best_move = None
        for i in moves:
            if b[i] == EMPTY:
                b[i] = X
                sc, _ = alphabeta(b, False, alpha, beta)
                b[i] = EMPTY
                if sc > best_score:
                    best_score, best_move = sc, i
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break
        return best_score, best_move
    else:
        best_score = math.inf
        best_move = None
        for i in moves:
            if b[i] == EMPTY:
                b[i] = O
                sc, _ = alphabeta(b, True, alpha, beta)
                b[i] = EMPTY
                if sc < best_score:
                    best_score, best_move = sc, i
                beta = min(beta, best_score)
                if beta <= alpha:
                    break  # prune
        return best_score, best_move

def human_move(b):
    while True:
        try:
            s = int(input("Your move (1-9): ")) - 1
            if 0 <= s < 9 and b[s] == EMPTY:
                b[s] = O
                return
            print("Invalid or occupied. Try again.")
        except ValueError:
            print("Enter number 1..9.")

def play(use_alphabeta=False):
    global minimax_nodes, alphabeta_nodes
    minimax_nodes = alphabeta_nodes = 0

    board = [EMPTY]*9
    print("Positions:")
    print("1 2 3\n4 5 6\n7 8 9\n")
    print("Computer (X) starts.\n")
    print_board(board)

    start = time.time()
    while True:
        if use_alphabeta:
            _, mv = alphabeta(board, True, -math.inf, math.inf)
            algo = "Alpha-Beta"
        else:
            _, mv = minimax(board, True)
            algo = "Minimax"

        if mv is None:
            pass
        else:
            board[mv] = X
            print(f"{algo} chose {mv+1}")
        print_board(board)

        s = score_board(board)
        if s is not None:
            end = time.time()
            if s == 1: print("Computer (X) wins!")
            elif s == -1: print("Human (O) wins!")
            else: print("-1")  # draw
            print_stats(end - start)
            return

        human_move(board)
        print_board(board)
        s = score_board(board)
        if s is not None:
            end = time.time()
            if s == 1: print("Computer (X) wins!")
            elif s == -1: print("Human (O) wins!")
            else: print("-1")
            print_stats(end - start)
            return

def print_stats(elapsed):
    print("\n--- Stats ---")
    print(f"Time elapsed: {elapsed:.6f} s")
    print(f"Minimax nodes visited: {minimax_nodes}")
    print(f"Alpha-Beta nodes visited: {alphabeta_nodes}")
    if minimax_nodes and alphabeta_nodes:
        red = (1 - alphabeta_nodes / minimax_nodes) * 100
        print(f"Alpha-Beta reduced nodes by: {red:.1f}%")
    print("--------------\n")


if __name__ == "__main__":
    print("Choose AI algorithm: 1) Minimax  2) Alpha-Beta")
    ch = input("Enter 1 or 2: ").strip()
    use_ab = (ch == '2')
    play(use_ab)
