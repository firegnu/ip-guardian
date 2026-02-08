"""Generate menu bar template icons for IP Guardian.

Normal: outline shield. Abnormal: outline shield with diagonal strikethrough.
"""

from PIL import Image, ImageDraw

SIZE = 44  # @2x for retina
PAD = 4


def _shield_points():
    cx, cy = SIZE // 2, SIZE // 2
    top = PAD
    bottom = top + SIZE - PAD * 2
    left = PAD
    right = SIZE - PAD
    mid_y = top + (SIZE - PAD * 2) * 0.55
    return [
        (cx, top), (right, top + 4), (right, mid_y),
        (cx, bottom), (left, mid_y), (left, top + 4),
    ], cx, cy


def make_allowed():
    """Clean outline shield."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    points, _, _ = _shield_points()
    draw.polygon(points, outline="black", width=3)
    img.save("icons/allowed.png")


def _make_strikethrough(name):
    """Outline shield with diagonal strikethrough."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    points, _, _ = _shield_points()
    draw.polygon(points, outline="black", width=3)
    pad = 2
    draw.line(
        [(SIZE - pad, pad), (pad, SIZE - pad)],
        fill="black", width=3,
    )
    img.save(f"icons/{name}.png")


if __name__ == "__main__":
    make_allowed()
    _make_strikethrough("blocked")
    _make_strikethrough("error")
    _make_strikethrough("unknown")
    print("Icons generated in icons/")
