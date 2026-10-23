"""Regenerate the paper tables in README.md from data/papers.yaml.

    python scripts/build_readme.py           # validate the data, then rewrite the tables
    python scripts/build_readme.py --check   # validate only; exit 1 if anything is wrong

Each table lives between a pair of markers in README.md, e.g.
    <!-- BEGIN papers:articulated -->  ...  <!-- END papers:articulated -->
Only the text between markers is replaced; everything else in the README is hand-written.
Requires PyYAML (pip install pyyaml).
"""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "papers.yaml"
README_PATH = ROOT / "README.md"

ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}$")
VENUE_RE = re.compile(r".+ '\d\d\)?$")
DATASET_SECTIONS = {"object_datasets", "scene_datasets", "demo_datasets", "benchmarks"}
DATASET_HEADER = {"object_datasets": "Dataset", "scene_datasets": "Dataset", "demo_datasets": "Dataset",
                  "benchmarks": "Benchmark"}


def load():
    return yaml.safe_load(DB_PATH.read_text(encoding="utf-8"))


def validate(db):
    errors = []
    keys = {t["key"] for t in db["taxonomy"]}
    seen = set()
    for kind in ("methods", "datasets"):
        for i, e in enumerate(db[kind]):
            where = f"{kind}[{i}] {e.get('name', '?')}"
            for field in ("name", "title", "venue", "section"):
                if not e.get(field):
                    errors.append(f"{where}: missing '{field}'")
            if e.get("section") not in keys:
                errors.append(f"{where}: unknown section '{e.get('section')}'")
            if kind == "methods" and e.get("section") in DATASET_SECTIONS:
                errors.append(f"{where}: dataset section used for a method")
            if e.get("arxiv") and not ARXIV_RE.match(str(e["arxiv"])):
                errors.append(f"{where}: arxiv id '{e['arxiv']}' should look like 2412.01506")
            if not e.get("arxiv") and not e.get("paper_url"):
                errors.append(f"{where}: needs 'arxiv' or 'paper_url'")
            if not e.get("arxiv") and not re.match(r"^\d{4}(-\d\d)?$", str(e.get("date", ""))):
                errors.append(f"{where}: without an arxiv id, give 'date' as YYYY-MM")
            if e.get("venue") and not VENUE_RE.match(e["venue"]):
                errors.append(f"{where}: venue '{e['venue']}' should end with 'YY, e.g. CVPR '26")
            for field in ("paper_url", "project", "code", "website"):
                if e.get(field) and not str(e[field]).startswith(("http://", "https://")):
                    errors.append(f"{where}: '{field}' is not a URL")
            ident = (e.get("section"), e.get("arxiv") or e.get("name"))
            if ident in seen:
                errors.append(f"{where}: duplicate entry in section '{e.get('section')}'")
            seen.add(ident)
    return errors


def sort_key(e):
    if e.get("arxiv"):
        yymm, num = str(e["arxiv"]).split(".")
        return (f"20{yymm[:2]}-{yymm[2:]}", int(num))
    date = str(e.get("date", "0000"))
    return (date if len(date) > 4 else date + "-12", 0)


def paper_cell(e):
    title = e["title"].replace("|", "\\|")
    if e.get("arxiv"):
        a = e["arxiv"]
        badge = f"[![arXiv](https://img.shields.io/badge/arXiv-{a}-b31b1b.svg)](https://arxiv.org/abs/{a})"
    else:
        badge = f"[![Paper](https://img.shields.io/badge/Paper-PDF-blue)]({e['paper_url']})"
    return f"{badge} <br> {title}"


def project_cell(url):
    return f"[![Project](https://img.shields.io/badge/Project-Page-blue)]({url})" if url else "-"


def code_cell(url):
    if not url:
        return "-"
    m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", url)
    if m:
        return f"[![GitHub Stars](https://img.shields.io/github/stars/{m.group(1)}/{m.group(2)})]({url})"
    return f"[![Code](https://img.shields.io/badge/Code-blue)]({url})"


def table(header, rows):
    widths = [max(len(header[i]), *(len(r[i]) for r in rows)) for i in range(len(header))]
    line = lambda cells: "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"
    return "\n".join([line(header), line(["-" * w for w in widths])] + [line(r) for r in rows])


def render_section(db, key):
    if key in DATASET_SECTIONS:
        entries = sorted((e for e in db["datasets"] if e["section"] == key), key=sort_key)
        rows = [[f"`{e['name']}`", paper_cell(e), e["venue"], e.get("details", "-"), project_cell(e.get("website"))]
                for e in entries]
        return table([DATASET_HEADER[key], "Paper", "Venue", "Details", "Website"], rows)
    entries = sorted((e for e in db["methods"] if e["section"] == key), key=sort_key)
    rows = [[f"`{e['name']}`", paper_cell(e), e["venue"], project_cell(e.get("project")), code_cell(e.get("code"))]
            for e in entries]
    return table(["Model", "Paper", "Venue", "Website", "GitHub"], rows)


def render_platforms(db):
    rows = [[p["name"], p["type"], p["strengths"], f"[![Website](https://img.shields.io/badge/Website-blue)]({p['website']})"]
            for p in db.get("platforms", [])]
    return table(["Platform", "Type", "Strengths", "Link"], rows)


def main():
    db = load()
    errors = validate(db)
    if errors:
        print("data/papers.yaml has problems:\n  " + "\n  ".join(errors))
        sys.exit(1)
    if "--check" in sys.argv:
        print(f"OK: {len(db['methods'])} methods, {len(db['datasets'])} datasets")
        return
    readme = README_PATH.read_text(encoding="utf-8")
    blocks = {f"papers:{t['key']}": render_section(db, t["key"]) for t in db["taxonomy"]}
    blocks["platforms"] = render_platforms(db)
    for name, body in blocks.items():
        pat = re.compile(rf"(<!-- BEGIN {re.escape(name)} -->\n).*?(\n<!-- END {re.escape(name)} -->)", re.S)
        readme, n = pat.subn(lambda m: m.group(1) + body + m.group(2), readme)
        if n != 1:
            print(f"README.md: expected one '{name}' marker pair, found {n}")
            sys.exit(1)
    README_PATH.write_text(readme, encoding="utf-8")
    print(f"README.md updated: {len(db['methods'])} methods, {len(db['datasets'])} datasets")


if __name__ == "__main__":
    main()
