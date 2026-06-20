from dataclasses import dataclass


@dataclass(slots=True)
class Edge:
    """校园道路边，保存相邻节点编号和不同出行方式下的拥堵系数。"""

    to: int
    distance: float
    bike_factor: float = 1.0
    walk_factor: float = 1.0
    congested: int = 0
