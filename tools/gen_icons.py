# -*- coding: utf-8 -*-
"""
生成记账本 tabBar 图标（81x81 透明底 PNG）
纯标准库实现：struct + zlib 手写 PNG 编码
4x 超采样抗锯齿
"""
import os
import struct
import zlib

SIZE = 81
SS = 4  # 超采样倍数
N = SIZE * SS

BLUE = (47, 107, 255, 255)      # 品牌蓝 #2F6BFF
GRAY = (154, 163, 178, 255)     # 未选中灰 #9AA3B2
WHITE = (255, 255, 255, 255)


# ---------- 几何测试（坐标均为 81 空间，内部乘 SS） ----------
def circle(cx, cy, r):
    cx, cy, r = cx * SS, cy * SS, r * SS

    def test(x, y):
        return (x - cx) ** 2 + (y - cy) ** 2 <= r * r
    return test


def ring(cx, cy, r, w):
    cx, cy, r, w = cx * SS, cy * SS, r * SS, w * SS

    def test(x, y):
        d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        return abs(d - r) <= w / 2
    return test


def rrect(x0, y0, x1, y1, r):
    x0, y0, x1, y1, r = x0 * SS, y0 * SS, x1 * SS, y1 * SS, r * SS

    def test(x, y):
        if x < x0 or x > x1 or y < y0 or y > y1:
            return False
        nx = min(max(x, x0 + r), x1 - r)
        ny = min(max(y, y0 + r), y1 - r)
        return (x - nx) ** 2 + (y - ny) ** 2 <= r * r
    return test


def poly(pts):
    pts = [(px * SS, py * SS) for (px, py) in pts]

    def test(x, y):
        inside = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > y) != (yj > y):
                xint = xi + (y - yi) * (xj - xi) / (yj - yi)
                if x < xint:
                    inside = not inside
            j = i
        return inside
    return test


def clip_ymax(test, ymax):
    ymax = ymax * SS
    return lambda x, y: y <= ymax and test(x, y)


# ---------- 渲染 ----------
def render(shapes):
    out = bytearray(SIZE * SIZE * 4)
    total = SS * SS
    for oy in range(SIZE):
        for ox in range(SIZE):
            r = g = b = a = 0
            for sy in range(SS):
                py = oy * SS + sy + 0.5
                for sx in range(SS):
                    px = ox * SS + sx + 0.5
                    col = None
                    for (test, color) in shapes:
                        if col is None or color is not WHITE:
                            if test(px, py):
                                col = color
                    if col is not None:
                        r += col[0]
                        g += col[1]
                        b += col[2]
                        a += col[3]
            i = (oy * SIZE + ox) * 4
            out[i] = r // total
            out[i + 1] = g // total
            out[i + 2] = b // total
            out[i + 3] = a // total
    return out


# ---------- PNG 编码 ----------
def chunk(tag, data):
    return (struct.pack('>I', len(data)) + tag + data
            + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF))


def save_png(path, rgba):
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', SIZE, SIZE, 8, 6, 0, 0, 0)
    raw = bytearray()
    stride = SIZE * 4
    for y in range(SIZE):
        raw.append(0)  # filter: none
        raw.extend(rgba[y * stride:(y + 1) * stride])
    png = sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


# ---------- 图标定义 ----------
def icon_record(color):
    """明细：三行列表（圆点 + 长条）"""
    return [
        (circle(16, 22, 4.5), color),
        (rrect(27, 17.5, 65, 26.5, 4.5), color),
        (circle(16, 40.5, 4.5), color),
        (rrect(27, 36, 59, 45, 4.5), color),
        (circle(16, 59, 4.5), color),
        (rrect(27, 54.5, 65, 63.5, 4.5), color),
    ]


def icon_chart(color):
    """图表：三根圆角柱"""
    return [
        (rrect(13, 47, 26, 66, 5), color),
        (rrect(34, 30, 47, 66, 5), color),
        (rrect(55, 14, 68, 66, 5), color),
    ]


def icon_add(_):
    """记账：蓝色实心圆 + 白色加号（两种状态相同，均为蓝色）"""
    return [
        (circle(40.5, 40.5, 29), BLUE),
        (rrect(24, 36.5, 57, 44.5, 4), WHITE),
        (rrect(36.5, 24, 44.5, 57, 4), WHITE),
    ]


def icon_discover(color):
    """发现：罗盘"""
    return [
        (ring(40.5, 40.5, 26, 5), color),
        (poly([(53, 28), (45.5, 45.5), (28, 53), (35.5, 35.5)]), color),
    ]


def icon_mine(color):
    """我的：人像"""
    return [
        (circle(40.5, 29, 13), color),
        (clip_ymax(circle(40.5, 68, 24), 56), color),
    ]


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'static', 'tab')
    out_dir = os.path.normpath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    icons = {
        'record': icon_record,
        'chart': icon_chart,
        'add': icon_add,
        'discover': icon_discover,
        'mine': icon_mine,
    }
    for name, fn in icons.items():
        save_png(os.path.join(out_dir, name + '.png'), render(fn(GRAY)))
        save_png(os.path.join(out_dir, name + '-active.png'), render(fn(BLUE)))
        print('ok', name)

    print('done ->', out_dir)


if __name__ == '__main__':
    main()
