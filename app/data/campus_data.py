from app.graph.campus_graph import CampusGraph

# 地点代码来自项目根目录“学校地图.png”下方抽象图。
# 算法层统一使用连续数字编号，地点代码用于和图片标注对应。
place_codes: dict[str, str] = {
    "西大门": "WG",
    "东大门": "EG",
    "学思苑A": "A",
    "学思苑B": "B",
    "学思苑C": "C",
    "学思苑D": "D",
    "学思苑E": "E",
    "学思苑F": "F",
    "学思苑G": "G",
    "学思苑H": "H",
    "学思苑I": "I",
    "学思苑J": "J",
    "学思苑K": "K",
    "集贤苑A": "AT",
    "集贤苑B": "BT",
    "集贤苑C": "CT",
    "集贤苑D": "DT",
    "集贤苑E": "ET",
    "至善楼": "J1",
    "明德楼": "J2",
    "修齐楼": "J3",
    "治平楼": "J4",
    "格致楼": "S1",
    "博雅楼": "S2S3",
    "笃行楼": "S4",
    "致用楼": "S5",
    "田径场": "Playground",
    "体育综合馆": "PECT",
    "篮球馆": "BR",
    "游泳馆": "ST",
    "学术会议中心": "SMC",
    "学术交流中心": "SCC",
    "大礼堂": "A1",
    "图书馆": "Lib",
    "桃园饭堂": "C1",
    "桃蹊饭堂": "C2",
}
# 地点编号转译：地点代码转换为编号
code_to_id: dict[str, int] = {code: index for index, code in enumerate(place_codes.values())}   # 地点代码转换为编号
places: dict[str, int] = {name: code_to_id[code] for name, code in place_codes.items()}              # 地点名称转换为编号
place_names: dict[int, str] = {node_id: name for name, node_id in places.items()}                    # 地点编号转换为名称
place_id_to_code: dict[int, str] = {node_id: code for code, node_id in code_to_id.items()}           # 地点编号转换为代码

# 边集格式: (起点代码, 终点代码, 距离/km, 受拥堵影响: 1=是 0=否)
# 以 WG→EG 直达距离 1.2km 作为新的校准基准，其余历史距离按 1.2/1.1 比例统一缩放。
# 构建图时距离统一转换为 m。
raw_edges_km: tuple[tuple[str, str, float, int], ...] = (
    # ── 主干道 ────────────────────────
    ("WG", "EG", 1.200, 0),
    ("WG", "J", 0.1, 0),
    ("WG", "J4", 0.1, 1),
    ("WG", "S2S3", 0.545, 0),
    ("EG", "S2S3", 0.382, 0),
    ("EG", "J2", 0.087, 1),
    # ── 学思苑内部 ─────────────────────
    ("A", "B", 0.044, 0),
    ("A", "C1", 0.033, 0),
    ("A", "J1", 0.065, 0),
    ("B", "C", 0.044, 0),
    ("B", "C1", 0.033, 0),
    ("C", "D", 0.044, 0),
    ("D", "E", 0.044, 0),
    ("E", "F", 0.044, 0),
    ("F", "Lib", 0.065, 0),
    ("G", "H", 0.044, 1),
    ("G", "CT", 0.044, 1),
    ("H", "DT", 0.055, 0),
    ("I", "J", 0.044, 0),
    ("I", "ET", 0.055, 1),
    ("I", "J4", 0.165, 1),
    ("I", "C2", 0.033, 0),
    ("J", "K", 0.033, 0),
    ("J", "C2", 0.033, 0),
    ("K", "ET", 0.055, 0),
    # ── 集贤苑内部 ──────────────────────
    ("AT", "BT", 0.044, 1),
    ("AT", "ST", 0.065, 0),
    ("BT", "CT", 0.044, 1),
    ("CT", "S4", 0.055, 1),
    ("DT", "ET", 0.065, 0),
    ("DT", "ST", 0.196, 0),
    ("ET", "SCC", 0.044, 0),
    ("ET", "SMC", 0.044, 0),
    # ── 教学行政区干道 ──────────────────
    ("C2", "J4", 0.115, 1),
    ("J1", "J2", 0.055, 1),
    ("J1", "Lib", 0.105, 1),
    ("J3", "J4", 0.124, 1),
    ("J3", "A1", 0.155, 1),
    ("J3", "SMC", 0.055, 1),
    ("J4", "SCC", 0.055, 1),
    # ── 实验楼周边 ────────────────────
    ("S1", "PECT", 0.044, 0),
    ("S1", "Lib", 0.110, 1),
    ("S1", "S2S3", 0.087, 1),
    ("S1", "A1", 0.065, 1),
    ("S2S3", "S4", 0.527, 1),
    ("S4", "S5", 0.074, 1),
    ("S5", "A1", 0.084, 1),
    # ── 运动场馆 ───────────────────────
    ("Playground", "ST", 0.044, 0),
    ("Playground", "PECT", 0.033, 0),
    ("PECT", "BR", 0.033, 0),
    ("BR", "ST", 0.033, 0),
    ("BR", "Lib", 0.087, 0),
    # ── 学术交流区 ────────────────────
    ("SMC", "SCC", 0.033, 1),
    # ── 二期东侧路线补充 (北线) ───────────
    ("DT", "G", 0.098, 0),
    ("DT", "CT", 0.013, 0),
    ("DT", "BT", 0.153, 0),
    ("DT", "AT", 0.175, 0),
    # ── 二期路线补充 (南线) ─────────────────
    ("J3", "WG", 0.218, 0),
    ("J3", "S2S3", 0.327, 0),
)


def build_campus_graph() -> CampusGraph:
    """初始化校园地图数据，后续可替换为数据库或配置文件加载。"""
    graph = CampusGraph()

    for node_id in sorted(place_names):
        graph.add_vertex(node_id, place_names[node_id])

    added_edges: set[tuple[int, int]] = set()
    for from_code, to_code, distance_km, congested in raw_edges_km:
        from_id = code_to_id[from_code]
        to_id = code_to_id[to_code]
        edge_key = tuple(sorted((from_id, to_id)))

        if edge_key in added_edges:
            continue

        graph.add_edge(from_id, to_id, distance_km * 1000, congested=congested)  #初始化边集
        added_edges.add(edge_key)

    return graph


def list_places() -> list[dict[str, object]]:
    """返回所有地点的编号、名称与代码，供前端选择起终点使用。"""
    return [
        {"id": node_id, "name": place_names[node_id], "code": place_id_to_code[node_id]}
        for node_id in sorted(place_names)
    ]
