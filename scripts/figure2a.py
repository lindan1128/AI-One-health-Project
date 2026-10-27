"""Figure 2A: annual original-research counts by overlapping model category."""
from collections import Counter
from common import MODELS, MODEL_COLORS, SVG, studies, tags, write_table


def main():
    rows = [r for r in studies(True) if int(r["year"]) <= 2025]
    counts = Counter((int(r["year"]), m) for r in rows for m in tags(r["model_categories"]))
    years = range(min(int(r["year"]) for r in rows), 2026)
    write_table("figure2a_counts.csv", [dict(year=y, model=m, articles=counts[y, m])
                                        for m in MODELS for y in years])
    svg = SVG(8.2 * 72, 2.8 * 72, "Figure 2A. AI research in One Health over time")
    left, right, top, bottom = 48, 578, 16, 133

    def x(year):
        # The historical interval is compressed, matching the manuscript layout.
        v = (year - 1940) / 75 if year <= 2015 else 1 + (year - 2015) * 0.3
        return left + (v - 5 / 75) / (4.1 - 5 / 75) * (right - left)

    def y(n):
        return bottom - n / 310 * (bottom - top)

    for m, color in zip(MODELS, MODEL_COLORS):
        active = [yr for yr in years if counts[yr, m]]
        if active:
            svg.polyline([(x(yr), y(counts[yr, m])) for yr in years if yr >= min(active)], color, 4)
    for yr, height in [(1952, 50), (2000, 150), (2017, 200), (2022, 250)]:
        svg.line(x(yr), bottom, x(yr), y(height), "#C65359", 2.6, "7 5")
        svg.circle(x(yr), y(height), 3.3, "#C65359")
    # Historical annotations shown in the manuscript.
    for yr, height, label, anchor, dx in [
        (1952, 50, "1952: Machine", "start", -4),
        (2000, 150, "2000: Deep Learning", "middle", 0),
        (2017, 200, "2017: Transformer Architecture", "middle", 0),
        (2022, 250, "2022: ChatGPT", "middle", 0),
    ]:
        svg.text(x(yr) + dx, y(height) - 10, label, anchor=anchor)
    svg.text(x(1952) + 18, y(50) + 3, "Learning")
    svg.line(left, top, left, bottom, width=1.5)
    svg.line(left, bottom, right, bottom, width=1.5)
    for n in (0, 100, 200, 300):
        svg.line(left - 4, y(n), left, y(n), width=1.2)
        svg.text(left - 7, y(n) + 4, n, anchor="end")
    for yr in [1955, 1970, 1985, 2000, 2015, *range(2016, 2026)]:
        svg.line(x(yr), bottom, x(yr), bottom + 4, width=1.2)
        if yr <= 2015:
            svg.text(x(yr) + 3, bottom + 8, yr, anchor="end", rotate=-90)
        else:
            svg.text(x(yr), bottom + 15, yr, anchor="middle")
    svg.text(13, (top + bottom) / 2, "Number of studies", anchor="middle", rotate=-90)
    svg.text((left + right) / 2, 177, "Publication year", anchor="middle")
    for xx, label, color in zip((75, 252, 419), ("Machine learning", "Deep learning", "Language models"), MODEL_COLORS):
        svg.line(xx, 193, xx + 18, 193, color, 3)
        svg.text(xx + 24, 197, label)
    return svg.save("Figure_2A.svg")


if __name__ == "__main__":
    print(main())
