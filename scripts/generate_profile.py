#!/usr/bin/env python3
"""Generate self-hosted animated SVGs for the ezriouil GitHub profile."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from html import escape
from io import BytesIO
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance, ImageOps


USERNAME = "ezriouil"
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
GREEN = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fetch_avatar() -> Image.Image:
    response = requests.get(
        f"https://github.com/{USERNAME}.png?size=460",
        timeout=30,
        headers={"User-Agent": f"{USERNAME}-profile-readme"},
    )
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")


def render_ascii_portrait(image: Image.Image) -> None:
    size = min(image.size)
    left = (image.width - size) // 2
    top = (image.height - size) // 2
    image = image.crop((left, top, left + size, top + size))
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(1.65)

    columns = 58
    rows = 34
    image = image.resize((columns, rows))
    ramp = "@%#*+=-:. "
    lines = []
    for y in range(rows):
        line = "".join(ramp[image.getpixel((x, y)) * (len(ramp) - 1) // 255] for x in range(columns))
        lines.append(line.rstrip())

    text_nodes = []
    for index, line in enumerate(lines):
        delay = index * 0.045
        text_nodes.append(
            f'<text x="18" y="{28 + index * 10.2:.1f}" class="row" '
            f'style="animation-delay:{delay:.3f}s">{escape(line)}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="390" viewBox="0 0 390 390">
  <style>
    .bg {{ fill: #0d1117; stroke: #30363d; }}
    .dot-red {{ fill: #ff5f56; }} .dot-yellow {{ fill: #ffbd2e; }} .dot-green {{ fill: #27c93f; }}
    .label {{ fill: #8b949e; font: 11px ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .row {{ fill: #c9d1d9; font: 8.2px ui-monospace, SFMono-Regular, Menlo, monospace; white-space: pre; opacity: 0; animation: print .22s ease-out forwards; }}
    @keyframes print {{ from {{ opacity: 0; transform: translateX(-5px); }} to {{ opacity: 1; transform: translateX(0); }} }}
  </style>
  <rect class="bg" x="1" y="1" width="388" height="388" rx="12"/>
  <circle class="dot-red" cx="18" cy="18" r="5"/><circle class="dot-yellow" cx="35" cy="18" r="5"/><circle class="dot-green" cx="52" cy="18" r="5"/>
  <text class="label" x="195" y="22" text-anchor="middle">avatar.sh</text>
  <g xml:space="preserve">{''.join(text_nodes)}</g>
</svg>'''
    write(ASSETS / "avatar-ascii.svg", svg)


def render_info_card() -> None:
    rows = [
        ("user", "Mohamed Ezriouil", "#58a6ff"),
        ("role", "Software Engineer", "#c9d1d9"),
        ("focus", "Mobile · Web · AI", "#39d353"),
        ("building", "Products from idea to production", "#c9d1d9"),
        ("based", "Morocco", "#c9d1d9"),
        ("status", "Open to collaboration", "#f2cc60"),
    ]
    nodes = []
    for index, (key, value, color) in enumerate(rows):
        y = 106 + index * 42
        delay = 0.35 + index * 0.18
        nodes.append(
            f'<g class="line" style="animation-delay:{delay:.2f}s">'
            f'<text x="32" y="{y}" class="key">{escape(key)}</text>'
            f'<text x="142" y="{y}" fill="{color}" class="value">{escape(value)}</text></g>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="490" height="390" viewBox="0 0 490 390">
  <style>
    .bg {{ fill: #0d1117; stroke: #30363d; }}
    .dot-red {{ fill: #ff5f56; }} .dot-yellow {{ fill: #ffbd2e; }} .dot-green {{ fill: #27c93f; }}
    .title, .key, .value, .prompt {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .title {{ fill: #8b949e; font-size: 11px; }} .prompt {{ fill: #39d353; font-size: 15px; font-weight: 700; }}
    .key {{ fill: #8b949e; font-size: 13px; }} .value {{ font-size: 13px; }}
    .line {{ opacity: 0; animation: reveal .42s ease-out forwards; }}
    .cursor {{ fill: #39d353; animation: blink .8s steps(1) infinite; }}
    @keyframes reveal {{ from {{ opacity: 0; transform: translateY(7px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
  </style>
  <rect class="bg" x="1" y="1" width="488" height="388" rx="12"/>
  <circle class="dot-red" cx="18" cy="18" r="5"/><circle class="dot-yellow" cx="35" cy="18" r="5"/><circle class="dot-green" cx="52" cy="18" r="5"/>
  <text class="title" x="245" y="22" text-anchor="middle">mohamed@github: ~</text>
  <text class="prompt" x="30" y="62">$ whoami</text>
  {''.join(nodes)}
  <text class="prompt" x="30" y="364">$ <tspan class="cursor">_</tspan></text>
</svg>'''
    write(ASSETS / "info-card.svg", svg)


def fetch_contributions() -> list[dict[str, int | str]]:
    response = requests.get(
        f"https://github.com/users/{USERNAME}/contributions",
        timeout=30,
        headers={"User-Agent": f"{USERNAME}-profile-readme"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    tooltips = {}
    for tooltip in soup.select("tool-tip[for]"):
        match = re.search(r"([\d,]+) contribution", tooltip.get_text(" ", strip=True))
        tooltips[tooltip["for"]] = int(match.group(1).replace(",", "")) if match else 0

    days = []
    for cell in soup.select("[data-date][data-level]"):
        days.append(
            {
                "date": cell["data-date"],
                "level": int(cell["data-level"]),
                "count": tooltips.get(cell.get("id", ""), 0),
            }
        )
    if not days:
        raise RuntimeError("GitHub returned no contribution cells")
    days.sort(key=lambda day: str(day["date"]))
    write(DATA / "contributions.json", json.dumps(days, indent=2) + "\n")
    return days


def streaks(days: list[dict[str, int | str]]) -> tuple[int, int]:
    counts = [int(day["count"]) for day in days]
    longest = running = 0
    for count in counts:
        running = running + 1 if count else 0
        longest = max(longest, running)

    last_index = len(counts) - 1
    if date.fromisoformat(str(days[-1]["date"])) >= date.today() and counts[last_index] == 0:
        last_index -= 1
    current = 0
    while last_index >= 0 and counts[last_index] > 0:
        current += 1
        last_index -= 1
    return current, longest


def render_heatmap(days: list[dict[str, int | str]]) -> None:
    first = date.fromisoformat(str(days[0]["date"]))
    week_start = first.fromordinal(first.toordinal() - ((first.weekday() + 1) % 7))
    cells = []
    max_week = 0
    for index, day in enumerate(days):
        current = date.fromisoformat(str(day["date"]))
        week = (current - week_start).days // 7
        weekday = (current.weekday() + 1) % 7
        max_week = max(max_week, week)
        x = 42 + week * 15
        y = 46 + weekday * 15
        level = min(int(day["level"]), 4)
        delay = min(1.8, (week + weekday) * 0.018)
        cells.append(
            f'<rect class="cell" x="{x}" y="{y}" width="11" height="11" rx="2" fill="{GREEN[level]}" '
            f'style="animation-delay:{delay:.3f}s"><title>{day["count"]} contributions on {day["date"]}</title></rect>'
        )

    total = sum(int(day["count"]) for day in days)
    current, longest = streaks(days)
    width = max(860, 72 + (max_week + 1) * 15)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="190" viewBox="0 0 {width} 190">
  <style>
    .bg {{ fill: #0d1117; stroke: #30363d; }}
    .heading, .meta, .day {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .heading {{ fill: #39d353; font-size: 14px; font-weight: 700; }} .meta {{ fill: #8b949e; font-size: 11px; }} .day {{ fill: #8b949e; font-size: 9px; }}
    .cell {{ opacity: 0; transform: translateY(-7px); animation: drop .35s ease-out forwards; }}
    @keyframes drop {{ to {{ opacity: 1; transform: translateY(0); }} }}
  </style>
  <rect class="bg" x="1" y="1" width="{width - 2}" height="188" rx="12"/>
  <text class="heading" x="24" y="26">$ ./contributions.sh</text>
  <text class="day" x="18" y="69">M</text><text class="day" x="18" y="99">W</text><text class="day" x="18" y="129">F</text>
  {''.join(cells)}
  <text class="meta" x="24" y="171">{total:,} contributions · current streak {current} days · longest streak {longest} days</text>
  <text class="meta" x="{width - 24}" y="171" text-anchor="end">updated {datetime.now().date().isoformat()}</text>
</svg>'''
    write(ASSETS / "contributions.svg", svg)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    render_ascii_portrait(fetch_avatar())
    render_info_card()
    render_heatmap(fetch_contributions())
    print("Generated animated profile assets in assets/")


if __name__ == "__main__":
    main()
