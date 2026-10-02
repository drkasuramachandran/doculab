from pathlib import Path
from PIL import Image


def open_rgb(path: Path):
    image = Image.open(path)
    if image.mode in ("RGBA", "LA"):
        background = Image.new("RGB", image.size, "white")
        background.paste(image, mask=image.getchannel("A"))
        return background
    return image.convert("RGB")


def resize_image(path: Path, output: Path, width: int, height: int):
    image = open_rgb(path)
    image.thumbnail((width, height), Image.Resampling.LANCZOS)
    image.save(output, "JPEG", quality=90, optimize=True)


def compress_image(path: Path, output: Path, quality: int):
    image = open_rgb(path)
    image.save(output, "JPEG", quality=quality, optimize=True)


def convert_image(path: Path, output: Path, format: str):
    image = open_rgb(path)
    fmt = format.upper()
    if fmt == "JPG":
        fmt = "JPEG"
    image.save(output, fmt, quality=90 if fmt in ("JPEG", "WEBP") else None)


def image_to_pdf(path: Path, output: Path):
    image = open_rgb(path)
    image.save(output, "PDF", resolution=150.0)
