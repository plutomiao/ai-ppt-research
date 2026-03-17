from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

from .config import BACKGROUND, DEFAULT_TITLE, SLIDE_SIZE
from .models import RectangleElement, SlideScene, TextElement


def _find_mask_bounds(mask_pixels):
    xs = []
    ys = []
    for y, row in enumerate(mask_pixels):
        for x, active in enumerate(row):
            if active:
                xs.append(x)
                ys.append(y)
    if not xs:
        raise RuntimeError("Could not detect any active pixels in the target image.")
    return min(xs), min(ys), max(xs), max(ys)


def detect_layout_from_image(image_path: Path, title_text: Optional[str] = None) -> SlideScene:
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    pixels = image.load()

    box_mask = [[False] * width for _ in range(height)]
    background = BACKGROUND

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            bg_distance = abs(r - background[0]) + abs(g - background[1]) + abs(b - background[2])
            if bg_distance < 20:
                continue
            if b > r + 20 and b > g + 10 and b > 150:
                box_mask[y][x] = True

    box_left, box_top, box_right, box_bottom = _find_mask_bounds(box_mask)
    text_mask = [[False] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            if y >= box_top - 10:
                continue
            r, g, b = pixels[x, y]
            bg_distance = abs(r - background[0]) + abs(g - background[1]) + abs(b - background[2])
            if bg_distance < 35:
                continue
            if b > r + 15 and b > g + 10:
                continue
            text_mask[y][x] = True

    text_left, text_top, _, _ = _find_mask_bounds(text_mask)

    return SlideScene(
        title=TextElement(
            text=title_text or DEFAULT_TITLE,
            x=text_left,
            y=text_top,
        ),
        box=RectangleElement(
            x=box_left,
            y=box_top,
            w=box_right - box_left,
            h=box_bottom - box_top,
        ),
        slide_w=width,
        slide_h=height,
    )


def create_reference_target(image_path: Path) -> SlideScene:
    from .renderer import render_scene

    scene = SlideScene(
        title=TextElement(text=DEFAULT_TITLE, x=414, y=130),
        box=RectangleElement(x=340, y=240, w=600, h=260),
        slide_w=SLIDE_SIZE[0],
        slide_h=SLIDE_SIZE[1],
    )
    render_scene(scene, image_path)
    return scene
