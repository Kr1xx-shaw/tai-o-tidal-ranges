# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.9,<4"]
# ///

"""Draw one flat view from the committed data. Run with: uv run plot.py."""
import calendar
import datetime as dt
import json
import math
from decimal import Decimal
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "tides-TAO-2026.json"
OUT = HERE / "out" / "tai-o-year-plan.png"
YEAR = 2026
PAPER, INK, ORANGE = "#f8f6f1", "#334342", "#d46b32"
BLACK = "#171717"
PALETTE = [
    "#537d80", "#ad788b", "#a88e47", "#679592", "#c48d9b", "#bea258",
    "#98b7ad", "#dfb0b7", "#d9c68c", "#afc4be", "#e5c1c6", "#e3d6ac",
]


def load_months(path):
    """Validate every daily row and calculate its hourly sampled range."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    fields = ["MM", "DD"] + [f"{hour:02d}" for hour in range(1, 25)]
    if raw.get("fields") != fields:
        raise ValueError("Unexpected HKO fields: expected month, day and hours 01–24.")
    months = {month: [] for month in range(1, 13)}
    dates = []
    for row in raw["data"]:
        if len(row) != 26:
            raise ValueError(f"Expected 24 hourly heights in row: {row}")
        date = dt.date(YEAR, int(row[0]), int(row[1]))
        heights = [Decimal(value) for value in row[2:]]
        if not all(value.is_finite() for value in heights):
            raise ValueError(f"Non-finite tide height on {date}.")
        sampled_range = max(heights) - min(heights)
        months[date.month].append((date.day, sampled_range))
        dates.append(date)
    start, stop = dt.date(YEAR, 1, 1), dt.date(YEAR + 1, 1, 1)
    expected = [start + dt.timedelta(days=i) for i in range((stop - start).days)]
    if sorted(dates) != expected:
        raise ValueError("Expected every date exactly once: missing or duplicate dates found.")
    for entries in months.values():
        entries.sort()
    print(f"{path.name}: {len(dates)} complete days, {len(dates) * 24:,} hourly predictions.")
    print(f"First daily sampled range: {months[1][0][1]:.2f} m.")
    return months


def to_xy(day, radius):
    """Day 1 points north; advance clockwise on a fixed 31-day scale."""
    angle = (day - 1) * math.tau / 31
    return float(radius) * math.sin(angle), float(radius) * math.cos(angle)


def draw(months):
    plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})
    fig = plt.figure(figsize=(14, 10), facecolor=PAPER)
    fig.text(.07, .921, "A YEAR OF TIDE", fontsize=29)
    fig.text(.072, .882, "TAI O, HONG KONG  /  JANUARY–DECEMBER 2026", fontsize=10, color="#77817c")
    fig.text(.93, .922, "PLAN VIEW", ha="right", fontsize=11, color="#77817c")
    ax = fig.add_axes([.055, .172, .65, .66], facecolor=PAPER)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-3.65, 3.65)
    ax.set_ylim(-3.65, 3.65)

    for radius in [1, 2, 3]:
        angles = [i * math.tau / 360 for i in range(361)]
        ax.plot([radius * math.sin(a) for a in angles],
                [radius * math.cos(a) for a in angles],
                color="#cfd3cb", lw=.65, ls=(0, (3, 5)), zorder=0)
        angle = math.radians(59)
        xy = radius * math.sin(angle), radius * math.cos(angle)
        ax.annotate(f"{radius} m", xy, xytext=(5, 3), textcoords="offset points", fontsize=8, color="#89938c")
    for day in [1, 5, 10, 15, 20, 25, 30]:
        x, y = to_xy(day, 3.2)
        ax.plot([0, x], [0, y], color="#e0e3dc", lw=.65, zorder=0)
        x, y = to_xy(day, 3.48)
        ax.text(x, y, f"{day:02d}", ha="center", va="center", fontsize=10, color="#8a928b")

    peaks, minima = [], []
    for month, color in zip(range(1, 13), PALETTE):
        entries = months[month]
        coordinates = [to_xy(day, value) for day, value in entries]
        x, y = zip(*coordinates)
        ax.fill(x, y, color=color, alpha=.025, lw=0, zorder=1)
        ax.plot(x, y, color=color, lw=1.55, marker="o", markersize=2.1,
                markeredgewidth=0, zorder=3 + month * .1)
        # This graphical closure does not interpolate missing days in shorter months.
        ax.plot([x[-1], x[0]], [y[-1], y[0]], color=color, lw=.9,
                ls=(0, (2, 4)), alpha=.65, zorder=3)
        maximum = max(value for _, value in entries)
        peak_days = [day for day, value in entries if value == maximum]
        peaks.extend(to_xy(day, maximum) for day in peak_days)
        minimum = min(value for _, value in entries)
        minimum_days = [day for day, value in entries if value == minimum]
        minima.extend(to_xy(day, minimum) for day in minimum_days)
        print(f"{calendar.month_name[month]}: {len(entries)} days; maximum {maximum:.2f} m on day(s) {peak_days}; minimum {minimum:.2f} m on day(s) {minimum_days}.")
        yy = .75 - (month - 1) * .041
        fig.add_artist(plt.Line2D([.765, .807], [yy, yy], transform=fig.transFigure, color=color, lw=3))
        fig.text(.826, yy - .006, calendar.month_name[month].upper(), fontsize=11)

    ax.scatter(*zip(*peaks), s=60, color=ORANGE, edgecolors=PAPER, linewidths=1.3, zorder=10)
    ax.scatter(*zip(*minima), s=60, color=BLACK, edgecolors=PAPER, linewidths=1.3, zorder=10)
    fig.text(.765, .8, "MONTH / 2026", fontsize=9, color="#7c8880")
    fig.text(.765, .239, "●", fontsize=15, color=ORANGE)
    fig.text(.791, .242, "Monthly maximum", fontsize=10, color="#7b837c")
    fig.text(.765, .204, "●", fontsize=15, color=BLACK)
    fig.text(.791, .207, "Monthly minimum", fontsize=10, color="#7b837c")
    fig.text(.765, .172, "One point = one day", fontsize=10, color="#7b837c")
    fig.add_artist(plt.Line2D([.07, .93], [.125, .125], transform=fig.transFigure, color="#c5cbc1", lw=.7))
    fig.text(.07, .088, "ANGLE = DAY OF MONTH  /  RADIUS = RANGE OF HOURLY TIDE PREDICTIONS (m)", fontsize=9)
    fig.text(.07, .057, "HKO astronomical predictions · Daily samples: 01:00–24:00 HKT · Fixed 31-day angular scale · Dashed joins are not observations.", fontsize=8, color="#7b857d")
    fig.text(.93, .032, "Shared radial scale · Hourly samples may miss high and low water between hours.", ha="right", fontsize=8, color="#7b857d")
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=190, facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {OUT}")


def main():
    draw(load_months(DATA))


if __name__ == "__main__":
    main()
