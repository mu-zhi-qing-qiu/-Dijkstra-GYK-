from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf
from typing import Literal

from app.graph.campus_graph import CampusGraph
from app.graph.edge import Edge

TravelMode = Literal["walk", "bike"]
TrafficPeriod = Literal["normal", "morning_peak", "lunch_peak", "evening_peak"]
PathStrategy = Literal["distance", "time"]

# 不同交通模式的平均速度，单位：米/秒
MODE_SPEEDS: dict[TravelMode, float] = {
    "walk": 1.4,
    "bike": 4.5,
}

# 不同时段拥堵系数
PERIOD_FACTORS: dict[TrafficPeriod, float] = {
    "normal": 1.0,
    "morning_peak": 1.35,
    "lunch_peak": 1.2,
    "evening_peak": 1.3,
}


@dataclass(slots=True)
class PathResult:
    """最短路径结果，供服务层和接口层复用。"""

    path: list[int]
    total_distance: float
    total_time: float


def _edge_mode_factor(edge: Edge, mode: TravelMode) -> float:
    return edge.bike_factor if mode == "bike" else edge.walk_factor


def calculate_edge_time(edge: Edge, mode: TravelMode, period: TrafficPeriod) -> float:
    speed = MODE_SPEEDS[mode]
    traffic_factor = PERIOD_FACTORS[period] if edge.congested else 1.0
    mode_factor = _edge_mode_factor(edge, mode)
    return edge.distance / speed * traffic_factor * mode_factor


def _edge_weight(edge: Edge, mode: TravelMode, period: TrafficPeriod, strategy: PathStrategy) -> float:
    if strategy == "distance":
        return edge.distance
    return calculate_edge_time(edge, mode, period)


def _rebuild_path(previous_nodes: dict[int, int | None], end: int) -> list[int]:
    path: list[int] = []
    current: int | None = end

    while current is not None:
        path.append(current)
        current = previous_nodes[current]

    path.reverse()
    return path


def find_shortest_path(
    graph: CampusGraph,
    start: int,
    end: int,
    mode: TravelMode,
    period: TrafficPeriod,
    strategy: PathStrategy,
) -> PathResult:
    """使用 Dijkstra 算法查询校园最短路径。"""
    if not graph.has_node(start):
        raise ValueError(f"起点不存在: {start}")
    if not graph.has_node(end):
        raise ValueError(f"终点不存在: {end}")

    distances: dict[int, float] = {node_id: inf for node_id in graph.nodes}
    actual_distances: dict[int, float] = {node_id: inf for node_id in graph.nodes}
    actual_times: dict[int, float] = {node_id: inf for node_id in graph.nodes}
    previous_nodes: dict[int, int | None] = {node_id: None for node_id in graph.nodes}

    distances[start] = 0.0
    actual_distances[start] = 0.0
    actual_times[start] = 0.0

    priority_queue: list[tuple[float, int]] = [(0.0, start)]

    while priority_queue:
        current_weight, current_node = heappop(priority_queue)

        if current_weight > distances[current_node]:
            continue
        if current_node == end:
            break

        for edge in graph.get_neighbors(current_node):
            next_node = edge.to
            edge_weight = _edge_weight(edge, mode, period, strategy)
            new_weight = current_weight + edge_weight

            if new_weight < distances[next_node]:
                distances[next_node] = new_weight
                actual_distances[next_node] = actual_distances[current_node] + edge.distance
                actual_times[next_node] = actual_times[current_node] + calculate_edge_time(edge, mode, period)
                previous_nodes[next_node] = current_node
                heappush(priority_queue, (new_weight, next_node))

    if distances[end] == inf:
        raise ValueError(f"无法从 {start} 到达 {end}")

    return PathResult(
        path=_rebuild_path(previous_nodes, end),
        total_distance=actual_distances[end],
        total_time=actual_times[end],
    )
