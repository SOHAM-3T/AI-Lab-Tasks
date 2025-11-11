import numpy as np
from scipy.spatial import Delaunay
import networkx as nx
import time
import psutil
import os


class CSP:
    def __init__(self, variables, domains, neighbors):
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors


def is_consistent(var, value, assignment, csp):
    for neighbor in csp.neighbors[var]:
        if neighbor in assignment and assignment[neighbor] == value:
            return False
    return True


def select_unassigned_variable(assignment, csp):
    unassigned = [v for v in csp.variables if v not in assignment]
    return min(unassigned, key=lambda v: len(csp.domains[v]))


def order_domain_values(var, assignment, csp):
    # Least Constraining Value (LCV) heuristic
    def count_constrained(value):
        count = 0
        for neighbor in csp.neighbors[var]:
            if neighbor not in assignment and value in csp.domains[neighbor]:
                count += 1
        return count

    return sorted(csp.domains[var], key=count_constrained)


def inference(var, value, assignment, csp):
    removed = {}
    for neighbor in csp.neighbors[var]:
        if neighbor not in assignment:
            if value in csp.domains[neighbor]:
                if neighbor not in removed:
                    removed[neighbor] = []
                removed[neighbor].append(value)
                csp.domains[neighbor].remove(value)
            if len(csp.domains[neighbor]) == 0:
                return False
    return removed


def revert_inference(removed, csp):
    for neighbor, vals in removed.items():
        for val in vals:
            csp.domains[neighbor].append(val)


def backtrack(assignment, csp):
    if len(assignment) == len(csp.variables):
        return assignment
    var = select_unassigned_variable(assignment, csp)
    for value in order_domain_values(var, assignment, csp):
        if is_consistent(var, value, assignment, csp):
            assignment[var] = value
            removed = inference(var, value, assignment, csp)
            if removed is not False:
                result = backtrack(assignment, csp)
                if result is not None:
                    return result
                revert_inference(removed, csp)
            del assignment[var]
    return None


def backtracking_search(csp):
    return backtrack({}, csp)


def create_coloring_csp(G, colors):
    variables = list(G.nodes())
    domains = {v: colors[:] for v in variables}
    neighbors = {v: list(G.neighbors(v)) for v in variables}
    return CSP(variables, domains, neighbors)


def generate_planar_graph(n):
    points = np.random.rand(n, 2)
    tri = Delaunay(points)
    G = nx.Graph()
    for i in range(n):
        G.add_node(i)
    for simplex in tri.simplices:
        G.add_edge(simplex[0], simplex[1])
        G.add_edge(simplex[0], simplex[2])
        G.add_edge(simplex[1], simplex[2])
    return G


def solve_and_measure(n, colors):
    G = generate_planar_graph(n)
    csp = create_coloring_csp(G, colors)

    process = psutil.Process(os.getpid())
    start_time = time.perf_counter()
    start_mem = process.memory_info().rss / (1024 * 1024)  # MB

    assignment = backtracking_search(csp)

    end_time = time.perf_counter()
    end_mem = process.memory_info().rss / (1024 * 1024)  # MB

    time_taken = end_time - start_time
    mem_used = end_mem - start_mem  # Approximate delta in MB
    success = assignment is not None

    return n, success, time_taken, mem_used

if __name__ == "__main__":
    colors = ['R', 'G', 'B', 'Y']
    sizes = [100, 1000, 10000]

    results = []
    for n in sizes:
        print(f"Running for n={n}...")
        result = solve_and_measure(n, colors)
        results.append(result)

    # Tabulate results
    print("\nResults:")
    print("{:<10} {:<10} {:<15} {:<15}".format("Nodes", "Success", "Time (s)", "Memory (MB)"))
    for n, success, t, m in results:
        print("{:<10} {:<10} {:<15.4f} {:<15.4f}".format(n, success, t, m))