from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "processed" / "travel_distances.json"
DEFAULT_OUTPUT = ROOT / "docs" / "assets" / "travel-distance-chart.png"

WIDTH = 2400
LEFT_MARGIN = 84
RIGHT_MARGIN = 84
TOP_MARGIN = 120
TITLE_SPACE = 150
BOTTOM_MARGIN = 120
LABEL_COLUMN = 600
BAR_GAP = 14
BAR_HEIGHT = 16
ROW_HEIGHT = BAR_HEIGHT + BAR_GAP
PLOT_LEFT = LEFT_MARGIN + LABEL_COLUMN
PLOT_RIGHT = WIDTH - RIGHT_MARGIN
PLOT_WIDTH = PLOT_RIGHT - PLOT_LEFT

BAR_FILL = "#8fb4dc"
BAR_BORDER = "#6f93bc"
GRID = "#e8edf4"
TEXT = "#10233f"
MUTED = "#5f6f84"


def load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def format_km(value: int | float) -> str:
    return f"{int(round(value)):,} km"


def fit_font(draw: ImageDraw.ImageDraw, text: str, font_path: Path, size: int, max_width: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(font_path), size=size)
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
        return font
    current = size
    while current > 14:
        current -= 1
        font = ImageFont.truetype(str(font_path), size=current)
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return font
    return font


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [text]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def load_fonts() -> tuple[Path, Path]:
    regular = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    bold = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    if not regular.exists():
        raise FileNotFoundError(f"Could not find a system font at {regular}")
    if not bold.exists():
        bold = regular
    return regular, bold


def draw_bar_chart(payload: dict, output: Path) -> None:
    regular_path, bold_path = load_fonts()
    teams = list(payload.get("teams", []))
    if not teams:
        raise ValueError("No team rows found in the processed JSON payload")

    data = sorted(teams, key=lambda item: item["total_distance_km"], reverse=True)
    max_value = max(item["total_distance_km"] for item in data)
    tick_step = 5000
    tick_max = ((max_value + tick_step - 1) // tick_step) * tick_step

    height = TOP_MARGIN + TITLE_SPACE + (len(data) * ROW_HEIGHT) + BOTTOM_MARGIN
    image = Image.new("RGB", (WIDTH, height), "white")
    draw = ImageDraw.Draw(image)

    title_font = ImageFont.truetype(str(bold_path), size=58)
    subtitle_font = ImageFont.truetype(str(regular_path), size=26)
    label_font = ImageFont.truetype(str(regular_path), size=24)
    value_font = ImageFont.truetype(str(bold_path), size=21)
    note_font = ImageFont.truetype(str(regular_path), size=20)

    title = "Which national team has to fly the most to their games?"
    subtitle = "2026 FIFA World Cup group stage | Total estimated one-way legs"
    note = "Kilometers are the canonical unit. Miles are shown only in the interactive dashboard."

    draw.multiline_text((LEFT_MARGIN, 36), title, font=title_font, fill=TEXT, spacing=6)
    draw.multiline_text((LEFT_MARGIN, 92), subtitle, font=subtitle_font, fill=MUTED, spacing=4)

    x_axis_y = TOP_MARGIN + TITLE_SPACE - 28
    for tick in range(0, tick_max + tick_step, tick_step):
        x = int(PLOT_LEFT + (tick / tick_max) * PLOT_WIDTH) if tick_max else PLOT_LEFT
        draw.line((x, x_axis_y, x, height - BOTTOM_MARGIN + 6), fill=GRID, width=1)
        tick_label = f"{tick:,}"
        bbox = draw.textbbox((0, 0), tick_label, font=label_font)
        draw.text((x - (bbox[2] - bbox[0]) / 2, x_axis_y - 26), tick_label, font=label_font, fill=MUTED)

    draw.line((PLOT_LEFT, TOP_MARGIN + TITLE_SPACE - 2, PLOT_RIGHT, TOP_MARGIN + TITLE_SPACE - 2), fill=GRID, width=2)

    for index, row in enumerate(data):
        team = str(row["team"])
        value = int(round(row["total_distance_km"]))
        y = TOP_MARGIN + TITLE_SPACE + index * ROW_HEIGHT
        center_y = y + BAR_HEIGHT // 2
        bar_width = max(1, int(round((value / tick_max) * PLOT_WIDTH))) if tick_max else 1

        label_font_fit = fit_font(draw, team, regular_path, 24, LABEL_COLUMN - 18)
        draw.text((LEFT_MARGIN, y - 1), team, font=label_font_fit, fill=TEXT)

        draw.rounded_rectangle(
            (PLOT_LEFT, y, PLOT_LEFT + bar_width, y + BAR_HEIGHT),
            radius=0,
            fill=BAR_FILL,
            outline=BAR_BORDER,
            width=1,
        )

        value_label = format_km(value)
        value_bbox = draw.textbbox((0, 0), value_label, font=value_font)
        value_width = value_bbox[2] - value_bbox[0]
        value_x = PLOT_LEFT + bar_width + 14
        if value_x + value_width > PLOT_RIGHT:
            value_x = max(PLOT_LEFT + 8, PLOT_LEFT + bar_width - value_width - 10)
            value_fill = "white"
        else:
            value_fill = TEXT
        value_y = center_y - (value_bbox[3] - value_bbox[1]) / 2 - 1
        draw.text((value_x, value_y), value_label, font=value_font, fill=value_fill)

    note_lines = wrap_text(draw, note, note_font, WIDTH - (LEFT_MARGIN * 2))
    note_y = height - BOTTOM_MARGIN + 20
    for line in note_lines:
        draw.text((LEFT_MARGIN, note_y), line, font=note_font, fill=MUTED)
        note_y += 24

    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a static PNG of the travel distance chart.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Processed JSON input file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="PNG output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_payload(args.input)
    draw_bar_chart(payload, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
