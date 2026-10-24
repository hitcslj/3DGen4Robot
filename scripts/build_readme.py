"""Regenerate the paper tables in README.md from data/papers.yaml.

    python scripts/build_readme.py           # validate the data, then rewrite the tables
    python scripts/build_readme.py --check   # validate only; exit 1 if anything is wrong

Each table lives between a pair of markers in README.md, e.g.
    <!-- BEGIN papers:articulated -->  ...  <!-- END papers:articulated -->
Only the text between markers is replaced; everything else in the README is hand-written.
Each generated table is wrapped in an open <details> block whose summary gives the entry count,
so readers can fold it.
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
DATASET_SECTIONS = {"object_datasets", "scene_datasets", "demo_datasets", "benchmarks", "evaluation"}
DATASET_HEADER = {"object_datasets": "Dataset", "scene_datasets": "Dataset", "demo_datasets": "Dataset",
                  "benchmarks": "Benchmark", "evaluation": "Benchmark / Metric"}
DATASET_NOUN = {"object_datasets": "dataset", "scene_datasets": "dataset", "demo_datasets": "dataset",
                "benchmarks": "benchmark", "evaluation": "entry"}
NEW_MARK = " 🆕"  # additions first released in or after `new_since` (see is_new)


def load():
    return yaml.safe_load(DB_PATH.read_text(encoding="utf-8"))


def validate(db):
    errors = []
    if not re.match(r"^\d{4}-\d\d$", str(db.get("new_since", ""))):
        errors.append("new_since: give the first release month after the survey as YYYY-MM")
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
            for rel in e.get("related", []):
                if not rel.get("name") or not (rel.get("arxiv") or rel.get("url")):
                    errors.append(f"{where}: each 'related' item needs a name and an arxiv id or url")
            ident = (e.get("section"), e.get("arxiv") or e.get("name"))
            if ident in seen:
                errors.append(f"{where}: duplicate entry in section '{e.get('section')}'")
            seen.add(ident)
    for i, p in enumerate(db.get("platforms", [])):
        where = f"platforms[{i}] {p.get('name', '?')}"
        for field in ("name", "type", "strengths", "website"):
            if not p.get(field):
                errors.append(f"{where}: missing '{field}'")
        if p.get("in_paper") is False and not re.match(r"^\d{4}-\d\d$", str(p.get("date", ""))):
            errors.append(f"{where}: a platform added after the survey needs 'date' as YYYY-MM")
        for u in p.get("updates", []):
            if not u.get("name") or not str(u.get("url", "")).startswith(("http://", "https://")):
                errors.append(f"{where}: each 'updates' item needs a name and a url")
    return errors


def sort_key(e):
    if e.get("arxiv"):
        yymm, num = str(e["arxiv"]).split(".")
        return (f"20{yymm[:2]}-{yymm[2:]}", int(num))
    date = str(e.get("date", "0000"))
    return (date if len(date) > 4 else date + "-12", 0)


def is_new(e, since):
    # added after the survey and first released after its April 2026 version
    return e.get("in_paper") is False and sort_key(e)[0] >= since


def paper_cell(e):
    title = e["title"].replace("|", "\\|")
    if e.get("arxiv"):
        a = e["arxiv"]
        badge = f"[![arXiv](https://img.shields.io/badge/arXiv-{a}-b31b1b.svg)](https://arxiv.org/abs/{a})"
    else:
        badge = f"[![Paper](https://img.shields.io/badge/Paper-PDF-blue)]({e['paper_url']})"
    cell = f"{badge} <br> {title}"
    if e.get("related"):
        links = ", ".join(f"[{r['name']}]({rel_url(r)})" for r in e["related"])
        cell += f" <br> ↳ also: {links}"
    return cell


def rel_url(r):
    return f"https://arxiv.org/abs/{r['arxiv']}" if r.get("arxiv") else r["url"]


def name_cell(e, since):
    return f"`{e['name']}`" + (NEW_MARK if is_new(e, since) else "")


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


def collapsible(body, entries, noun, since):
    n, n_new = len(entries), sum(is_new(e, since) for e in entries)
    label = f"{n} {noun}" if n == 1 else f"{n} {noun[:-1] + 'ies' if noun.endswith('y') else noun + 's'}"
    if n_new:
        label += f" ({n_new}{NEW_MARK})"
    return f"<details open>\n<summary>{label}</summary>\n\n{body}\n\n</details>"


def render_section(db, key):
    since = db["new_since"]
    if key in DATASET_SECTIONS:
        entries = sorted((e for e in db["datasets"] if e["section"] == key), key=sort_key)
        rows = [[name_cell(e, since), paper_cell(e), e["venue"], e.get("details", "-"), project_cell(e.get("website"))]
                for e in entries]
        body = table([DATASET_HEADER[key], "Paper", "Venue", "Details", "Website"], rows)
        return collapsible(body, entries, DATASET_NOUN[key], since)
    entries = sorted((e for e in db["methods"] if e["section"] == key), key=sort_key)
    rows = [[name_cell(e, since), paper_cell(e), e["venue"], project_cell(e.get("project")), code_cell(e.get("code"))]
            for e in entries]
    body = table(["Model", "Paper", "Venue", "Website", "GitHub"], rows)
    return collapsible(body, entries, "paper", since)


def render_platforms(db):
    since, rows = db["new_since"], []
    for p in db.get("platforms", []):
        updates = ", ".join(f"[{u['name']}]({u['url']})" for u in p.get("updates", [])) or "-"
        rows.append([p["name"] + (NEW_MARK if is_new(p, since) else ""), p["type"], p["strengths"], updates,
                     f"[![Website](https://img.shields.io/badge/Website-blue)]({p['website']})"])
    body = table(["Platform", "Type", "Strengths", "Recent Updates", "Link"], rows)
    return collapsible(body, db.get("platforms", []), "platform", since)


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
