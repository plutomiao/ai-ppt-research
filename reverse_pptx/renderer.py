from __future__ import annotations

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

from .config import BACKGROUND, BOX_FILL, BOX_OUTLINE, SLIDE_SIZE, TITLE_COLOR
from .models import SlideScene


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def title_bbox(scene: SlideScene) -> Tuple[int, int, int, int]:
    image = Image.new("RGB", SLIDE_SIZE)
    draw = ImageDraw.Draw(image)
    font = load_font(scene.title.font_size)
    return draw.textbbox((scene.title.x, scene.title.y), scene.title.text, font=font)


def render_scene(scene: SlideScene, output_path: Path) -> None:
    image = Image.new("RGB", (scene.slide_w, scene.slide_h), BACKGROUND)
    draw = ImageDraw.Draw(image)
    font = load_font(scene.title.font_size)

    draw.rounded_rectangle(scene.box.rect, radius=18, fill=BOX_FILL, outline=BOX_OUTLINE, width=5)
    draw.text((scene.title.x, scene.title.y), scene.title.text, font=font, fill=TITLE_COLOR)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def save_diff_image(reference_path: Path, candidate_path: Path, diff_path: Path) -> float:
    reference = Image.open(reference_path).convert("RGB")
    candidate = Image.open(candidate_path).convert("RGB")
    diff = ImageChops.difference(reference, candidate)
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff.save(diff_path)
    stat = ImageStat.Stat(diff.convert("L"))
    return stat.mean[0] / 255.0
