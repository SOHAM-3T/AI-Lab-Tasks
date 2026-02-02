# ֎ AI Algorithms Guide

This repository contains a collection of Artificial Intelligence algorithms implemented in Python, organized by "Tasks". These implementations cover a wide range of topics including Search Strategies, Constraint Satisfaction Problems (CSPs), Adversarial Search, Logic, and Probabilistic Reasoning (Bayesian Networks).

## ☰ Table of Contents

- [Dependencies](#dependencies)
- [Tasks Overview](#tasks-overview)
- [Usage](#usage)

### 🖇️ Dependencies

The project relies on the following Python packages. You can install them using `pip`:

```bash
pip install numpy pandas scipy networkx tabulate psutil
```

### 🗹 Tasks Overview

The codebase is structured into numbered Task folders, each focusing on specific AI concepts:

| Task | Topic | Algorithms / Description | Key Files |
| :--- | :--- | :--- | :--- |
| **Task 1** | Graph Search | **BFS, DFS, UCS, IDS** (Iterative Deepening Search). Implementation of standard uninformed and informed search algorithms on dense graphs. | `TASK 1/` |
| **Task 2** | Heuristic Search | **A\*, RBFS** (Recursive Best-First Search). Solving the 8-Puzzle problem using Manhattan distance heuristic. | `TASK 2/` |
| **Task 3** | Local Search | **Hill Climbing** (with Random Restarts). Applied to **8-Queens**, **8-Puzzle**, and **TSP** (Traveling Salesperson Problem). | `TASK 3/` |
| **Task 4** | CSP | **Backtracking Search** for **Graph Coloring**. Includes MRV (Minimum Remaining Values), LCV (Least Constraining Value) heuristics, and Forward Checking. | `TASK 4/` |
| **Task 5** | Adv. Search / CSP | **Sudoku Solver**. Compares Backjumping vs. Backjumping with Heuristics (MRV + LCV). | `TASK 5/` |
| **Task 6** | Logic | **Propositional Logic Resolution**. A theorem prover using CNF conversion and resolution refutation. | `TASK 6/` |
| **Task 7** | Adversarial Search | **Tic-Tac-Toe** AI. Implements **Minimax** and **Alpha-Beta Pruning**. | `TASK 7/` |
| **Task 8** | Logic | **First-Order Logic**. Implements **Forward Chaining** with unification and substitutions. | `TASK 8/` |
| **Task 9** | Bayesian Networks | **Exact Inference**. Enumeration algorithm for answering queries on a Bayes Net (Burglary/Alarm example). | `TASK 9/` |
| **Task 10** | Bayesian Networks | **Approximate Inference**. Sampling methods: **Prior Sampling, Rejection Sampling, Likelihood Weighting, Gibbs Sampling**. | `TASK 10/` |

### ⚙ Usage

Each lab task can be run independently. Navigate to the specific directory or run the scripts from the root.

**Example: Running the 8-Puzzle Solver (Task 2)**

```bash
python "TASK 2/task_2.1.py"
```

**Example: Running the Tic-Tac-Toe AI (Task 7)**

```bash
python "TASK 7/task_7.py"
```
*Follow the on-screen prompts to choose between Minimax or Alpha-Beta.*
</br>
</br>
##### "Guide created by Soham Tripathy 👨🏻‍💻"
###### for contact mail 423194@student.nitandhra.ac.in