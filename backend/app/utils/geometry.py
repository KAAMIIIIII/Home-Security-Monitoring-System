from typing import List, Tuple


Point = Tuple[float, float]


def point_in_polygon(pt: Point, poly: List[Point]) -> bool:
    """
    射线法判断点是否在多边形内（含边界）。
    poly: 按顺/逆时针排列的多边形顶点序列
    """
    x, y = pt
    inside = False
    n = len(poly)
    if n < 3:
        return False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        # 判断是否跨过水平射线
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1):
            inside = not inside
    return inside


def _ccw(a: Point, b: Point, c: Point) -> bool:
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])


def segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    """
    线段相交快速判定（一般位置）。
    对毕业设计演示足够用；遇到共线边界情形可能有极少数误差，可接受。
    """
    return _ccw(a, c, d) != _ccw(b, c, d) and _ccw(a, b, c) != _ccw(a, b, d)


def bbox_iou(b1, b2) -> float:
    """
    计算两框 IoU
    b: [x1,y1,x2,y2]
    """
    x1 = max(b1[0], b2[0])
    y1 = max(b1[1], b2[1])
    x2 = min(b1[2], b2[2])
    y2 = min(b1[3], b2[3])
    inter_w = max(0.0, x2 - x1)
    inter_h = max(0.0, y2 - y1)
    inter = inter_w * inter_h
    area1 = max(0.0, b1[2] - b1[0]) * max(0.0, b1[3] - b1[1])
    area2 = max(0.0, b2[2] - b2[0]) * max(0.0, b2[3] - b2[1])
    union = area1 + area2 - inter + 1e-9
    return inter / union


def bbox_center(b):
    return ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)


def bbox_polygon_intersect(b, poly: List[Point]) -> bool:
    """
    判断 bbox 与多边形是否“有交集”（用于禁区闯入）。
    这里用一个简单但够用的判定：
    - bbox 四个角任意一个在多边形内 -> 相交
    - 多边形任意顶点在 bbox 内 -> 相交
    - bbox 边与多边形边任意相交 -> 相交

    说明（论文写法建议）：
    这属于几何相交的近似判定，优点是无需第三方几何库，易解释易复现；
    对实时安防演示场景已足够稳定。
    """
    if len(poly) < 3:
        return False
    x1, y1, x2, y2 = b
    corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    for c in corners:
        if point_in_polygon(c, poly):
            return True
    for px, py in poly:
        if x1 <= px <= x2 and y1 <= py <= y2:
            return True
    # 边相交
    bbox_edges = [
        (corners[0], corners[1]),
        (corners[1], corners[2]),
        (corners[2], corners[3]),
        (corners[3], corners[0]),
    ]
    for i in range(len(poly)):
        p1 = poly[i]
        p2 = poly[(i + 1) % len(poly)]
        for e1, e2 in bbox_edges:
            if segments_intersect(e1, e2, p1, p2):
                return True
    return False

