from pathlib import Path

from PIL import Image

from vpe.eval import HumanEvalItem, compare_images, export_human_eval


def test_compare_images_similarity(tmp_path: Path) -> None:
    left = tmp_path / "left.png"
    right = tmp_path / "right.png"
    Image.new("RGB", (8, 8), "red").save(left)
    Image.new("RGB", (8, 8), "red").save(right)

    result = compare_images(left, right, image_size=8)

    assert result.mae == 0
    assert result.similarity == 1


def test_export_human_eval(tmp_path: Path) -> None:
    csv_path, json_path = export_human_eval(
        [
            HumanEvalItem(
                sample_id="sample-1",
                candidate_a="baseline.png",
                candidate_b="vpe.png",
                garment_category="shirt",
                brand_id="demo",
            )
        ],
        tmp_path,
    )

    assert csv_path.exists()
    assert json_path.exists()
    assert "candidate_a" in csv_path.read_text(encoding="utf-8")
