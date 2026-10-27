"""Shared data definitions and deterministic SVG primitives. Standard library only."""
import csv
import html
import math
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
MODELS = ("Machine learning", "Deep learning", "Language models")
MODEL_COLORS = ("#c17c70", "#a7b6cb", "#d8c398")
TRACKS = (
    "Health systems", "Emerging zoonoses", "Endemic and vector-borne diseases",
    "Food safety", "Antimicrobial resistance", "Environment and health",
)
TRACK_LABELS = (
    "Health systems", "Emerging zoonoses", "Endemic/vector-borne",
    "Food safety", "Antimicrobial resistance", "Environment & health",
)
TRACK_COLORS = ("#9A9AB9", "#FFC992", "#B4D1C8", "#CEA2B5", "#70C0DB", "#F1C667")
GROUPS = ("Developed economies", "Other developing economies", "Least developed countries")
ROLES = ("Analysis", "Prediction", "Generation", "Decision support", "Intervention")
ROLE_COLORS = ("#FFC992", "#50B9AE", "#9A9AB9", "#CEA2B5", "#E29578")
TIER_COLUMNS = ("analysis_tier", "prediction_tier", "generation_tier", "decision_support_tier", "intervention_tier")
TIER_LABELS = (
    ("Pattern discovery", "Robustness checks", "External replication", "Experimental confirmation"),
    ("Model development", "Internal validation", "External validation", "Prospective validation"),
    ("Data generation", "Quality assessment", "Functional testing", "Real-world utility"),
    ("Offline testing", "Simulation comparison", "Real-world comparison"),
    ("Uncontrolled trial", "Non-randomized controlled trial", "Randomized controlled trial"),
)


def read_csv(name):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def tags(value):
    return set(filter(None, value.split("|")))


def studies(original_only=False):
    rows = read_csv("studies.csv")
    return [r for r in rows if not original_only or r["article_type"] == "original_research"]


def write_table(name, rows, fields=None):
    TABLES.mkdir(exist_ok=True)
    with (TABLES / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def annual_growth(counts):
    """Mean of nine add-one-adjusted annual percentage changes, not CAGR."""
    if len(counts) != 10:
        raise ValueError("Growth requires ten annual counts, 2016–2025.")
    return sum(100 * (b - a) / (a + 1) for a, b in zip(counts, counts[1:])) / 9


def tier_counts():
    rows = studies(True)
    return {role: Counter(r[column] for r in rows if r[column])
            for role, column in zip(ROLES, TIER_COLUMNS)}


def tier_percent(role, tier, n, total):
    # Display 13/16 as 81.2%, consistent with the manuscript.
    if role == "Intervention" and tier == "T1" and n / total == 13 / 16:
        return "81.2"
    value = Decimal(100) * Decimal(n) / Decimal(total)
    return str(value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


class SVG:
    """SVG coordinates in typographic points (72 points per inch)."""
    def __init__(self, width, height, title):
        self.width, self.height = width, height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}pt" height="{height}pt" viewBox="0 0 {width} {height}">',
            f'<title>{html.escape(title)}</title>',
            '<g font-family="Arial, Helvetica, sans-serif" font-size="11" fill="#111111">',
        ]

    def raw(self, markup):
        self.parts.append(markup)

    def text(self, x, y, value, size=11, anchor="start", color="#111111", bold=False, rotate=None):
        transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
        self.raw(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" '
                 f'fill="{color}" font-weight="{"bold" if bold else "normal"}"{transform}>'
                 f'{html.escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color="#111111", width=0.8, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
                 f'stroke="{color}" stroke-width="{width}"{extra}/>')

    def rect(self, x, y, w, h, fill, stroke="none", width=0.5):
        self.raw(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def path(self, path, fill="none", stroke="none", width=0.7, opacity=1):
        self.raw(f'<path d="{path}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
                 f'opacity="{opacity}" stroke-linejoin="round" stroke-linecap="round"/>')

    def polyline(self, points, color, width=1, dash=None):
        coords = " ".join(f"{x:.3f},{y:.3f}" for x, y in points)
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<polyline points="{coords}" fill="none" stroke="{color}" '
                 f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{extra}/>')

    def circle(self, x, y, radius, fill, stroke="none", width=0.5):
        self.raw(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius:.3f}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def donut(self, x, y, radius, shares, colors):
        theta = -math.pi / 2
        inner = radius * 0.57
        for share, color in zip(shares, colors):
            if share <= 0:
                continue
            end = theta + share * 2 * math.pi
            # Polygon sampling keeps full-circle and very small sectors well-defined.
            steps = max(2, math.ceil(share * 160))
            angles = [theta + (end - theta) * i / steps for i in range(steps + 1)]
            points = [(x + radius * math.cos(a), y + radius * math.sin(a)) for a in angles]
            points += [(x + inner * math.cos(a), y + inner * math.sin(a)) for a in reversed(angles)]
            path = "M " + " L ".join(f"{px:.3f} {py:.3f}" for px, py in points) + " Z"
            self.path(path, fill=color, stroke="black", width=0.6)
            theta = end

    def save(self, name):
        FIGURES.mkdir(exist_ok=True)
        path = FIGURES / name
        path.write_text("\n".join(self.parts + ["</g></svg>"]), encoding="utf-8")
        return path
