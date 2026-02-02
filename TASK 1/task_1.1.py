import random
import time
from collections import deque
import heapq
from tabulate import tabulate
import statistics

def generate_dense_graph(num_nodes, min_weight=1, max_weight=10, density=0.7):
    graph = {i: [] for i in range(num_nodes)}
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < density:
                weight = random.randint(min_weight, max_weight)
                graph[i].append((j, weight))
                graph[j].append((i, weight))
    return graph


def is_connected(graph):
    if not graph:
        return False

    start = next(iter(graph))
    visited = set()
    queue = [start]
    visited.add(start)

    while queue:
        node = queue.pop(0)
        for neighbor, _ in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return len(visited) == len(graph)


def calculate_path_cost(graph, path):
    if len(path) < 2:
        return 0

    total_cost = 0
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        for neighbor, weight in graph[current_node]:
            if neighbor == next_node:
                total_cost += weight
                break

    return total_cost


def bfs(graph, start, goal):
    visited = set()
    queue = deque([(start, [start])])
    nodes_generated = 0
    start_time = time.time()

    while queue:
        node, path = queue.popleft()
        nodes_generated += 1

        if node == goal:
            path_cost = calculate_path_cost(graph, path)
            return path, nodes_generated, time.time() - start_time, path_cost

        if node not in visited:
            visited.add(node)
            for neighbor, _ in graph[node]:
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

    return [], nodes_generated, time.time() - start_time, float('inf')


def dfs(graph, start, goal):
    visited = set()
    stack = [(start, [start])]
    nodes_generated = 0
    start_time = time.time()

    while stack:
        node, path = stack.pop()
        nodes_generated += 1

        if node == goal:
            path_cost = calculate_path_cost(graph, path)
            return path, nodes_generated, time.time() - start_time, path_cost

        if node not in visited:
            visited.add(node)
            for neighbor, _ in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

    return [], nodes_generated, time.time() - start_time, float('inf')


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
        if neighbor not in path:
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
            path_cost = calculate_path_cost(graph, path)
            return path, nodes_generated, time.time() - start_time, path_cost

    return [], nodes_generated, time.time() - start_time, float('inf')


def run_single_test(graph, start, goal):
    results = {}
    # BFS
    try:
        bfs_path, bfs_nodes, bfs_time, bfs_cost = bfs(graph, start, goal)
        results['BFS'] = {
            'path_length': len(bfs_path) if bfs_path else 0,
            'nodes_generated': bfs_nodes,
            'time': bfs_time,
            'cost': bfs_cost,
            'found': len(bfs_path) > 0
        }
    except Exception as e:
        print(f"BFS failed: {e}")
        results['BFS'] = {'path_length': 0, 'nodes_generated': 0, 'time': 0, 'cost': float('inf'), 'found': False}

    try:
        dfs_path, dfs_nodes, dfs_time, dfs_cost = dfs(graph, start, goal)
        results['DFS'] = {
            'path_length': len(dfs_path) if dfs_path else 0,
            'nodes_generated': dfs_nodes,
            'time': dfs_time,
            'cost': dfs_cost,
            'found': len(dfs_path) > 0
        }
    except Exception as e:
        print(f"DFS failed: {e}")
        results['DFS'] = {'path_length': 0, 'nodes_generated': 0, 'time': 0, 'cost': float('inf'), 'found': False}

    try:
        ucs_path, ucs_nodes, ucs_time, ucs_cost = ucs(graph, start, goal)
        results['UCS'] = {
            'path_length': len(ucs_path) if ucs_path else 0,
            'nodes_generated': ucs_nodes,
            'time': ucs_time,
            'cost': ucs_cost,
            'found': len(ucs_path) > 0
        }
    except Exception as e:
        print(f"UCS failed: {e}")
        results['UCS'] = {'path_length': 0, 'nodes_generated': 0, 'time': 0, 'cost': float('inf'), 'found': False}

    try:
        ids_path, ids_nodes, ids_time, ids_cost = ids(graph, start, goal, max_depth=50)
        results['IDS'] = {
            'path_length': len(ids_path) if ids_path else 0,
            'nodes_generated': ids_nodes,
            'time': ids_time,
            'cost': ids_cost,
            'found': len(ids_path) > 0
        }
    except Exception as e:
        print(f"IDS failed: {e}")
        results['IDS'] = {'path_length': 0, 'nodes_generated': 0, 'time': 0, 'cost': float('inf'), 'found': False}

    return results


def run_multiple_tests(graph, num_tests=10):
    all_results = {
        'BFS': {'path_lengths': [], 'nodes_generated': [], 'times': [], 'costs': [], 'success_rate': 0},
        'DFS': {'path_lengths': [], 'nodes_generated': [], 'times': [], 'costs': [], 'success_rate': 0},
        'UCS': {'path_lengths': [], 'nodes_generated': [], 'times': [], 'costs': [], 'success_rate': 0},
        'IDS': {'path_lengths': [], 'nodes_generated': [], 'times': [], 'costs': [], 'success_rate': 0}
    }

    nodes = list(graph.keys())
    successful_tests = 0

    print(f"Running {num_tests} tests with random start-goal pairs...")

    for test_num in range(num_tests):
        start = random.choice(nodes)
        goal = random.choice([n for n in nodes if n != start])

        print(f"Test {test_num + 1}/{num_tests}: Start={start}, Goal={goal}")
        test_results = run_single_test(graph, start, goal)
        # Check if at least one algorithm found a solution
        if any(result['found'] for result in test_results.values()):
            successful_tests += 1

            for algo, result in test_results.items():
                if result['found']:
                    all_results[algo]['path_lengths'].append(result['path_length'])
                    all_results[algo]['nodes_generated'].append(result['nodes_generated'])
                    all_results[algo]['times'].append(result['time'])
                    all_results[algo]['costs'].append(result['cost'])

    for algo in all_results:
        successful_runs = len(all_results[algo]['path_lengths'])
        all_results[algo]['success_rate'] = (successful_runs / num_tests) * 100

        if successful_runs > 0:
            all_results[algo]['avg_path_length'] = statistics.mean(all_results[algo]['path_lengths'])
            all_results[algo]['avg_nodes_generated'] = statistics.mean(all_results[algo]['nodes_generated'])
            all_results[algo]['avg_time'] = statistics.mean(all_results[algo]['times'])
            all_results[algo]['avg_cost'] = statistics.mean(all_results[algo]['costs'])
        else:
            all_results[algo]['avg_path_length'] = 0
            all_results[algo]['avg_nodes_generated'] = 0
            all_results[algo]['avg_time'] = 0
            all_results[algo]['avg_cost'] = float('inf')

    return all_results, successful_tests

if __name__ == "__main__":
    NUM_NODES = 1000
    NUM_TESTS = 10

    print("Generating connected dense graph...")
    attempts = 0
    while True:
        attempts += 1
        graph = generate_dense_graph(NUM_NODES, density=0.8)
        if is_connected(graph):
            print(f"Connected graph generated after {attempts} attempt(s)")
            break
        print(f"Attempt {attempts}: Graph not connected, regenerating...")

        if attempts > 50:
            print("Warning: Too many attempts, reducing density...")
            graph = generate_dense_graph(NUM_NODES, density=0.9)
            if is_connected(graph):
                break

    results, successful_tests = run_multiple_tests(graph, NUM_TESTS)

    table_data = []
    for algo in ['BFS', 'DFS', 'UCS', 'IDS']:
        result = results[algo]
        table_data.append([
            algo,
            f"{result['avg_path_length']:.1f}",
            f"{result['avg_nodes_generated']:.0f}",
            f"{result['avg_cost']:.1f}" if result['avg_cost'] != float('inf') else "∞",
            f"{result['avg_time']:.4f}s",
            f"{result['success_rate']:.1f}%"
        ])

    print(f"\nSearch Algorithm Performance (Average of {successful_tests} successful tests):")
    print(tabulate(
        table_data,
        headers=["Algorithm", "Avg Path Length", "Avg Nodes Generated", "Avg Cost", "Avg Time", "Success Rate"]
    ))
