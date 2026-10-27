"""Validate the frozen dataset and the article counts behind the manuscript."""
import hashlib
import json
from collections import Counter
from common import DATA, ROLES, TIER_COLUMNS, TIER_LABELS, studies, tags, tier_counts


def validate():
    provenance = json.loads((DATA / "provenance.json").read_text())
    for filename, expected in provenance["data_sha256"].items():
        actual = hashlib.sha256((DATA / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Snapshot file changed: {filename}. Reconcile and version the data before regenerating.")
    all_rows = studies()
    articles = studies(True)
    assert len(all_rows) == len({r["study_id"] for r in all_rows}) == 1786
    assert len(articles) == 1390
    assert len(all_rows) - len(articles) == 396
    for r in articles:
        assigned = {role for role, col in zip(ROLES, TIER_COLUMNS) if r[col]}
        assert assigned == tags(r["ai_roles"]), r["study_id"]
        assert assigned, r["study_id"]
        for col, labels in zip(TIER_COLUMNS, TIER_LABELS):
            assert not r[col] or r[col] in {f"T{i}" for i in range(1, len(labels) + 1)}, r["study_id"]
    expected = {"Analysis": [210, 1006, 15, 0], "Prediction": [173, 763, 34, 3],
                "Generation": [11, 15, 12, 0], "Decision support": [90, 1, 0], "Intervention": [13, 2, 1]}
    counts = tier_counts()
    for role, values in expected.items():
        assert [counts[role][f"T{i}"] for i in range(1, len(values) + 1)] == values, role
    assert sum(sum(c.values()) for c in counts.values()) == 2349
    counts_2025 = Counter(m for r in articles if r["year"] == "2025" for m in tags(r["model_categories"]))
    assert counts_2025 == {"Machine learning": 295, "Deep learning": 199, "Language models": 18}
    assert sum(r["year"] == "2025" for r in articles) == 380
    print("Validated: 1,786 publications, 1,390 original articles, 2,349 article-role assignments.")


if __name__ == "__main__":
    validate()
