import random
import math

def random_geometric_graph(n, radius=0.2, seed=None):
    if seed is not None:
        random.seed(seed)
    pts = [(random.random(), random.random()) for _ in range(n)]
    G = {i: [] for i in range(n)}
    for i in range(n):
        xi, yi = pts[i]
        for j in range(i+1, n):
            xj, yj = pts[j]
            d = math.hypot(xi-xj, yi-yj)
            if d <= radius:
                G[i].append(j)
                G[j].append(i)
    return G

def is_consistent(node, color, assignment, graph):
    for nb in graph[node]:
        if nb in assignment and assignment[nb] == color:
            return False
    return True

def MRV(assignment, domains):
    unassigned = [v for v in domains.keys() if v not in assignment]
    return min(unassigned, key=lambda v: len(domains[v]))

def LCV(node, assignment, domains, graph):
    def constrained_count(color):
        cnt = 0
        for nb in graph[node]:
            if nb not in assignment and color in domains[nb]:
                cnt += 1
        return cnt
    values = list(domains[node])
    values.sort(key=constrained_count)
    return values

def forward_check(node, color, assignment, domains, graph):
    removed = {}
    for nb in graph[node]:
        if nb in assignment:
            continue
        if color in domains[nb]:
            removed.setdefault(nb, []).append(color)
            domains[nb].remove(color)
            if len(domains[nb]) == 0:
                # revert and fail
                for rnode, vals in removed.items():
                    domains[rnode].extend(vals)
                return False
    return removed

def revert_forward(removed, domains):
    if not removed:
        return
    for node, vals in removed.items():
        domains[node].extend(vals)

def backtrack_coloring(graph, colors):
    domains = {v: list(colors) for v in graph}
    assignment = {}

    def backtrack():
        if len(assignment) == len(graph):
            return assignment.copy()

        var = MRV(assignment, domains)

        for value in LCV(var, assignment, domains, graph):
            if not is_consistent(var, value, assignment, graph):
                continue

            assignment[var] = value

            removed = forward_check(var, value, assignment, domains, graph)
            if removed is not False:
                result = backtrack()
                if result is not None:
                    return result
                revert_forward(removed, domains)

            # undo assignment
            del assignment[var]

        return None

    return backtrack()


if __name__ == "__main__":
    n = 10
    G = random_geometric_graph(n, radius=0.18, seed=42)
    colors = ['R', 'G', 'B', 'Y']   # 4 colors

    print("Graph: n =", n)
    degs = sorted([len(G[v]) for v in G])
    print("Degrees: min", min(degs), "max", max(degs), "avg", sum(degs)/len(degs))

    sol = backtrack_coloring(G, colors)
    if sol is None:
        print("No coloring found with", len(colors), "colors.")
    else:
        print("Coloring found! Example (first 10 nodes):")
        for v in sorted(list(sol.keys())[:10]):
            print(v, "->", sol[v])
