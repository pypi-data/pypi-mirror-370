from dataclasses import dataclass
from .models import LineType, Cardinality


@dataclass
class Edge:
    from_node_id: str
    to_node_id: str
    line_type: LineType = LineType.STRAIGHT
    cardinality: Cardinality = None
    
    def __post_init__(self):
        if self.cardinality is None:
            self.cardinality = Cardinality()

    def render(self, from_x: int, from_y: int, to_x: int, to_y: int, line_type: LineType, from_edge: str = None, to_edge: str = None) -> str:
        def get_perpendicular_point(x, y, edge_type, length):
            """接地面（外枠の辺）に対して垂直に伸ばした点を計算"""
            if edge_type == 'left':      # 左辺から左方向に垂直
                return x - length, y
            elif edge_type == 'right':   # 右辺から右方向に垂直
                return x + length, y
            elif edge_type == 'top':     # 上辺から上方向に垂直
                return x, y - length
            elif edge_type == 'bottom':  # 下辺から下方向に垂直
                return x, y + length
            else:
                return x, y

        def render_ie_notation_symbol(x: int, y: int, cardinality: str, edge_type: str) -> tuple:
            """IE記法でカーディナリティ記号を描画し、新しい接続点を返す"""
            symbols = []
            new_x, new_y = x, y  # デフォルトは元の接続点
            
            if cardinality == "0":
                # "0"の場合は円のみ（円の外から線を出す）
                if edge_type == 'left':
                    circle_x = x - 8
                    symbols.append(f'<circle cx="{circle_x}" cy="{y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    new_x = circle_x - 3  # 円の左端から線を出す
                elif edge_type == 'right':
                    circle_x = x + 8
                    symbols.append(f'<circle cx="{circle_x}" cy="{y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    new_x = circle_x + 3  # 円の右端から線を出す
                elif edge_type == 'top':
                    circle_y = y - 8
                    symbols.append(f'<circle cx="{x}" cy="{circle_y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    new_y = circle_y - 3  # 円の上端から線を出す
                elif edge_type == 'bottom':
                    circle_y = y + 8
                    symbols.append(f'<circle cx="{x}" cy="{circle_y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    new_y = circle_y + 3  # 円の下端から線を出す
            
            elif not cardinality or cardinality == "1":
                # "1"の場合はプラス記号（先端から線を出す）
                if edge_type == 'left':
                    cross_x = x - 8
                    symbols.append(f'<line x1="{cross_x}" y1="{y-4}" x2="{cross_x}" y2="{y+4}" stroke="black" stroke-width="2"/>')
                    symbols.append(f'<line x1="{cross_x-4}" y1="{y}" x2="{cross_x+4}" y2="{y}" stroke="black" stroke-width="2"/>')
                    new_x = cross_x - 4  # 左端から線を出す
                elif edge_type == 'right':
                    cross_x = x + 8
                    symbols.append(f'<line x1="{cross_x}" y1="{y-4}" x2="{cross_x}" y2="{y+4}" stroke="black" stroke-width="2"/>')
                    symbols.append(f'<line x1="{cross_x-4}" y1="{y}" x2="{cross_x+4}" y2="{y}" stroke="black" stroke-width="2"/>')
                    new_x = cross_x + 4  # 右端から線を出す
                elif edge_type == 'top':
                    cross_y = y - 8
                    symbols.append(f'<line x1="{x}" y1="{cross_y-4}" x2="{x}" y2="{cross_y+4}" stroke="black" stroke-width="2"/>')
                    symbols.append(f'<line x1="{x-4}" y1="{cross_y}" x2="{x+4}" y2="{cross_y}" stroke="black" stroke-width="2"/>')
                    new_y = cross_y - 4  # 上端から線を出す
                elif edge_type == 'bottom':
                    cross_y = y + 8
                    symbols.append(f'<line x1="{x}" y1="{cross_y-4}" x2="{x}" y2="{cross_y+4}" stroke="black" stroke-width="2"/>')
                    symbols.append(f'<line x1="{x-4}" y1="{cross_y}" x2="{x+4}" y2="{cross_y}" stroke="black" stroke-width="2"/>')
                    new_y = cross_y + 4  # 下端から線を出す
            
            elif cardinality == "0..1":
                # "0..1"の場合は円 + 縦線
                if edge_type == 'left':
                    circle_x = x - 8
                    line_x = x - 15
                    symbols.append(f'<circle cx="{circle_x}" cy="{y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{line_x}" y1="{y-4}" x2="{line_x}" y2="{y+4}" stroke="black" stroke-width="2"/>')
                    new_x = line_x
                elif edge_type == 'right':
                    circle_x = x + 8
                    line_x = x + 15
                    symbols.append(f'<circle cx="{circle_x}" cy="{y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{line_x}" y1="{y-4}" x2="{line_x}" y2="{y+4}" stroke="black" stroke-width="2"/>')
                    new_x = line_x
                elif edge_type == 'top':
                    circle_y = y - 8
                    line_y = y - 15
                    symbols.append(f'<circle cx="{x}" cy="{circle_y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x-4}" y1="{line_y}" x2="{x+4}" y2="{line_y}" stroke="black" stroke-width="2"/>')
                    new_y = line_y
                elif edge_type == 'bottom':
                    circle_y = y + 8
                    line_y = y + 15
                    symbols.append(f'<circle cx="{x}" cy="{circle_y}" r="3" fill="none" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x-4}" y1="{line_y}" x2="{x+4}" y2="{line_y}" stroke="black" stroke-width="2"/>')
                    new_y = line_y
            
            elif cardinality in ["*", "1..*", "0..*", "0...*", "1...*", "many"]:
                # 多数の場合は鳥の足のみ（枠との間にスペースを設ける）
                if edge_type == 'left':
                    crow_x = x - 12  # テーブル枠外により遠く配置（スペース確保）
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x+8}" y2="{y-5}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x+8}" y2="{y+5}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x+8}" y2="{y}" stroke="black" stroke-width="1"/>')
                    new_x = crow_x
                elif edge_type == 'right':
                    crow_x = x + 12  # テーブル枠外により遠く配置（スペース確保）
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x-8}" y2="{y-5}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x-8}" y2="{y+5}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{crow_x}" y1="{y}" x2="{crow_x-8}" y2="{y}" stroke="black" stroke-width="1"/>')
                    new_x = crow_x
                elif edge_type == 'top':
                    crow_y = y - 12  # テーブル枠外により遠く配置（スペース確保）
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x-5}" y2="{crow_y+8}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x+5}" y2="{crow_y+8}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x}" y2="{crow_y+8}" stroke="black" stroke-width="1"/>')
                    new_y = crow_y
                elif edge_type == 'bottom':
                    crow_y = y + 12  # テーブル枠外により遠く配置（スペース確保）
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x-5}" y2="{crow_y-8}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x+5}" y2="{crow_y-8}" stroke="black" stroke-width="1"/>')
                    symbols.append(f'<line x1="{x}" y1="{crow_y}" x2="{x}" y2="{crow_y-8}" stroke="black" stroke-width="1"/>')
                    new_y = crow_y
            
            return '\n'.join(symbols), new_x, new_y

        # IE記号の位置計算と描画
        from_symbols = ""
        to_symbols = ""
        final_from_x, final_from_y = from_x, from_y
        final_to_x, final_to_y = to_x, to_y

        if self.cardinality:
            # from側のカーディナリティ記号
            if self.cardinality.from_side:
                from_symbols, final_from_x, final_from_y = render_ie_notation_symbol(from_x, from_y, self.cardinality.from_side, from_edge)
            
            # to側のカーディナリティ記号
            if self.cardinality.to_side:
                to_symbols, final_to_x, final_to_y = render_ie_notation_symbol(to_x, to_y, self.cardinality.to_side, to_edge)

        svg_parts = []
        
        if line_type == LineType.STRAIGHT:
            # 直線はIE記号の最終位置まで接続
            svg_parts.append(f'<line x1="{final_from_x}" y1="{final_from_y}" x2="{final_to_x}" y2="{final_to_y}" stroke="black" stroke-width="1"/>')

        elif line_type == LineType.CRANK:
            # 接点から接地面に垂直に伸ばした点を経由するクランク
            from_perp_x, from_perp_y = get_perpendicular_point(final_from_x, final_from_y, from_edge, 30)
            to_perp_x, to_perp_y = get_perpendicular_point(final_to_x, final_to_y, to_edge, 30)

            # シンプルなクランクロジック（Z字回避）
            if from_edge in ['top', 'bottom'] and to_edge in ['top', 'bottom']:
                # 上下辺同士 → from側Y座標で水平線
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = final_to_x, from_perp_y
            elif from_edge in ['left', 'right'] and to_edge in ['left', 'right']:
                # 左右辺同士 → from側X座標で垂直線
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = from_perp_x, final_to_y
            elif from_edge in ['top', 'bottom'] and to_edge in ['left', 'right']:
                # 上下→左右 → 水平線
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = to_perp_x, from_perp_y
            elif from_edge in ['left', 'right'] and to_edge in ['top', 'bottom']:
                # 左右→上下 → 垂直線
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = from_perp_x, to_perp_y
            else:
                # フォールバック
                mid1_x, mid1_y = from_perp_x, from_perp_y
                mid2_x, mid2_y = to_perp_x, to_perp_y

            # クランクパス: 接点→垂直伸ばし→中央線→接点
            if from_edge in ['top', 'bottom'] and to_edge in ['top', 'bottom']:
                # 上下辺同士: from側Y座標の水平線
                svg_parts.append(f'<path d="M {final_from_x} {final_from_y} L {from_perp_x} {from_perp_y} L {mid2_x} {mid2_y} L {final_to_x} {final_to_y}" stroke="black" stroke-width="1" fill="none"/>')
            elif from_edge in ['left', 'right'] and to_edge in ['left', 'right']:
                # 左右辺同士: from側X座標の垂直線
                svg_parts.append(f'<path d="M {final_from_x} {final_from_y} L {from_perp_x} {from_perp_y} L {mid2_x} {mid2_y} L {final_to_x} {final_to_y}" stroke="black" stroke-width="1" fill="none"/>')
            else:
                # 異なる辺同士: 6点パス
                svg_parts.append(f'<path d="M {final_from_x} {final_from_y} L {from_perp_x} {from_perp_y} L {mid1_x} {mid1_y} L {mid2_x} {mid2_y} L {to_perp_x} {to_perp_y} L {final_to_x} {final_to_y}" stroke="black" stroke-width="1" fill="none"/>')

        elif line_type == LineType.SPLINE:
            # 接点から接地面に垂直に伸ばした点を制御点とするスプライン
            from_perp_x, from_perp_y = get_perpendicular_point(final_from_x, final_from_y, from_edge, 50)
            to_perp_x, to_perp_y = get_perpendicular_point(final_to_x, final_to_y, to_edge, 50)

            svg_parts.append(f'<path d="M {final_from_x} {final_from_y} C {from_perp_x} {from_perp_y} {to_perp_x} {to_perp_y} {final_to_x} {final_to_y}" stroke="black" stroke-width="1" fill="none"/>')

        else:
            svg_parts.append(f'<line x1="{final_from_x}" y1="{final_from_y}" x2="{final_to_x}" y2="{final_to_y}" stroke="black" stroke-width="1"/>')

        # IE記号を追加
        if from_symbols:
            svg_parts.append(from_symbols)
        if to_symbols:
            svg_parts.append(to_symbols)

        return '\n'.join(svg_parts)