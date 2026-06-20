from app.algorithm.dijkstra import PathResult, find_shortest_path
from app.algorithm.floyd import find_shortest_path_by_floyd
from app.graph.campus_graph import CampusGraph
from app.models.request import NavigationRequest
from app.models.response import NavigationResponse


class NavigationService:
    def __init__(self, graph: CampusGraph) -> None:
        self._graph = graph

    def navigate(self, request: NavigationRequest) -> NavigationResponse:
        result = find_shortest_path(
            graph=self._graph,
            start=request.start,
            end=request.end,
            mode=request.mode,
            period=request.period,
            strategy=request.strategy,
        )
        return self._build_response(result)

    def navigate_by_floyd(self, request: NavigationRequest) -> NavigationResponse:
        result = find_shortest_path_by_floyd(
            graph=self._graph,
            start=request.start,
            end=request.end,
            mode=request.mode,
            period=request.period,
            strategy=request.strategy,
        )
        return self._build_response(result)

    def _build_response(self, result: PathResult) -> NavigationResponse:
        return NavigationResponse(
            path=result.path,
            path_names=[self._graph.get_node_name(node_id) for node_id in result.path],
            distance=round(result.total_distance, 2),
            time=round(result.total_time, 2),
        )
