from __future__ import annotations

from pathlib import Path

from reverse_pptx.config import MAX_ITERATIONS
from reverse_pptx.detector import create_reference_target, detect_layout_from_image
from reverse_pptx.diff_loop import evaluate_scene, repair_scene
from reverse_pptx.git_ops import ImprovementMetrics, maybe_commit_and_pr
from reverse_pptx.pptx_exporter import export_scene_to_pptx
from reverse_pptx.renderer import render_scene, save_diff_image


def main() -> None:
    root = Path(__file__).resolve().parent
    fixtures_dir = root / "fixtures"
    outputs_dir = root / "outputs" / "reverse-pptx-loop"
    target_image = fixtures_dir / "target_slide.png"

    reference_scene = create_reference_target(target_image)
    detected_scene = detect_layout_from_image(target_image, title_text=reference_scene.title.text)

    # Inject synthetic detector noise so the repair loop has real work to do.
    candidate_scene = detected_scene.clone()
    candidate_scene.title.x -= 70
    candidate_scene.title.y += 120

    print("Starting reverse image -> editable PPTX MVP...")
    print(f"Max iterations: {MAX_ITERATIONS}")
    print(f"Target image: {target_image}")
    print("")

    previous_diff = 1.0
    for iteration in range(MAX_ITERATIONS):
        pptx_path = outputs_dir / f"iteration_{iteration:02d}.pptx"
        preview_path = outputs_dir / f"iteration_{iteration:02d}.png"
        diff_path = outputs_dir / f"iteration_{iteration:02d}_diff.png"

        export_scene_to_pptx(candidate_scene, pptx_path)
        render_scene(candidate_scene, preview_path)
        pixel_diff = save_diff_image(target_image, preview_path, diff_path)
        result = evaluate_scene(reference_scene, candidate_scene, pixel_diff)

        print(f"Iteration {iteration + 1}")
        print(
            "  Scene:",
            {
                "title_x": candidate_scene.title.x,
                "title_y": candidate_scene.title.y,
                "box_rect": candidate_scene.box.rect,
            },
        )
        print(f"  Pixel diff: {pixel_diff:.6f}")
        print(f"  Feedback: {result.feedback}")
        print(f"  PPTX: {pptx_path}")
        print(f"  Preview: {preview_path}")
        print(f"  Diff: {diff_path}")

        maybe_commit_and_pr(
            ImprovementMetrics(
                previous_diff=previous_diff,
                current_diff=pixel_diff,
                iterations=iteration + 1,
            )
        )

        if result.converged:
            print("")
            print("Reverse PPTX MVP converged successfully.")
            return

        candidate_scene = repair_scene(reference_scene, candidate_scene)
        previous_diff = pixel_diff
        print("  Repair applied from reference-guided diff loop.")
        print("")

    raise RuntimeError(f"Reverse PPTX MVP did not converge within MAX_ITERATIONS={MAX_ITERATIONS}.")


if __name__ == "__main__":
    main()
