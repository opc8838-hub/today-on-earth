# -*- coding: utf-8 -*-
"""Render the Today on Earth broadcast-style top overlay.

The sample video renderer keeps footage processing in FFmpeg, but the header
art direction needs softer edges than FFmpeg drawbox/drawtext can produce.
This module creates one transparent 1920x1080 PNG per location segment.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WORK = Path(__file__).resolve().parent
ASSETS_DIR = WORK / "assets"
GLOBE_REFERENCE = ASSETS_DIR / "globe-reference.png"
GPT_OVERLAY_TEMPLATE = ASSETS_DIR / "top-overlay-gpt-alpha.png"

CANVAS_SIZE = (1920, 1080)
PANEL_X = 145
PANEL_Y = 82
PANEL_W = 1675
PANEL_H = 165
PANEL_R = 52

WEATHER_X = PANEL_X + 175
WEATHER_Y = PANEL_Y + 83
WEATHER_W = 1098
WEATHER_H = 56

FONT_REGULAR = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
FONT_LIGHT = Path("C:/Windows/Fonts/msyhl.ttc")
FONT_BRAND = Path("C:/Windows/Fonts/segoeui.ttf")
FONT_BRAND_LIGHT = Path("C:/Windows/Fonts/segoeuil.ttf")

INK = (7, 53, 82, 255)
BLUE = (100, 176, 217, 232)
BLUE_DARK = (72, 145, 190, 238)
WHITE = (255, 255, 255, 255)


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.truetype("arial.ttf", size=size)


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def make_horizontal_gradient(
    size: tuple[int, int],
    left: tuple[int, int, int, int],
    right: tuple[int, int, int, int],
) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    pixels = image.load()
    for x in range(width):
        t = x / max(width - 1, 1)
        color = tuple(round(left[i] * (1 - t) + right[i] * t) for i in range(4))
        for y in range(height):
            pixels[x, y] = color
    return image


def paste_masked(base: Image.Image, layer: Image.Image, xy: tuple[int, int], mask: Image.Image) -> None:
    base.alpha_composite(Image.composite(layer, Image.new("RGBA", layer.size, (0, 0, 0, 0)), mask), xy)


def draw_curve(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    *,
    fill: tuple[int, int, int, int],
    width: int = 1,
    samples: int = 80,
) -> None:
    """Draw a quadratic/cubic Bezier curve from control points."""
    if len(points) == 3:
        coords = []
        for i in range(samples + 1):
            t = i / samples
            x = (1 - t) ** 2 * points[0][0] + 2 * (1 - t) * t * points[1][0] + t**2 * points[2][0]
            y = (1 - t) ** 2 * points[0][1] + 2 * (1 - t) * t * points[1][1] + t**2 * points[2][1]
            coords.append((x, y))
        draw.line(coords, fill=fill, width=width, joint="curve")
        return

    coords = []
    for i in range(samples + 1):
        t = i / samples
        x = (
            (1 - t) ** 3 * points[0][0]
            + 3 * (1 - t) ** 2 * t * points[1][0]
            + 3 * (1 - t) * t**2 * points[2][0]
            + t**3 * points[3][0]
        )
        y = (
            (1 - t) ** 3 * points[0][1]
            + 3 * (1 - t) ** 2 * t * points[1][1]
            + 3 * (1 - t) * t**2 * points[2][1]
            + t**3 * points[3][1]
        )
        coords.append((x, y))
    draw.line(coords, fill=fill, width=width, joint="curve")


def draw_glass_panel(image: Image.Image) -> None:
    shadow = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (PANEL_X + 4, PANEL_Y + 7, PANEL_X + PANEL_W + 4, PANEL_Y + PANEL_H + 7),
        radius=PANEL_R,
        fill=(20, 72, 102, 52),
    )
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16)))

    panel = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
    mask = rounded_mask((PANEL_W, PANEL_H), PANEL_R)
    glass = make_horizontal_gradient(
        (PANEL_W, PANEL_H),
        (255, 255, 255, 218),
        (255, 255, 255, 166),
    )
    paste_masked(panel, glass, (0, 0), mask)

    glow = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rectangle((130, 78, 1320, 132), fill=(90, 190, 232, 38))
    glow_draw.rectangle((0, 78, 980, 132), fill=(55, 159, 208, 32))
    panel.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))

    line = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
    line_draw = ImageDraw.Draw(line)
    line_draw.line((0, 1, PANEL_W - 55, 1), fill=(255, 255, 255, 230), width=2)
    line_draw.line((20, PANEL_H - 2, PANEL_W - 62, PANEL_H - 2), fill=(115, 170, 194, 88), width=2)
    line_draw.rounded_rectangle((0, 0, PANEL_W - 1, PANEL_H - 1), radius=PANEL_R, outline=(255, 255, 255, 120), width=1)
    panel.alpha_composite(line)

    image.alpha_composite(panel, (PANEL_X, PANEL_Y))


def draw_weather_band(image: Image.Image) -> None:
    x = WEATHER_X
    y = WEATHER_Y
    w = WEATHER_W
    h = WEATHER_H
    band = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mask = Image.new("L", (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, w + 34, h - 1), radius=20, fill=255)
    grad = make_horizontal_gradient((w, h), BLUE, (168, 214, 231, 70))
    paste_masked(band, grad, (0, 0), mask)
    band_draw = ImageDraw.Draw(band)
    band_draw.line((0, 1, w - 22, 1), fill=(255, 255, 255, 135), width=1)
    band_draw.line((0, h - 1, w - 44, h - 1), fill=(54, 125, 166, 88), width=1)
    image.alpha_composite(band, (x, y))


def draw_globe(image: Image.Image) -> None:
    cx = PANEL_X + 76
    cy = PANEL_Y + 82
    r = 86

    glow = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((cx - r - 11, cy - r - 11, cx + r + 11, cy + r + 11), fill=(92, 198, 239, 72))
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)))

    if GLOBE_REFERENCE.exists():
        globe = Image.open(GLOBE_REFERENCE).convert("RGBA").resize((178, 178), Image.Resampling.LANCZOS)
        image.alpha_composite(globe, (cx - 89, cy - 89))
        return

    image.alpha_composite(make_globe_icon(r * 2), (cx - r, cy - r))


def make_globe_icon(size: int) -> Image.Image:
    scale = 4
    big = size * scale
    center = big / 2
    radius = big * 0.48

    icon = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((center - radius, center - radius, center + radius, center + radius), fill=255)

    sphere = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    px = sphere.load()
    for y in range(big):
        for x in range(big):
            dx = (x - center) / radius
            dy = (y - center) / radius
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            z = (1 - d2) ** 0.5
            light = max(0, min(1, 0.62 + 0.32 * z - 0.16 * dx - 0.12 * dy))
            rim = max(0, min(1, (d2 - 0.60) / 0.40))
            blue = (
                round(36 + 120 * light + 34 * (1 - rim)),
                round(137 + 92 * light),
                round(190 + 48 * light),
                244,
            )
            px[x, y] = blue
    icon.alpha_composite(sphere)

    draw = ImageDraw.Draw(icon)
    waterline = (226, 249, 255, 116)
    for inset, alpha, width in [(18, 130, 5), (42, 82, 3), (70, 52, 2)]:
        draw.ellipse(
            (inset, inset, big - inset, big - inset),
            outline=(210, 246, 255, alpha),
            width=width,
        )
    for offset, alpha in [(-82, 72), (-30, 55), (38, 45)]:
        draw.arc(
            (big * 0.18, big * 0.18 + offset, big * 0.82, big * 0.82 - offset),
            80,
            280,
            fill=waterline[:3] + (alpha,),
            width=3,
        )

    land = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(land)

    def pts(values: list[tuple[float, float]]) -> list[tuple[int, int]]:
        return [(round(x * big), round(y * big)) for x, y in values]

    main_land = (32, 111, 164, 210)
    soft_land = (32, 111, 164, 166)
    ldraw.polygon(
        pts(
            [
                (0.45, 0.15),
                (0.56, 0.18),
                (0.68, 0.27),
                (0.70, 0.42),
                (0.61, 0.52),
                (0.48, 0.49),
                (0.42, 0.38),
                (0.36, 0.31),
                (0.39, 0.22),
            ]
        ),
        fill=main_land,
    )
    ldraw.polygon(
        pts(
            [
                (0.54, 0.50),
                (0.64, 0.58),
                (0.68, 0.73),
                (0.62, 0.88),
                (0.52, 0.82),
                (0.48, 0.66),
                (0.44, 0.56),
            ]
        ),
        fill=main_land,
    )
    ldraw.polygon(
        pts([(0.26, 0.35), (0.38, 0.40), (0.37, 0.54), (0.26, 0.58), (0.19, 0.48)]),
        fill=soft_land,
    )
    ldraw.polygon(
        pts([(0.67, 0.22), (0.83, 0.30), (0.88, 0.43), (0.77, 0.47), (0.68, 0.38)]),
        fill=(32, 111, 164, 130),
    )
    ldraw.polygon(
        pts([(0.70, 0.48), (0.82, 0.56), (0.83, 0.68), (0.72, 0.66), (0.66, 0.56)]),
        fill=(32, 111, 164, 118),
    )
    land = land.filter(ImageFilter.GaussianBlur(0.55 * scale))
    icon.alpha_composite(Image.composite(land, Image.new("RGBA", land.size, (0, 0, 0, 0)), mask))

    shine = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shine)
    sdraw.ellipse((big * 0.12, big * 0.07, big * 0.58, big * 0.45), fill=(255, 255, 255, 86))
    sdraw.ellipse((big * 0.22, big * 0.14, big * 0.46, big * 0.32), fill=(255, 255, 255, 90))
    shine = shine.filter(ImageFilter.GaussianBlur(14 * scale))
    icon.alpha_composite(Image.composite(shine, Image.new("RGBA", shine.size, (0, 0, 0, 0)), mask))

    rim = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(rim)
    rdraw.ellipse((8, 8, big - 8, big - 8), outline=(248, 255, 255, 230), width=4 * scale)
    rdraw.ellipse((30, 30, big - 30, big - 30), outline=(78, 190, 232, 150), width=2 * scale)
    icon.alpha_composite(rim)

    return icon.resize((size, size), Image.Resampling.LANCZOS)


def draw_icon_thermometer(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x + 9, y, x + 18, y + 29), radius=5, outline=WHITE, width=4)
    draw.ellipse((x + 3, y + 25, x + 24, y + 46), outline=WHITE, width=4)
    draw.line((x + 13, y + 16, x + 13, y + 31), fill=WHITE, width=4)


def draw_icon_wind(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.arc((x, y + 3, x + 38, y + 28), 200, 360, fill=WHITE, width=4)
    draw.line((x, y + 16, x + 53, y + 16), fill=WHITE, width=4)
    draw.arc((x + 24, y + 16, x + 67, y + 43), 195, 355, fill=WHITE, width=4)
    draw.line((x + 10, y + 32, x + 40, y + 32), fill=WHITE, width=4)


def draw_icon_drops(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    def drop(cx: int, cy: int, scale: int) -> None:
        draw.polygon([(cx, cy), (cx - scale, cy + scale + 7), (cx + scale, cy + scale + 7)], fill=WHITE)
        draw.ellipse((cx - scale, cy + scale, cx + scale, cy + scale * 3), fill=WHITE)

    drop(x + 12, y + 4, 7)
    drop(x + 34, y + 14, 8)
    drop(x + 52, y + 0, 6)


def draw_icon_clock(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.ellipse((x, y, x + 42, y + 42), outline=WHITE, width=4)
    draw.line((x + 21, y + 21, x + 21, y + 9), fill=WHITE, width=4)
    draw.line((x + 21, y + 21, x + 32, y + 28), fill=WHITE, width=4)


def fit_text(text: str, font_path: Path, target_size: int, max_width: int) -> ImageFont.FreeTypeFont:
    size = target_size
    while size > 18:
        font = load_font(font_path, size)
        bbox = font.getbbox(text)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 2
    return load_font(font_path, size)


def draw_labels(
    image: Image.Image,
    *,
    city_label: str,
    country_label: str,
    temp_c: int | float,
    wind_kmh: int | float,
    humidity: int | float,
    local_time: str,
) -> None:
    draw = ImageDraw.Draw(image)
    city_font = fit_text(city_label, FONT_BOLD, 41, 245)
    country_font = fit_text(country_label, FONT_BOLD, 41, 310)
    brand_font = load_font(FONT_BRAND if FONT_BRAND.exists() else FONT_REGULAR, 35)
    metric_font = load_font(FONT_REGULAR, 30)

    draw.text((PANEL_X + 220, PANEL_Y + 27), city_label, font=city_font, fill=INK)
    draw.text((PANEL_X + 515, PANEL_Y + 27), country_label, font=country_font, fill=INK)

    metric_y = WEATHER_Y + 16
    icon_y = WEATHER_Y + 11
    columns = [
        (WEATHER_X + 65, WEATHER_X + 118, draw_icon_thermometer, f"{round(float(temp_c))}°C"),
        (WEATHER_X + 292, WEATHER_X + 366, draw_icon_wind, f"{round(float(wind_kmh))} km/h"),
        (WEATHER_X + 560, WEATHER_X + 636, draw_icon_drops, f"{round(float(humidity))}%"),
        (WEATHER_X + 810, WEATHER_X + 870, draw_icon_clock, local_time),
    ]
    for x, value_x, icon, value in columns:
        icon(draw, x, icon_y)
        draw.text((value_x, metric_y), value, font=metric_font, fill=(255, 255, 255, 238))

    brand_x = PANEL_X + PANEL_W - 305
    draw.text((brand_x, PANEL_Y + 74), "Today on Earth", font=brand_font, fill=INK)
    draw_orbit_mark(image, brand_x - 28, PANEL_Y + 27)


def draw_orbit_mark(image: Image.Image, x: int, y: int) -> None:
    mark = Image.new("RGBA", (260, 70), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mark)
    draw_curve(
        draw,
        [(8, 47), (85, 8), (180, 9), (243, 35)],
        fill=(16, 73, 105, 122),
        width=2,
        samples=110,
    )
    draw_curve(
        draw,
        [(40, 40), (110, 18), (170, 18), (222, 32)],
        fill=(85, 145, 172, 92),
        width=1,
        samples=90,
    )
    draw_curve(
        draw,
        [(150, 16), (178, 22), (205, 29), (236, 36)],
        fill=(14, 70, 100, 142),
        width=2,
        samples=50,
    )
    draw.ellipse((174, 17, 182, 25), fill=(24, 116, 164, 230))
    draw.ellipse((172, 15, 184, 27), outline=(255, 255, 255, 120), width=1)
    draw.line((204, 29, 230, 36), fill=(12, 68, 100, 128), width=1)
    image.alpha_composite(mark, (x, y))


def draw_dynamic_labels(
    image: Image.Image,
    *,
    city_label: str,
    country_label: str,
    temp_c: int | float,
    wind_kmh: int | float,
    humidity: int | float,
    local_time: str,
) -> None:
    """Draw only the variable text over the GPT-rendered template asset."""
    draw = ImageDraw.Draw(image)
    city_font = fit_text(city_label, FONT_BOLD, 41, 280)
    country_font = fit_text(country_label, FONT_BOLD, 41, 330)
    brand_font = load_font(FONT_BRAND if FONT_BRAND.exists() else FONT_REGULAR, 35)
    metric_font = load_font(FONT_REGULAR, 30)

    draw.text((PANEL_X + 220, PANEL_Y + 27), city_label, font=city_font, fill=INK)
    draw.text((PANEL_X + 500, PANEL_Y + 27), country_label, font=country_font, fill=INK)

    metric_y = WEATHER_Y + 16
    values = [
        (WEATHER_X + 115, f"{round(float(temp_c))}°C"),
        (WEATHER_X + 365, f"{round(float(wind_kmh))} km/h"),
        (WEATHER_X + 635, f"{round(float(humidity))}%"),
        (WEATHER_X + 870, local_time),
    ]
    for x, value in values:
        draw.text((x, metric_y), value, font=metric_font, fill=(255, 255, 255, 242))

    draw.text((PANEL_X + PANEL_W - 305, PANEL_Y + 74), "Today on Earth", font=brand_font, fill=INK)


def render_overlay(
    output_path: Path,
    *,
    city_label: str = "Tokyo 东京",
    country_label: str = "Japan 日本",
    temp_c: int | float = 17,
    wind_kmh: int | float = 10,
    humidity: int | float = 73,
    local_time: str = "09:55",
) -> Path:
    image = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    if GPT_OVERLAY_TEMPLATE.exists():
        template = Image.open(GPT_OVERLAY_TEMPLATE).convert("RGBA").resize(CANVAS_SIZE, Image.Resampling.LANCZOS)
        image.alpha_composite(template)
        draw_dynamic_labels(
            image,
            city_label=city_label,
            country_label=country_label,
            temp_c=temp_c,
            wind_kmh=wind_kmh,
            humidity=humidity,
            local_time=local_time,
        )
    else:
        draw_glass_panel(image)
        draw_weather_band(image)
        draw_globe(image)
        draw_labels(
            image,
            city_label=city_label,
            country_label=country_label,
            temp_c=temp_c,
            wind_kmh=wind_kmh,
            humidity=humidity,
            local_time=local_time,
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return output_path


def composite_preview(background: Path, overlay: Path, output: Path) -> Path:
    bg = Image.open(background).convert("RGBA").resize(CANVAS_SIZE)
    ov = Image.open(overlay).convert("RGBA")
    bg.alpha_composite(ov)
    output.parent.mkdir(parents=True, exist_ok=True)
    bg.convert("RGB").save(output, quality=94)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("C:/tmp/today-on-earth-overlay.png"))
    parser.add_argument("--preview-background", type=Path, default=None)
    parser.add_argument("--preview-output", type=Path, default=Path("C:/tmp/today-on-earth-overlay-preview.jpg"))
    parser.add_argument("--city", default="Tokyo 东京")
    parser.add_argument("--country", default="Japan 日本")
    parser.add_argument("--temp", type=float, default=17)
    parser.add_argument("--wind", type=float, default=10)
    parser.add_argument("--humidity", type=float, default=73)
    parser.add_argument("--time", default="09:55")
    args = parser.parse_args()

    overlay = render_overlay(
        args.output,
        city_label=args.city,
        country_label=args.country,
        temp_c=args.temp,
        wind_kmh=args.wind,
        humidity=args.humidity,
        local_time=args.time,
    )
    print(f"overlay: {overlay}")

    if args.preview_background:
        preview = composite_preview(args.preview_background, overlay, args.preview_output)
        print(f"preview: {preview}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
