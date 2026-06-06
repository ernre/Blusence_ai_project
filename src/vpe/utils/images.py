"""Image IO and simple deterministic image operations."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageOps


def load_rgb(path: Path, size: int | None = None) -> Image.Image:
    """Load an image as RGB, optionally resizing to a square."""

    if not path.exists():
        raise FileNotFoundError(f"Image does not exist: {path}")
    image = Image.open(path).convert("RGB")
    if size is not None:
        image = ImageOps.fit(image, (size, size), method=Image.Resampling.BICUBIC)
    return image


def load_mask(path: Path, size: int | None = None) -> Image.Image:
    """Load a mask as single-channel luminance."""

    if not path.exists():
        raise FileNotFoundError(f"Mask does not exist: {path}")
    image = Image.open(path).convert("L")
    if size is not None:
        image = ImageOps.fit(image, (size, size), method=Image.Resampling.NEAREST)
    return image


def composite_garment(person: Image.Image, garment: Image.Image, mask: Image.Image) -> Image.Image:
    """CPU stub compositor used for smoke tests and local development."""

    resized_garment = ImageOps.fit(garment, person.size, method=Image.Resampling.BICUBIC)
    return Image.composite(resized_garment, person, mask)


def mean_abs_difference(left: Image.Image, right: Image.Image) -> float:
    """Return the mean absolute RGB pixel difference in the 0..255 range."""

    diff = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    histogram = diff.histogram()
    total = sum(value * (index % 256) for index, value in enumerate(histogram))
    return total / (left.width * left.height * 3)
