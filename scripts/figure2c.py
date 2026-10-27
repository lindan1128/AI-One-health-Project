"""Figure 2C: fractional track stacks and country means by development group."""
from collections import Counter
from common import GROUPS, TRACKS, TRACK_COLORS, SVG, read_csv, studies, tags, write_table


def aggregate():
    mapping = {r["country"]: r for r in read_csv("country_groups.csv")}
    universes = {g: {r["classification_name"] for r in read_csv("country_universe.csv") if r["group"] == g}
                 for g in GROUPS}
    totals, stacks, by_country = Counter(), Counter(), Counter()
    excluded = []
    for r in studies(True):
        year = int(r["year"])
        if not 2016 <= year <= 2025:
            continue
        tracks = tags(r["one_health_tracks"]) & set(TRACKS)
        if not tracks:
            excluded.append(dict(study_id=r["study_id"], reason="No assigned One Health track"))
            continue
        countries = tags(r["countries"])
        missing = countries - set(mapping)
        if missing:
            excluded.append(dict(study_id=r["study_id"], reason="Country omitted from bars by source mapping, but retained in means if present in UNCTAD universe: " + "|".join(sorted(missing))))
        groups = {mapping[c]["group"] for c in countries if c in mapping}
        for group in groups:
            if group not in GROUPS:
                continue
            totals[group, year] += 1
            for track in tracks:
                stacks[group, year, track] += 1 / len(tracks)
        # Country means also match raw names against the fixed country universe.
        # This includes Cambodia, which is missing from the alias table.
        for country in {mapping[c]["classification_name"] if c in mapping else c for c in countries}:
            by_country[country, year] += 1
    means, bars = [], []
    for group in GROUPS:
        universe = universes[group]
        ranked = sorted(universe, key=lambda c: (-sum(by_country[c, y] for y in range(2016, 2026)), c))
        excluded_countries = ranked[:2]
        for year in range(2016, 2026):
            means.append(dict(group=group, year=year, country_denominator=len(universe),
                              excluded_top_two="|".join(excluded_countries),
                              mean_all=sum(by_country[c, year] for c in universe) / len(universe),
                              mean_excluding_top_two=sum(by_country[c, year] for c in ranked[2:]) / (len(universe) - 2)))
            for track in TRACKS:
                bars.append(dict(group=group, year=year, track=track,
                                 fractional_articles=stacks[group, year, track], articles=totals[group, year]))
    return bars, means, excluded


def main():
    bars, means, excluded = aggregate()
    write_table("figure2c_stacks.csv", bars)
    write_table("figure2c_country_means.csv", means)
    write_table("figure2c_exclusions.csv", excluded, ("study_id", "reason"))
    svg = SVG(7.6 * 72, 2.3 * 72, "Figure 2C. Original research across development groups")
    left, right, top, bottom = 40, 507, 29, 112
    group_width = (right - left) / 3
    bar_lookup = {(r["group"], r["year"], r["track"]): r["fractional_articles"] for r in bars}
    maximum = max(r["articles"] for r in bars)
    ymax = max(300, (int(maximum) // 100 + 1) * 100)
    for j, group in enumerate(GROUPS):
        x0 = left + j * group_width
        svg.text(x0 + group_width / 2, 16, group.replace("Other developing", "Developing"), anchor="middle")
        positions = [x0 + 10 + i * (group_width - 20) / 9 for i in range(10)]
        bar_width = (group_width - 20) / 9 * 0.78
        for year, xx in zip(range(2016, 2026), positions):
            base = bottom
            for track, color in zip(TRACKS, TRACK_COLORS):
                height = bar_lookup[group, year, track] / ymax * (bottom - top)
                svg.rect(xx - bar_width / 2, base - height, bar_width, height, color, "black", 0.35)
                base -= height
            svg.line(xx, bottom, xx, bottom + 3)
            svg.text(xx + 3, bottom + 8, year, anchor="end", rotate=-90)
        mm = [r for r in means if r["group"] == group]
        for field, dash in [("mean_all", None), ("mean_excluding_top_two", "6 4")]:
            svg.polyline([(xx, bottom - r[field] / 3 * (bottom - top)) for xx, r in zip(positions, mm)], "#333333", 1.8, dash)
        if j == 0:
            for k, (label, dash) in enumerate((("All countries", None), ("Excluding top 2", "4 3"))):
                yy = top + 9 + k * 13
                svg.line(x0 + 8, yy, x0 + 24, yy, "#333333", 1.8, dash)
                svg.text(x0 + 29, yy + 4, label)
        if j < 2:
            svg.line(x0 + group_width, top - 5, x0 + group_width, bottom + 32, "#aaaaaa", 0.6)
    svg.line(left, top, left, bottom)
    svg.line(left, bottom, right, bottom)
    svg.line(right, top, right, bottom)
    for n in range(0, ymax + 1, 100):
        yy = bottom - n / ymax * (bottom - top)
        svg.line(left - 3, yy, left, yy)
        svg.text(left - 6, yy + 4, n, anchor="end")
    for n in range(4):
        yy = bottom - n / 3 * (bottom - top)
        svg.line(right, yy, right + 3, yy)
        svg.text(right + 6, yy + 4, n)
    svg.text(10, (top + bottom) / 2, "Number of studies", anchor="middle", rotate=-90)
    svg.text(536, (top + bottom) / 2, "Studies per country per year", anchor="middle", rotate=90)
    svg.text((left + right) / 2, 160, "Publication year", anchor="middle")
    return svg.save("Figure_2C.svg")


if __name__ == "__main__":
    print(main())
