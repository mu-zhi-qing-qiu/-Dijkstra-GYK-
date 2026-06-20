from dataclasses import dataclass, field

from app.graph.edge import Edge
from app.graph.node import Node


@dataclass
class CampusGraph:
    """校园无向带权图，使用邻接表作为核心存储结构。"""

    nodes: dict[int, Node] = field(default_factory=dict)
    adjacency_list: dict[int, list[Edge]] = field(default_factory=dict)

    def add_node(self, node_id: int, name: str | None = None) -> None:
        """动态添加校园地点节点。"""
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(id=node_id, name=name or str(node_id))
            self.adjacency_list[node_id] = []

    def add_vertex(self, node_id: int, name: str | None = None) -> None:
        """兼容数据结构课程常见写法的顶点添加方法。"""
        self.add_node(node_id, name)

    def add_edge(
        self,
        from_node: int,
        to_node: int,
        distance: float,
        bike_factor: float = 1.0,
        walk_factor: float = 1.0,
        congested: int = 0,
    ) -> None:
        """动态添加无向道路边。"""
        if distance <= 0:
            raise ValueError("道路距离必须大于 0")

        self.add_node(from_node)
        self.add_node(to_node)

        self.adjacency_list[from_node].append(
            Edge(to=to_node, distance=distance, bike_factor=bike_factor, walk_factor=walk_factor, congested=congested)
        )
        self.adjacency_list[to_node].append(
            Edge(to=from_node, distance=distance, bike_factor=bike_factor, walk_factor=walk_factor, congested=congested)
        )

    def get_neighbors(self, node_id: int) -> list[Edge]:
        """获取指定节点的邻接边。"""
        if node_id not in self.nodes:
            raise KeyError(f"节点不存在: {node_id}")
        return self.adjacency_list[node_id]

    def get_node_name(self, node_id: int) -> str:
        """根据节点编号获取地点名称，供接口展示使用。"""
        if node_id not in self.nodes:
            raise KeyError(f"节点不存在: {node_id}")
        return self.nodes[node_id].name

    def has_node(self, node_id: int) -> bool:
        """判断指定节点是否存在。"""
        return node_id in self.nodes
