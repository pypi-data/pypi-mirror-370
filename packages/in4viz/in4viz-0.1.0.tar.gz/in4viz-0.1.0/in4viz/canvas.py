from typing import List, Dict, Any, Tuple
from .models import LineType
from .rendering import Edge
from .stencil import Stencil


class Canvas:
    def __init__(self, width: int = 1200, height: int = 800, default_line_type: LineType = LineType.STRAIGHT):
        self.width = width
        self.height = height
        self.default_line_type = default_line_type
        self.nodes: List['Node'] = []
        self.edges: List[Edge] = []
        self.next_position = [50, 50]
        self.column_width = 450
        self.row_height = 200

    def add_node(self, node: 'Node'):
        self.nodes.append(node)

    def add_edge(self, from_node_id: str, to_node_id: str, line_type: LineType = None):
        if line_type is None:
            line_type = self.default_line_type
        edge = Edge(from_node_id, to_node_id, line_type)
        self.edges.append(edge)

    def get_node(self, node_id: str) -> 'Node':
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def _get_node_edge_points(self, from_node: 'Node', to_node: 'Node') -> Tuple[int, int, int, int, str, str]:
        """ステンシル中央に向かって線を引き、外枠で止めるポイントを計算（元の正確な実装）"""
        def get_line_rect_intersection(center_x, center_y, target_x, target_y, rect_x, rect_y, rect_w, rect_h):
            """中央から目標点への線が外枠と交わる最適な点を計算"""
            dx = target_x - center_x
            dy = target_y - center_y

            if dx == 0 and dy == 0:
                return center_x, center_y, 'center'

            # 主方向を判定して適切な辺を選択
            if abs(dx) > abs(dy):
                # 水平方向が主
                if dx > 0:
                    # 右向き → 右辺から出る
                    x = rect_x + rect_w
                    t = (x - center_x) / dx
                    y = center_y + t * dy
                    if rect_y <= y <= rect_y + rect_h:
                        return x, y, 'right'
                else:
                    # 左向き → 左辺から出る
                    x = rect_x
                    t = (x - center_x) / dx
                    y = center_y + t * dy
                    if rect_y <= y <= rect_y + rect_h:
                        return x, y, 'left'
            else:
                # 垂直方向が主
                if dy > 0:
                    # 下向き → 下辺から出る
                    y = rect_y + rect_h
                    t = (y - center_y) / dy
                    x = center_x + t * dx
                    if rect_x <= x <= rect_x + rect_w:
                        return x, y, 'bottom'
                else:
                    # 上向き → 上辺から出る
                    y = rect_y
                    t = (y - center_y) / dy
                    x = center_x + t * dx
                    if rect_x <= x <= rect_x + rect_w:
                        return x, y, 'top'

            # フォールバック：最近傍辺を強制選択
            edges = [
                (rect_x, center_y, 'left'),  # 左辺
                (rect_x + rect_w, center_y, 'right'),  # 右辺
                (center_x, rect_y, 'top'),  # 上辺
                (center_x, rect_y + rect_h, 'bottom')  # 下辺
            ]

            # 境界内にクリップ
            best_edge = None
            min_dist = float('inf')
            for edge_x, edge_y, edge_name in edges:
                clipped_x = max(rect_x, min(rect_x + rect_w, edge_x))
                clipped_y = max(rect_y, min(rect_y + rect_h, edge_y))
                dist = abs(target_x - clipped_x) + abs(target_y - clipped_y)
                if dist < min_dist:
                    min_dist = dist
                    best_edge = (clipped_x, clipped_y, edge_name)

            return best_edge[0], best_edge[1], best_edge[2]

        from_center_x = from_node.x + from_node.width // 2
        from_center_y = from_node.y + from_node.height // 2
        to_center_x = to_node.x + to_node.width // 2
        to_center_y = to_node.y + to_node.height // 2

        # fromノードの外枠交点（中央に向かう線との交点）
        from_x, from_y, from_edge = get_line_rect_intersection(
            from_center_x, from_center_y, to_center_x, to_center_y,
            from_node.x, from_node.y, from_node.width, from_node.height
        )

        # toノードの外枠交点（中央に向かう線との交点）
        to_x, to_y, to_edge = get_line_rect_intersection(
            to_center_x, to_center_y, from_center_x, from_center_y,
            to_node.x, to_node.y, to_node.width, to_node.height
        )

        return int(from_x), int(from_y), int(to_x), int(to_y), from_edge, to_edge

    def render_edges(self) -> List[str]:
        edge_parts = []
        for edge in self.edges:
            from_node = self.get_node(edge.from_node_id)
            to_node = self.get_node(edge.to_node_id)

            if from_node and to_node:
                from_x, from_y, to_x, to_y, from_edge, to_edge = self._get_node_edge_points(from_node, to_node)
                edge_parts.append(edge.render(from_x, from_y, to_x, to_y, edge.line_type, from_edge, to_edge))

        return edge_parts

    def render_arrow_marker(self) -> str:
        return '''<defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7"
                    refX="10" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="black"/>
            </marker>
        </defs>'''


class Node:
    def __init__(self, node_id: str, stencil: Stencil, data: Dict[str, Any], x: int = 0, y: int = 0):
        self.node_id = node_id
        self.stencil = stencil
        self.data = data
        self.x = x
        self.y = y
        self.width = stencil.width
        self.height = self._calculate_height()

    def _calculate_height(self) -> int:
        if hasattr(self.stencil, 'calculate_height'):
            return self.stencil.calculate_height(self.data)
        return self.stencil.height

    def _calculate_width(self) -> int:
        if hasattr(self.stencil, 'get_width'):
            return self.stencil.get_width(self.data)
        return self.stencil.width

    def render(self) -> str:
        return self.stencil.render(self.data, self.x, self.y)