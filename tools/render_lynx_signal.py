from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "lynx-banner.jpg"
OUTPUT = ROOT / "assets" / "lynx-signal.gif"

WIDTH = 960
HEIGHT = 300
FRAME_COUNT = 12
FRAME_DURATION_MS = 175


def cover(image: Image.Image, scale: float) -> Image.Image:
    base_scale = max(WIDTH / image.width, HEIGHT / image.height)
    size = (
        round(image.width * base_scale * scale),
        round(image.height * base_scale * scale),
    )
    resized = image.resize(size, Image.Resampling.LANCZOS)

    left = (resized.width - WIDTH) // 2
    top = (resized.height - HEIGHT) // 2
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def eye_glow(frame: Image.Image, intensity: float) -> Image.Image:
    glow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    for x in (608, 722):
        glow_draw.ellipse(
            (x - 18, 162 - 8, x + 18, 162 + 8),
            fill=(233, 166, 72, round(175 * intensity)),
        )

    glow = glow.filter(ImageFilter.GaussianBlur(radius=8))
    return Image.alpha_composite(frame.convert("RGBA"), glow)


def build_palette(image: Image.Image) -> Image.Image:
    sampled = image.quantize(
        colors=71,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )
    colors = sampled.getpalette()[: 71 * 3]
    colors.extend((226, 151, 47))
    colors.extend([0] * (768 - len(colors)))

    palette = Image.new("P", (1, 1))
    palette.putpalette(colors)
    return palette


def render() -> None:
    source = Image.open(SOURCE).convert("RGB")
    rendered: list[Image.Image] = []

    for index in range(FRAME_COUNT):
        phase = index / FRAME_COUNT
        ease = (1 - math.cos(phase * math.tau)) / 2
        frame = cover(source, 1 + 0.012 * ease)

        pulse = 0.70 + 0.30 * ease
        frame = eye_glow(frame, pulse).convert("RGB")

        rendered.append(frame)

    palette = build_palette(rendered[0])
    frames = [
        frame.quantize(palette=palette, dither=Image.Dither.NONE)
        for frame in rendered
    ]

    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )


if __name__ == "__main__":
    render()
