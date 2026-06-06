from pathlib import Path

from PIL import Image

from vpe.utils.images import composite_garment, mean_abs_difference


def test_composite_garment(tmp_path: Path) -> None:
    person = Image.new("RGB", (8, 8), "white")
    garment = Image.new("RGB", (8, 8), "red")
    mask = Image.new("L", (8, 8), 255)

    result = composite_garment(person, garment, mask)
    out = tmp_path / "out.png"
    result.save(out)

    assert out.exists()
    assert mean_abs_difference(result, garment) == 0
