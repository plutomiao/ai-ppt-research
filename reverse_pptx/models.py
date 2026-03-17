from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Tuple


@dataclass
class TextElement:
    text: str
    x: int
    y: int
    font_size: int = 54


@dataclass
class RectangleElement:
    x: int
    y: int
    w: int
    h: int

    @property
    def rect(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)


@dataclass
class SlideScene:
    title: TextElement
    box: RectangleElement
    slide_w: int
    slide_h: int

    def clone(self) -> "SlideScene":
        return replace(
            self,
            title=replace(self.title),
            box=replace(self.box),
        )
