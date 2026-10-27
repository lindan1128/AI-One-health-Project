"""Figure 3: one curve per article-role pair and role-specific tier counts."""
import hashlib
import math
from common import ROLES, ROLE_COLORS, TIER_COLUMNS, TIER_LABELS, SVG, studies, tier_counts, tier_percent, write_table


def main():
    rows = studies(True)
    counts = tier_counts()
    records = []
    for role, labels in zip(ROLES, TIER_LABELS):
        total = sum(counts[role].values())
        for i, label in enumerate(labels, 1):
            tier = f"T{i}"
            n = counts[role][tier]
            records.append(dict(role=role, tier=tier, label=label, articles=n, role_total=total,
                                percent=100 * n / total, display_percent=tier_percent(role, tier, n, total)))
    write_table("figure3_tier_counts.csv", records)
    svg = SVG(8 * 72, 10.25 * 72, "Figure 3. AI roles and evaluation tiers in One Health")
    origin_x, origin_y = 25, 191
    band_x, band_width, rail = 239, 72, 563
    profile_x = band_x + band_width
    curve_end = band_x - 8
    cursor = 20
    panels = []
    # Count-sensitive heights have floors for legibility; they are not a ratio scale.
    for role, labels, height in zip(ROLES, TIER_LABELS, (182, 164, 124, 112, 100)):
        minimum, empty = 18, 14
        ns = [counts[role][f"T{i}"] for i in range(1, len(labels) + 1)]
        remaining = height - sum(minimum if n else empty for n in ns)
        denominator = sum(math.sqrt(n) for n in ns)
        top = cursor
        intervals = []
        for i, (label, n) in enumerate(zip(labels, ns), 1):
            h = minimum + remaining * math.sqrt(n) / denominator if n else empty
            intervals.append((f"T{i}", label, n, cursor, h))
            cursor += h
        panels.append((role, top, height, intervals))
        cursor += 7
    for (role, top, height, intervals), column, color in zip(panels, TIER_COLUMNS, ROLE_COLORS):
        for tier, label, n, y0, h in intervals:
            members = sorted((r for r in rows if r[column] == tier), key=lambda r: r["study_id"])
            for k, r in enumerate(members):
                y = y0 + 1.5 + (h - 3) * (k + 0.5) / n
                jitter = int(hashlib.sha256((r["study_id"] + role).encode()).hexdigest()[:8], 16) / 0xffffffff
                extent = origin_y - 20 if y < origin_y else cursor - origin_y
                outer = min(1, abs(y - origin_y) / extent) ** 0.65
                span = curve_end - origin_x
                c1 = origin_x + span * (0.30 + 0.12 * outer + 0.025 * (jitter - 0.5))
                c2 = origin_x + span * (0.72 - 0.20 * outer + 0.04 * (jitter - 0.5))
                svg.path(f"M {origin_x} {origin_y} C {c1:.3f} {origin_y}, {c2:.3f} {y:.3f}, {curve_end} {y:.3f}",
                         stroke=color, width=0.42, opacity=0.23)
    svg.circle(origin_x, origin_y, 2.4, "#333333")
    svg.text(10, 130, "AI in One Health", bold=True)
    svg.text(10, 144, f"({len(rows):,})", bold=True)
    svg.line(origin_x, 153, origin_x, origin_y - 7, width=1.1, dash="4 3")
    svg.text(rail + 1, 10, "Evaluation", anchor="end", bold=True)
    for (role, top, height, intervals), color in zip(panels, ROLE_COLORS):
        total = sum(counts[role].values())
        peak = max(counts[role].values())
        svg.rect(band_x, top, band_width, height, color)
        lines = [role] if role != "Decision support" else ["Decision", "support"]
        lines.append(f"({total:,})")
        for j, line in enumerate(lines):
            svg.text(band_x + band_width / 2, top + height / 2 + (j - (len(lines) - 1) / 2) * 13 + 4,
                     line, anchor="middle", color="white", bold=True)
        for tier, label, n, y0, h in intervals:
            mid = y0 + h / 2
            width = 43 * math.sqrt(n / peak)
            curve = (f"M {profile_x} {y0:.3f} C {profile_x} {y0+h*.25:.3f}, {profile_x+width:.3f} {y0+h*.2:.3f}, "
                     f"{profile_x+width:.3f} {mid:.3f} C {profile_x+width:.3f} {y0+h*.8:.3f}, "
                     f"{profile_x} {y0+h*.75:.3f}, {profile_x} {y0+h:.3f}")
            if n:
                svg.path(curve + " Z", fill=color, opacity=0.65)
                svg.path(curve, stroke="black", width=1.3)
            svg.line(profile_x, y0, rail - 11, y0, width=1)
            svg.text(profile_x + width + 7, mid + 4, tier_percent(role, tier, n, total) + "%", color=color, bold=True)
            svg.text(rail - 16, mid + 4, label, anchor="end")
            svg.text(rail, mid + 4, tier, anchor="middle", bold=True)
        svg.line(profile_x, top + height, rail - 11, top + height, width=1)
        svg.line(profile_x, top, profile_x, top + height, color, 1.5)
        arrow_x = 573
        svg.line(arrow_x, top + 12, arrow_x, top + height - 9, width=1)
        svg.path(f"M {arrow_x-2} {top+height-12} L {arrow_x} {top+height-6} L {arrow_x+2} {top+height-12} Z", fill="black")
    definitions = [("Analysis", "AI identifies patterns", "in data."),
                   ("Prediction", "AI infers unknown", "outcomes."),
                   ("Generation", "AI generates new data.", ""),
                   ("Decision support", "AI recommends actions.", ""),
                   ("Intervention", "AI is the action", "being tested.")]
    legend_y = 455
    svg.text(10, legend_y - 10, "AI roles in One Health", bold=True)
    for i, ((role, line1, line2), color) in enumerate(zip(definitions, ROLE_COLORS)):
        y = legend_y + i * 51
        svg.rect(10, y, 157, 46, color)
        svg.text(15, y + 13, role, color="white", bold=True)
        svg.text(15, y + 27, line1, color="white")
        if line2:
            svg.text(15, y + 40, line2, color="white")
    return svg.save("Figure_3.svg")


if __name__ == "__main__":
    print(main())
