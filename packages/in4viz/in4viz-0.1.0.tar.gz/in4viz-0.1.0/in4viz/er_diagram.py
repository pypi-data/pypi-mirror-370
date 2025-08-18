from typing import List, Dict, Tuple
from .models import LineType, Cardinality, Table, Column
from .canvas import Canvas, Node
from .stencil import TableStencil
from .rendering import Edge


class ERDiagram:
    def __init__(self, default_line_type: LineType = LineType.STRAIGHT):
        self.canvas = Canvas(800, 600, default_line_type)  # 初期値は動的調整で上書きされる
        self.nodes = self.canvas.nodes

    def add_table(self, table: Table, x: int = None, y: int = None) -> str:
        table_id = table.name  # 物理テーブル名をIDとして使用

        stencil = TableStencil()
        
        # Column dataclassをdict形式に変換
        columns_data = []
        for col in table.columns:
            columns_data.append({
                'name': col.name,
                'logical_name': col.logical_name,
                'type': col.type,
                'primary_key': col.primary_key,
                'nullable': col.nullable,
                'foreign_key': col.foreign_key,
                'index': col.index
            })
        
        data = {
            'table_name': table.name,
            'logical_name': table.logical_name,
            'columns': columns_data
        }

        # 幅を事前計算
        temp_node = Node(table_id, stencil, data, 0, 0)
        node_width = temp_node._calculate_width()

        auto_positioned = (x is None or y is None)
        if auto_positioned:
            x, y = self._get_next_position()
            # 幅チェックして改行判定
            if x + node_width > self.canvas.width - 50:
                x = 50
                y += self.canvas.row_height
                self.canvas.next_position = [x, y]

        node = Node(table_id, stencil, data, x, y)
        node.width = node_width
        self.canvas.add_node(node)

        # 次の配置位置を更新（自動配置の場合のみ）
        if auto_positioned:
            self._update_next_position(node_width)

        # キャンバスサイズを調整
        self._adjust_canvas_size_for_current_layout()

        return table_id

    def _get_next_position(self) -> Tuple[int, int]:
        x, y = self.canvas.next_position

        # 前回のノードの幅を考慮
        if self.nodes and x + 400 > self.canvas.width - 50:  # 仮の幅でチェック
            x = 50
            y += self.canvas.row_height

        self.canvas.next_position = [x, y]

        return x, y

    def _update_next_position(self, node_width: int):
        self.canvas.next_position[0] += node_width + 50  # ノード間のマージン

    def get_node(self, node_id: str) -> Node:
        return self.canvas.get_node(node_id)

    def set_node_position(self, node_id: str, x: int, y: int):
        node = self.get_node(node_id)
        if node:
            node.x = x
            node.y = y

    def add_edge(self, from_node_id: str, to_node_id: str, line_type: LineType = None, cardinality: Cardinality = None):
        edge = Edge(from_node_id, to_node_id, line_type or self.canvas.default_line_type, cardinality)
        self.canvas.edges.append(edge)
        # エッジ追加後にレイアウトを最適化
        self._optimize_layout_for_edges()

    def _optimize_layout_for_edges(self):
        """エッジを考慮した上から下、左から右のレイアウト最適化"""
        if not self.canvas.edges:
            # エッジがない場合でもキャンバスサイズを調整
            self._adjust_canvas_size_for_current_layout()
            return

        # エッジの関係から階層を構築
        hierarchy = self._build_hierarchy()

        # 階層に基づいて再配置
        self._arrange_by_hierarchy(hierarchy)

    def _adjust_canvas_size_for_current_layout(self):
        """現在のレイアウトに基づいてキャンバスサイズを調整"""
        if not self.nodes:
            return

        margin = 50
        max_width = 0
        max_height = 0

        for node in self.nodes:
            node_right = node.x + node.width
            node_bottom = node.y + node.height
            max_width = max(max_width, node_right)
            max_height = max(max_height, node_bottom)

        new_width = max_width + margin
        new_height = max_height + margin
        self._update_canvas_size(new_width, new_height)

    def _build_hierarchy(self) -> Dict[int, List[str]]:
        """エッジの関係から階層構造を構築（FK関係では参照元を参照先の近くに配置）"""
        # FK関係の場合は逆方向で考える（参照先 -> 参照元）
        # 各ノードの出次数を計算（逆方向）
        out_degree = {node.node_id: 0 for node in self.nodes}
        for edge in self.canvas.edges:
            out_degree[edge.from_node_id] += 1

        # 逆トポロジカルソートで階層を決定
        hierarchy = {}
        remaining_nodes = set(node.node_id for node in self.nodes)
        level = 0

        while remaining_nodes:
            # 出次数0のノード（最終参照先）を現在のレベルに配置
            current_level = []
            for node_id in list(remaining_nodes):
                if out_degree[node_id] == 0:
                    current_level.append(node_id)
                    remaining_nodes.remove(node_id)

            if not current_level:
                # 循環参照がある場合、残りのノードを次のレベルに
                current_level = list(remaining_nodes)
                remaining_nodes.clear()

            hierarchy[level] = current_level
            level += 1

            # 現在のレベルのノードを参照するノードの出次数を減らす
            for node_id in current_level:
                for edge in self.canvas.edges:
                    if edge.to_node_id == node_id and edge.from_node_id in remaining_nodes:
                        out_degree[edge.from_node_id] -= 1

        return hierarchy

    def _arrange_by_hierarchy(self, hierarchy: Dict[int, List[str]]):
        """階層に基づいてノードを再配置（FK関係のあるノードを隣接配置）"""
        margin_x = 50
        margin_y = 50
        level_width = 350  # レベル間の横間隔

        max_width = 0
        max_height = 0

        # FK関係を特定
        fk_pairs = self._get_fk_relationships()

        # 配置済みノードを追跡
        placed_nodes = set()

        # 全体でのY座標を管理
        global_y = margin_y

        for level, node_ids in hierarchy.items():
            x = margin_x + level * level_width

            for node_id in node_ids:
                if node_id in placed_nodes:
                    continue

                node = self.get_node(node_id)
                if node:
                    # 基本配置
                    node.x = x
                    node.y = global_y
                    placed_nodes.add(node_id)

                    # FK関係の相手ノードを隣接配置
                    current_max_height = node.height  # 現在行の最大高さを追跡
                    adjacent_count = 0  # 隣接配置したノード数

                    for from_node, to_node in fk_pairs:
                        adjacent_node_id = None
                        if from_node == node_id:
                            adjacent_node_id = to_node
                        elif to_node == node_id:
                            adjacent_node_id = from_node

                        if adjacent_node_id and adjacent_node_id not in placed_nodes:
                            adjacent_node = self.get_node(adjacent_node_id)
                            if adjacent_node:
                                if adjacent_count == 0:
                                    # 最初の隣接ノードは右隣に配置
                                    adjacent_x = x + node.width + 50
                                    adjacent_y = global_y
                                    current_max_height = max(current_max_height, adjacent_node.height)
                                else:
                                    # 2つ目以降は下に配置
                                    adjacent_x = x
                                    adjacent_y = global_y + current_max_height + margin_y
                                    # global_yを更新して次のノードが重ならないようにする
                                    global_y = adjacent_y
                                    current_max_height = adjacent_node.height

                                adjacent_node.x = adjacent_x
                                adjacent_node.y = adjacent_y
                                placed_nodes.add(adjacent_node_id)
                                adjacent_count += 1

                                # 隣接ノードのサイズも考慮
                                adj_right = adjacent_node.x + adjacent_node.width
                                adj_bottom = adjacent_node.y + adjacent_node.height
                                max_width = max(max_width, adj_right)
                                max_height = max(max_height, adj_bottom)

                    # 現在行の最大高さ分だけY座標を進める
                    global_y += current_max_height + margin_y

                    # 各ノードの右下座標を計算
                    node_right = node.x + node.width
                    node_bottom = node.y + node.height
                    max_width = max(max_width, node_right)
                    max_height = max(max_height, node_bottom)

        # キャンバスサイズを決定（マージンを追加）
        new_width = max_width + margin_x
        new_height = max_height + margin_y

        # キャンバスサイズを更新
        self._update_canvas_size(new_width, new_height)

    def _get_fk_relationships(self) -> List[Tuple[str, str]]:
        """FK関係のペアを取得"""
        fk_pairs = []
        for edge in self.canvas.edges:
            # エッジの方向を確認（from_node -> to_node がFK関係と仮定）
            fk_pairs.append((edge.from_node_id, edge.to_node_id))
        return fk_pairs

    def _update_canvas_size(self, width: int, height: int):
        """キャンバスサイズを更新"""
        self.canvas.width = width
        self.canvas.height = height

    def render_svg(self) -> str:
        svg_parts = []

        svg_parts.append(f'<svg width="{self.canvas.width}" height="{self.canvas.height}" '
                        f'xmlns="http://www.w3.org/2000/svg">')


        svg_parts.append('<style>')
        svg_parts.append('text { font-family: Arial, sans-serif; }')
        svg_parts.append('</style>')

        svg_parts.append(f'<rect width="{self.canvas.width}" height="{self.canvas.height}" '
                        f'fill="#f8f9fa" stroke="none"/>')

        for node in self.nodes:
            svg_parts.append(node.render())

        # エッジの描画
        edge_parts = self.canvas.render_edges()
        svg_parts.extend(edge_parts)

        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def save_svg(self, output):
        """SVGを出力する
        
        Args:
            output: ファイルパス(str)またはファイルライクオブジェクト
        """
        svg_content = self.render_svg()
        
        if isinstance(output, str):
            # ファイルパスの場合
            with open(output, 'w', encoding='utf-8') as f:
                f.write(svg_content)
        else:
            # ストリームオブジェクトの場合
            output.write(svg_content)