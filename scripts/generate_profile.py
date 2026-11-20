#!/usr/bin/env python3
"""Generate portfolio-branded animated SVGs for the ezriouil GitHub profile."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "ezriouil"
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
PALETTE = ["#161b22", "#0c2d6b", "#1158c7", "#1f6feb", "#58a6ff"]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_hero() -> None:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="430" viewBox="0 0 900 430">
  <defs><radialGradient id="glow" cx="72%" cy="5%" r="68%"><stop offset="0" stop-color="#ebe6d6"/><stop offset="1" stop-color="#f6f5f0"/></radialGradient></defs>
  <style>
    .sans { font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .serif { font-family: Georgia, "Times New Roman", serif; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    .intro { opacity: 0; animation: enter .75s cubic-bezier(.2,.8,.2,1) forwards; }
    .d1 { animation-delay: .12s; } .d2 { animation-delay: .28s; } .d3 { animation-delay: .44s; }
    .chip { opacity: 0; animation: chipIn .5s ease-out forwards; }
    .c1 { animation-delay: .7s; } .c2 { animation-delay: .82s; } .c3 { animation-delay: .94s; }
    .word1 { animation: word1 9s ease-in-out infinite; } .word2 { animation: word2 9s ease-in-out infinite; } .word3 { animation: word3 9s ease-in-out infinite; }
    .star { transform-origin: 816px 62px; animation: spin 12s linear infinite; }
    @keyframes enter { from { opacity:0; transform:translateY(13px) } to { opacity:1; transform:translateY(0) } }
    @keyframes chipIn { from { opacity:0; transform:translateX(-8px) } to { opacity:1; transform:translateX(0) } }
    @keyframes word1 { 0%,28% { opacity:1; transform:translateY(0) } 33%,95% { opacity:0; transform:translateY(-8px) } 96%,100% { opacity:1; transform:translateY(0) } }
    @keyframes word2 { 0%,30% { opacity:0; transform:translateY(8px) } 34%,61% { opacity:1; transform:translateY(0) } 66%,100% { opacity:0; transform:translateY(-8px) } }
    @keyframes word3 { 0%,63% { opacity:0; transform:translateY(8px) } 67%,94% { opacity:1; transform:translateY(0) } 99%,100% { opacity:0; transform:translateY(-8px) } }
    @keyframes spin { to { transform:rotate(360deg) } }
  </style>
  <rect x="1" y="1" width="898" height="428" rx="22" fill="url(#glow)" stroke="#e8e4d8"/>
  <text x="48" y="62" class="serif" fill="#181716" font-size="25" font-style="italic">me.</text>
  <text x="672" y="61" class="mono" fill="#878278" font-size="11" letter-spacing="1.2">MOHAMEDEZRIOUIL.COM</text>
  <text x="816" y="70" class="serif star" fill="#b9a66f" font-size="25">✶</text>
  <g class="intro d1"><text x="48" y="116" class="mono" fill="#878278" font-size="12" letter-spacing="1.8">SOFTWARE ENGINEER · MOROCCO</text></g>
  <g class="intro d2"><text x="48" y="177" class="serif" fill="#181716" font-size="50">Hi, I’m <tspan font-style="italic">Mohamed Ezriouil.</tspan></text><text x="49" y="211" class="sans" fill="#878278" font-size="16">Creating dependable products with clarity and purpose.</text></g>
  <g class="intro d3">
    <rect x="48" y="244" width="804" height="76" rx="16" fill="#fdfcf7" stroke="#e8e4d8"/>
    <text x="72" y="289" class="serif" fill="#181716" font-size="26">I build</text>
    <text x="164" y="289" class="serif word1" fill="#8e7b45" font-size="26" font-style="italic">mobile products.</text>
    <text x="164" y="289" class="serif word2" fill="#8e7b45" font-size="26" font-style="italic">web platforms.</text>
    <text x="164" y="289" class="serif word3" fill="#8e7b45" font-size="26" font-style="italic">AI-powered experiences.</text>
    <text x="825" y="288" text-anchor="end" class="mono" fill="#b4afa1" font-size="11">IDEA → PRODUCTION</text>
  </g>
  <g class="chip c1"><rect x="48" y="347" width="170" height="38" rx="19" fill="#ebe6d6"/><text x="133" y="371" text-anchor="middle" class="sans" fill="#181716" font-size="12">📱 Mobile Developer</text></g>
  <g class="chip c2"><rect x="230" y="347" width="164" height="38" rx="19" fill="#ebe6d6"/><text x="312" y="371" text-anchor="middle" class="sans" fill="#181716" font-size="12">🌐 Web Specialist</text></g>
  <g class="chip c3"><rect x="406" y="347" width="179" height="38" rx="19" fill="#ebe6d6"/><text x="495" y="371" text-anchor="middle" class="sans" fill="#181716" font-size="12">🤖 AI Product Builder</text></g>
  <text x="682" y="371" class="mono" fill="#878278" font-size="11">OPEN TO COLLABORATION</text>
</svg>'''
    write(ASSETS / "profile-hero.svg", svg)


def fetch_contributions() -> list[dict[str, int | str]]:
    response = requests.get(f"https://github.com/users/{USERNAME}/contributions", timeout=30, headers={"User-Agent": f"{USERNAME}-profile-readme"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    tooltips = {}
    for tooltip in soup.select("tool-tip[for]"):
        match = re.search(r"([\d,]+) contribution", tooltip.get_text(" ", strip=True))
        tooltips[tooltip["for"]] = int(match.group(1).replace(",", "")) if match else 0
    days = [{"date": cell["data-date"], "level": int(cell["data-level"]), "count": tooltips.get(cell.get("id", ""), 0)} for cell in soup.select("[data-date][data-level]")]
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
    for day in days:
        current_date = date.fromisoformat(str(day["date"]))
        week = (current_date - week_start).days // 7
        weekday = (current_date.weekday() + 1) % 7
        x, y = 68 + week * 14, 64 + weekday * 14
        level = min(int(day["level"]), 4)
        delay = min(1.8, (week + weekday) * 0.018)
        cells.append(f'<rect class="cell" x="{x}" y="{y}" width="10" height="10" rx="3" fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s"><title>{day["count"]} contributions on {day["date"]}</title></rect>')
    total = sum(int(day["count"]) for day in days)
    current, longest = streaks(days)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="210" viewBox="0 0 900 210">
  <style>
    .serif {{ font-family: Georgia, "Times New Roman", serif; }} .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .meta, .day {{ fill:#8b949e; font-size:10px; }} .cell {{ opacity:0; transform:translateY(6px); animation:rise .4s ease-out forwards; }}
    .pulse {{ transform-origin:839px 30px; animation:pulse 2.4s ease-in-out infinite; }}
    @keyframes rise {{ to {{ opacity:1; transform:translateY(0) }} }} @keyframes pulse {{ 50% {{ opacity:.35; transform:scale(.72) }} }}
  </style>
  <rect x="1" y="1" width="898" height="208" rx="22" fill="#0d1117" stroke="#30363d"/>
  <text x="40" y="39" class="serif" fill="#f0f6fc" font-size="21">Consistency, <tspan font-style="italic" fill="#58a6ff">visualized.</tspan></text>
  <circle class="pulse" cx="720" cy="30" r="5" fill="#58a6ff"/><text x="735" y="34" class="mono" fill="#8b949e" font-size="10">BUILDING IN PUBLIC</text>
  <text class="day mono" x="42" y="85">M</text><text class="day mono" x="42" y="113">W</text><text class="day mono" x="42" y="141">F</text>
  {''.join(cells)}
  <line x1="40" y1="171" x2="860" y2="171" stroke="#30363d"/>
  <text class="meta mono" x="40" y="192">{total:,} CONTRIBUTIONS · CURRENT {current} DAYS · LONGEST {longest} DAYS</text>
  <text class="meta mono" x="738" y="192">UPDATED {datetime.now().date().isoformat()}</text>
</svg>'''
    write(ASSETS / "contributions-blue.svg", svg)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    render_hero()
    render_heatmap(fetch_contributions())
    print("Generated portfolio-branded animated profile assets")


if __name__ == "__main__":
    main()
