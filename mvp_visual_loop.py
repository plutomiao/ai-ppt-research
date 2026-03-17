from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

#import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont


PREFERRED_MODEL_NAME = "models/gemini-1.5-flash"
FALLBACK_MODEL_NAMES = [
    "models/gemini-2.0-flash-lite",
    "models/gemini-flash-lite-latest",
    "models/gemini-2.0-flash",
]
MAX_ITERATIONS = 5
SLIDE_SIZE = (1280, 720)
BACKGROUND = (248, 249, 252)
TITLE_COLOR = (24, 26, 27)
BOX_FILL = (225, 234, 252)
BOX_OUTLINE = (41, 98, 255)
GUIDE_COLOR = (180, 188, 204)


@dataclass
class SlideState:
    title: str
    title_x: int
    title_y: int
    box_x: int
    box_y: int
    box_w: int
    box_h: int
    slide_w: int = SLIDE_SIZE[0]
    slide_h: int = SLIDE_SIZE[1]

    @property
    def box_rect(self) -> Tuple[int, int, int, int]:
        return (self.box_x, self.box_y, self.box_x + self.box_w, self.box_y + self.box_h)


def load_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, 54)
        except OSError:
            continue
    return ImageFont.load_default()


FONT = load_font()
_RESOLVED_MODEL_NAME: str | None = None


def title_bbox(state: SlideState) -> Tuple[int, int, int, int]:
    probe = Image.new("RGB", (state.slide_w, state.slide_h))
    draw = ImageDraw.Draw(probe)
    left, top, right, bottom = draw.textbbox((state.title_x, state.title_y), state.title, font=FONT)
    return (left, top, right, bottom)


def rects_intersect(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> bool:
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def render_slide(state: SlideState, output_path: Path) -> None:
    image = Image.new("RGB", (state.slide_w, state.slide_h), BACKGROUND)
    draw = ImageDraw.Draw(image)

    center_x = state.box_x + state.box_w // 2
    draw.line((center_x, 80, center_x, state.slide_h - 80), fill=GUIDE_COLOR, width=2)
    draw.rounded_rectangle(state.box_rect, radius=18, fill=BOX_FILL, outline=BOX_OUTLINE, width=5)
    draw.text((state.title_x, state.title_y), state.title, font=FONT, fill=TITLE_COLOR)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def local_geometry_validator(state: SlideState) -> Dict[str, object]:
    title_rect = title_bbox(state)
    box_rect = state.box_rect
    title_center_x = (title_rect[0] + title_rect[2]) // 2
    box_center_x = (box_rect[0] + box_rect[2]) // 2

    if rects_intersect(title_rect, box_rect):
        move_up = title_rect[3] - box_rect[1] + 50
        return {
            "aligned": False,
            "feedback": f"Title overlaps with the box. Move title up by {move_up}px.",
        }

    center_delta = box_center_x - title_center_x
    if abs(center_delta) > 8:
        direction = "right" if center_delta > 0 else "left"
        return {
            "aligned": False,
            "feedback": f"Title is not centered over the box. Move title {direction} by {abs(center_delta)}px.",
        }

    gap = box_rect[1] - title_rect[3]
    if gap < 36:
        move_up = 36 - gap
        return {
            "aligned": False,
            "feedback": f"Title is too close to the box. Move title up by {move_up}px.",
        }

    return {
        "aligned": True,
        "feedback": "Title is centered above the box with healthy spacing. Layout passes visual validation.",
    }


def _extract_json(text: str) -> Dict[str, object]:
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    payload = fenced.group(1) if fenced else text.strip()
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Gemini returned non-JSON content: {text}") from exc


def gemini_flash_validator(image_path: Path) -> Dict[str, object]:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY / GOOGLE_API_KEY for Gemini validation.")

    genai.configure(api_key=api_key)
    prompt = """
You are a strict slide layout validator.
Look at the slide image and decide whether the title is correctly placed relative to the blue box.

Return JSON only with this schema:
{
  "aligned": true | false,
  "feedback": "short imperative instruction"
}

Rules:
- aligned=true only if the title is clearly above the box, not overlapping, and horizontally centered over the box.
- If not aligned, feedback must contain one concrete move instruction in pixels.
- Allowed feedback patterns:
  - "Title overlaps with the box. Move title up by Npx."
  - "Title is not centered over the box. Move title left by Npx."
  - "Title is not centered over the box. Move title right by Npx."
  - "Title is too close to the box. Move title up by Npx."
- Use small, realistic pixel values.
""".strip()

    with Image.open(image_path) as image:
        response = None
        errors = []
        for model_name in resolve_candidate_models():
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    [prompt, image],
                    generation_config=genai.GenerationConfig(
                        temperature=0,
                        max_output_tokens=120,
                    ),
                )
                cache_resolved_model(model_name)
                break
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{model_name}: {exc}")
                print(f"Gemini model attempt failed: {model_name}")
        if response is None:
            raise RuntimeError("All Gemini Flash model attempts failed:\n" + "\n".join(errors))

    text = getattr(response, "text", "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return _extract_json(text)


def validate_layout(state: SlideState, image_path: Path) -> Dict[str, object]:
    validator_mode = os.getenv("VISUAL_LOOP_VALIDATOR", "gemini").lower()
    if validator_mode == "local":
        return local_geometry_validator(state)

    gemini_result = gemini_flash_validator(image_path)
    geometry_result = local_geometry_validator(state)

    if gemini_result.get("aligned") and geometry_result.get("aligned"):
        return gemini_result

    if geometry_result.get("aligned") and not gemini_result.get("aligned"):
        return {
            "aligned": True,
            "feedback": "Geometry guardrail confirms alignment; stopping instead of spending more Gemini calls.",
        }

    # Gemini is the real judge. Local geometry is used to calibrate the repair
    # step so the loop does not waste budget on tiny corrections.
    if not geometry_result.get("aligned"):
        gemini_result["feedback"] = str(geometry_result["feedback"])
    return gemini_result


def resolve_candidate_models() -> list[str]:
    global _RESOLVED_MODEL_NAME
    if _RESOLVED_MODEL_NAME:
        return [_RESOLVED_MODEL_NAME]

    available = {
        model.name
        for model in genai.list_models()
        if "generateContent" in getattr(model, "supported_generation_methods", [])
    }

    candidates: list[str] = []
    if PREFERRED_MODEL_NAME in available:
        candidates.append(PREFERRED_MODEL_NAME)
    else:
        print(
            f"Preferred model {PREFERRED_MODEL_NAME} is unavailable on 2026-03-17; "
            "trying the cheapest available Flash fallbacks."
        )

    for name in FALLBACK_MODEL_NAMES:
        if name in available:
            candidates.append(name)

    if candidates:
        return candidates

    raise RuntimeError(
        f"No supported low-cost Gemini Flash model available. Tried {PREFERRED_MODEL_NAME} "
        f"and {FALLBACK_MODEL_NAMES}."
    )


def cache_resolved_model(model_name: str) -> None:
    global _RESOLVED_MODEL_NAME
    if _RESOLVED_MODEL_NAME != model_name:
        print(f"Using Gemini judge model: {model_name}")
    _RESOLVED_MODEL_NAME = model_name


def apply_feedback(state: SlideState, feedback: str) -> SlideState:
    updated = SlideState(**state.__dict__)

    move_patterns = [
        (r"move title up by (\d+)px", "y", -1),
        (r"move title down by (\d+)px", "y", 1),
        (r"move title left by (\d+)px", "x", -1),
        (r"move title right by (\d+)px", "x", 1),
    ]

    lowered = feedback.lower()
    matched = False
    for pattern, axis, direction in move_patterns:
        match = re.search(pattern, lowered)
        if not match:
            continue
        matched = True
        amount = int(match.group(1))
        if axis == "x":
            updated.title_x += direction * amount
        else:
            updated.title_y += direction * amount

    if not matched:
        raise RuntimeError(f"Could not parse Gemini feedback into an action: {feedback}")

    return updated


def main() -> None:
    root = Path(__file__).resolve().parent
    outputs = root / "outputs" / "visual-loop"

    state = SlideState(
        title="Quarterly Revenue",
        title_x=360,
        title_y=280,
        box_x=340,
        box_y=240,
        box_w=600,
        box_h=260,
    )

    print("Starting agentic visual loop demo...")
    print(f"Preferred model: {PREFERRED_MODEL_NAME}")
    print(f"Max iterations: {MAX_ITERATIONS}")
    print(f"Output directory: {outputs}")
    print("")

    for round_index in range(MAX_ITERATIONS):
        image_path = outputs / f"iteration_{round_index:02d}.png"
        render_slide(state, image_path)
        result = validate_layout(state, image_path)

        print(f"Round {round_index + 1}")
        print(
            "  Coordinates:",
            {
                "title_x": state.title_x,
                "title_y": state.title_y,
                "box_rect": state.box_rect,
            },
        )
        print(f"  Feedback: {result['feedback']}")
        print(f"  Saved image: {image_path}")

        if result["aligned"]:
            print("")
            print("Visual loop succeeded.")
            return

        new_state = apply_feedback(state, str(result["feedback"]))
        print(
            "  Applying fix:",
            {
                "from": {"title_x": state.title_x, "title_y": state.title_y},
                "to": {"title_x": new_state.title_x, "title_y": new_state.title_y},
            },
        )
        print("")
        state = new_state

    raise RuntimeError(f"Visual loop did not converge within MAX_ITERATIONS={MAX_ITERATIONS}.")


if __name__ == "__main__":
    main()
