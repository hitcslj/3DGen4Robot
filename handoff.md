# Handoff: README Format Improvements

## What's been done

Awesome List paper tables (122 entries across 10 subsections) have been reformatted from the old `Year | Method | Venue | Paper | Project | Code` layout to the new badge-based format:

```
| Model | Paper | Venue | Website | GitHub |
```

- **Model**: backtick code style (`` `NAP` ``)
- **Paper**: arXiv badge + `<br>` + full title
- **Venue**: verbatim from JS data
- **Website**: green shields.io badge
- **GitHub**: stars badge via `img.shields.io/github/stars/owner/repo`

Data source: `D:\master\My-Paper\3D_Gen_for_Embodied_AI\pages\3dgen4robot.github.io\static\js\collections-data.js`

---

## Next step 1: Reformat Datasets section

The four dataset tables under `## Datasets and Benchmarks` still use the old plain-text format. Convert them to match the screenshot style (similar to papers but adapted for datasets):

### Target format

```
| Model | Paper | Venue | Website |
```

- **Model**: dataset name in backtick code style (`` `ShapeNet` ``)
- **Paper**: if the dataset has an associated paper with arXiv link, show arXiv badge + full title; if no paper, just show the dataset description/title text
- **Venue**: publication venue + year (e.g. `CVPR 2012`)
- **Website**: gold/green "Link" badge pointing to dataset URL

### Data source

`D:\master\My-Paper\3D_Gen_for_Embodied_AI\pages\3dgen4robot.github.io\static\js\datasets-data.js`

Each item has fields: `group`, `category`, `name`, `venue`, `type`, `scale`, `summary`, `phys`, `kin`, `sim`, `url`.

### Section mapping

| JS `group`           | README subsection                |
| -------------------- | -------------------------------- |
| Object Assets        | ### Object-Level Datasets        |
| Scene Datasets       | ### Scene-Level Datasets         |
| Robot Demonstrations | ### Robot Demonstration Datasets |

Plus `### Embodied Benchmarks` (subset of Robot Demonstrations where `category == "Sim-Based Benchmark"`).

### Key decisions needed

- The current dataset tables have extra columns (Type, Scale, Physics/Articulation for objects; Domain, Simulator Compatibility for scenes; Setting, Task Type for robots). Decide whether to:
  - (a) Drop these columns to match the 4-column screenshot format exactly, or
  - (b) Keep some extra columns but add badges to the Name/Link columns

- Dataset items in `datasets-data.js` don't have `pdfUrl` or `pdfUrl`-like fields — the `url` field points to the dataset page. Some datasets have associated papers (e.g., ShapeNet → CVPR 2015) but the arXiv link would need to be looked up separately or omitted.

---

## Next step 2: Non-arXiv paper badge

Currently, papers without arXiv links show one of:
- Plain text title only (no badge at all) — e.g., `PartRM`, `PhysPart`, `DSO`, `CAST`, `PhyScensis`, `Seed3D`
- `[Paper](url)` text link — e.g., `DynScene` (links to thecvf.com)

### What to change

Add a generic paper badge for non-arXiv papers. Suggested format:

```markdown
[![Paper](https://img.shields.io/badge/Paper-PDF-blue)](https://openaccess.thecvf.com/...)
```

### Affected entries (12 total)

Papers with no arXiv ID (neither `pdfUrl` nor `url` contains `arxiv.org`):

| Method | Current state | Has alternative PDF URL? |
| ------ | ------------- | ------------------------ |
| `PartRM` | Title only | No (`url` is project page) |
| `PhysPart` | Title only | No (`url` is project page) |
| `DSO` | Title only | No (`url` is project page) |
| `CAST` | Title only | No (`url` is project page) |
| `PhyScensis` | Title only | No (`url` is project page) |
| `Seed3D` | Title only | No (`url` is project page) |
| `DynScene` | `[Paper](cvf...)` | Yes (thecvf.com PDF) |

For `DynScene`, replace `[Paper](url)` with `[![Paper](https://img.shields.io/badge/Paper-PDF-blue)](url)`.

For the remaining 6 with no PDF link at all, leave as title-only (no badge) since there's nothing to link to — or optionally add a gray "Coming Soon" badge.

### Implementation

Search README for lines in Awesome List tables where the Paper column doesn't start with `[![arXiv` and doesn't contain just `-`. These are the entries to update.

Quick grep to find them:
```bash
grep -n "^| \`" README.md | grep -v "arXiv" | grep -v "^| Model"
```
