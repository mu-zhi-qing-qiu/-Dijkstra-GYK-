from dataclasses import dataclass
from math import inf

from app.algorithm.dijkstra import (
    PathResult,
    PathStrategy,
    TrafficPeriod,
    TravelMode,
    calculate_edge_time,
)
from app.graph.campus_graph import CampusGraph


@dataclass(slots=True)
class FloydResult:
    distance_matrix: list[list[float]]
    next_node_matrix: list[list[int | None]]
    actual_distance_matrix: list[list[float]]
    actual_time_matrix: list[list[float]]
    node_ids: list[int]
    node_to_index: dict[int, int]


def _build_weight(graph: CampusGraph, from_node: int, to_node: int, mode: TravelMode, period: TrafficPeriod, strategy: PathStrategy) -> tuple[float, float, float]:
    for edge in graph.get_neighbors(from_node):
        if edge.to != to_node:
            continue

        edge_time = calculate_edge_time(edge, mode, period)
        weight = edge.distance if strategy == "distance" else edge_time
        return weight, edge.distance, edge_time

    return inf, inf, inf


def _run_floyd(
    graph: CampusGraph,
    mode: TravelMode,
    period: TrafficPeriod,
    strategy: PathStrategy,
) -> FloydResult:
    node_ids = sorted(graph.nodes)
    node_count = len(node_ids)
    node_to_index = {node_id: index for index, node_id in enumerate(node_ids)}

    distance_matrix = [[inf] * node_count for _ in range(node_count)]
    next_node_matrix: list[list[int | None]] = [[None] * node_count for _ in range(node_count)]
    actual_distance_matrix = [[inf] * node_count for _ in range(node_count)]
    actual_time_matrix = [[inf] * node_count for _ in range(node_count)]

    for i in range(node_count):
        distance_matrix[i][i] = 0.0
        next_node_matrix[i][i] = node_ids[i]
        actual_distance_matrix[i][i] = 0.0
        actual_time_matrix[i][i] = 0.0

    for from_node in node_ids:
        from_index = node_to_index[from_node]
        for edge in graph.get_neighbors(from_node):
            to_index = node_to_index[edge.to]
            edge_time = calculate_edge_time(edge, mode, period)
            weight = edge.distance if strategy == "distance" else edge_time

            if weight < distance_matrix[from_index][to_index]:
                distance_matrix[from_index][to_index] = weight
                next_node_matrix[from_index][to_index] = edge.to
                actual_distance_matrix[from_index][to_index] = edge.distance
                actual_time_matrix[from_index][to_index] = edge_time

    for k in range(node_count):
        for i in range(node_count):
            if distance_matrix[i][k] == inf:
                continue
            for j in range(node_count):
                if distance_matrix[k][j] == inf:
                    continue

                new_distance = distance_matrix[i][k] + distance_matrix[k][j]
                if new_distance < distance_matrix[i][j]:
                    distance_matrix[i][j] = new_distance
                    next_node_matrix[i][j] = next_node_matrix[i][k]
                    actual_distance_matrix[i][j] = actual_distance_matrix[i][k] + actual_distance_matrix[k][j]
                    actual_time_matrix[i][j] = actual_time_matrix[i][k] + actual_time_matrix[k][j]

    return FloydResult(
        distance_matrix=distance_matrix,
        next_node_matrix=next_node_matrix,
        actual_distance_matrix=actual_distance_matrix,
        actual_time_matrix=actual_time_matrix,
        node_ids=node_ids,
        node_to_index=node_to_index,
    )


def _rebuild_path(result: FloydResult, start: int, end: int) -> list[int]:
    start_index = result.node_to_index[start]
    end_index = result.node_to_index[end]

    if result.next_node_matrix[start_index][end_index] is None:
        return []

    path = [start]
    current = start

    while current != end:
        current_index = result.node_to_index[current]
        next_node = result.next_node_matrix[current_index][end_index]
        if next_node is None:
            return []
        current = next_node
        path.append(current)

    return path


def find_shortest_path_by_floyd(
    graph: CampusGraph,
    start: int,
    end: int,
    mode: TravelMode,
    period: TrafficPeriod,
    strategy: PathStrategy,
) -> PathResult:
    if not graph.has_node(start):
        raise ValueError(f"起点不存在: {start}")
    if not graph.has_node(end):
        raise ValueError(f"终点不存在: {end}")

    result = _run_floyd(graph=graph, mode=mode, period=period, strategy=strategy)
    start_index = result.node_to_index[start]
    end_index = result.node_to_index[end]

    if result.distance_matrix[start_index][end_index] == inf:
        raise ValueError(f"无法从 {start} 到达 {end}")

    return PathResult(
        path=_rebuild_path(result, start, end),
        total_distance=result.actual_distance_matrix[start_index][end_index],
        total_time=result.actual_time_matrix[start_index][end_index],
    )
