from dataclasses import dataclass


@dataclass(slots=True)
class Node:
    """校园地点节点，id 为图算法编号，name 用于对外展示。"""

    id: int
    name: str
