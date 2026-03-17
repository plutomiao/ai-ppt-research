from __future__ import annotations

from dataclasses import dataclass

from .config import PIXEL_DIFF_THRESHOLD
from .models import SlideScene
from .renderer import title_bbox


@dataclass
class DiffResult:
    converged: bool
    pixel_diff: float
    feedback: str


def evaluate_scene(reference: SlideScene, candidate: SlideScene, pixel_diff: float) -> DiffResult:
    candidate_title_rect = title_bbox(candidate)
    reference_title_rect = title_bbox(reference)

    box_center = reference.box.x + reference.box.w // 2
    candidate_title_center = (candidate_title_rect[0] + candidate_title_rect[2]) // 2
    reference_title_center = (reference_title_rect[0] + reference_title_rect[2]) // 2

    if candidate_title_rect[3] >= reference.box.y:
        move_up = candidate_title_rect[3] - reference.box.y + 30
        return DiffResult(
            converged=False,
            pixel_diff=pixel_diff,
            feedback=f"Title overlaps target box region. Move title up by {move_up}px.",
        )

    center_delta = reference_title_center - candidate_title_center
    if abs(center_delta) > 4:
        direction = "right" if center_delta > 0 else "left"
        return DiffResult(
            converged=False,
            pixel_diff=pixel_diff,
            feedback=f"Title center does not match target. Move title {direction} by {abs(center_delta)}px.",
        )

    vertical_delta = reference.title.y - candidate.title.y
    if abs(vertical_delta) > 4:
        direction = "down" if vertical_delta > 0 else "up"
        return DiffResult(
            converged=False,
            pixel_diff=pixel_diff,
            feedback=f"Title vertical position differs from target. Move title {direction} by {abs(vertical_delta)}px.",
        )

    if pixel_diff > PIXEL_DIFF_THRESHOLD:
        return DiffResult(
            converged=False,
            pixel_diff=pixel_diff,
            feedback=f"Pixel diff {pixel_diff:.4f} is still above threshold {PIXEL_DIFF_THRESHOLD:.4f}.",
        )

    return DiffResult(
        converged=True,
        pixel_diff=pixel_diff,
        feedback="Preview is visually aligned with the reference image and pixel diff is below threshold.",
    )


def repair_scene(reference: SlideScene, candidate: SlideScene) -> SlideScene:
    updated = candidate.clone()
    updated.title.x += reference.title.x - candidate.title.x
    updated.title.y += reference.title.y - candidate.title.y
    return updated
