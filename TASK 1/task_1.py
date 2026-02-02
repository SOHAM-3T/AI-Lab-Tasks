import random
import time
from collections import deque
import heapq
from tabulate import tabulate

def generate_dense_graph(num_nodes, min_weight=1, max_weight=10, density=0.7):
    graph = {i: [] for i in range(num_nodes)}
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < density:
                weight = random.randint(min_weight, max_weight)
                graph[i].append((j, weight))
                graph[j].append((i, weight))
    return graph

def bfs(graph, start, goal):
    visited = set()
    queue = deque([(start, [start])])
    nodes_generated = 0
    start_time = time.time()
    while queue:
        node, path = queue.popleft()
        nodes_generated += 1

        if node == goal:
            return path, nodes_generated, time.time() - start_time

        if node not in visited:
            visited.add(node)
            for neighbor, _ in graph[node]:
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
    return [], nodes_generated, time.time() - start_time

def dfs(graph, start, goal):
    visited = set()
    stack = [(start, [start])]
    nodes_generated = 0
    start_time = time.time()

    while stack:
        node, path = stack.pop()
        nodes_generated += 1

        if node == goal:
            return path, nodes_generated, time.time() - start_time

        if node not in visited:
            visited.add(node)
            for neighbor, _ in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))
    return [], nodes_generated, time.time() - start_time

def ucs(graph, start, goal):
    visited = set()
    pq = [(0, start, [start])]
    nodes_generated = 0
    start_time = time.time()

    while pq:
        cost, node, path = heapq.heappop(pq)
        nodes_generated += 1

        if node == goal:
            return path, nodes_generated, time.time() - start_time, cost

        if node not in visited:
            visited.add(node)
            for neighbor, weight in graph[node]:
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor, path + [neighbor]))
    return [], nodes_generated, time.time() - start_time, float('inf')

def dls(graph, node, goal, limit, path, nodes_generated):
    if node == goal:
        return path, True, nodes_generated
    if limit <= 0:
        return None, False, nodes_generated

    for neighbor, _ in graph[node]:
        if neighbor not in path:  # only path-based cycle detection
            nodes_generated += 1
            new_path, found, nodes_generated = dls(
                graph, neighbor, goal, limit - 1, path + [neighbor], nodes_generated
            )
            if found:
                return new_path, True, nodes_generated
    return None, False, nodes_generated

def ids(graph, start, goal, max_depth=50):
    start_time = time.time()
    nodes_generated = 0
    for depth in range(max_depth):
        path, found, nodes_generated = dls(graph, start, goal, depth, [start], nodes_generated)
        if found:
            return path, nodes_generated, time.time() - start_time
    return [], nodes_generated, time.time() - start_time

if __name__ == "__main__":
    NUM_NODES = 1000
    START_NODE = 0
    GOAL_NODE = NUM_NODES - 1

    print("Generating dense graph...")
    graph = generate_dense_graph(NUM_NODES, density=0.8)

    results = []

    bfs_path, bfs_nodes, bfs_time = bfs(graph, START_NODE, GOAL_NODE)
    results.append(["BFS", f"{bfs_path[:3]}...{bfs_path[-1:]}", bfs_nodes, "-", bfs_time])

    dfs_path, dfs_nodes, dfs_time = dfs(graph, START_NODE, GOAL_NODE)
    results.append(["DFS", f"{dfs_path[:3]}...{dfs_path[-1:]}", dfs_nodes, "-", dfs_time])

    ucs_path, ucs_nodes, ucs_time, ucs_cost = ucs(graph, START_NODE, GOAL_NODE)
    results.append(["UCS", f"{ucs_path[:3]}...{ucs_path[-1:]}", ucs_nodes, ucs_cost, ucs_time])

    ids_path, ids_nodes, ids_time = ids(graph, START_NODE, GOAL_NODE, max_depth=50)
    results.append(["IDS", f"{ids_path[:3]}...{ids_path[-1:]}", ids_nodes, "-", ids_time])

    print("\nSearch Algorithm Performance:")
    print(tabulate(
        [[algo, path, nodes, cost, f"{t:.4f}s"] for algo, path, nodes, cost, t in results],
        headers=["Algorithm", "Path", "Nodes Traversed", "Cost", "Time Taken"]
    ))