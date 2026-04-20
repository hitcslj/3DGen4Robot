# Plan: Populate the Awesome List in README.md

This plan tells a downstream executor (Sonnet) exactly how to fill in the `README.md` awesome-list tables from two authoritative sources of truth:

- `D:\master\My-Paper\3D_Gen_for_Embodied_AI\pages\3dgen4robot.github.io\static\js\collections-data.js` → papers (122 items)
- `D:\master\My-Paper\3D_Gen_for_Embodied_AI\pages\3dgen4robot.github.io\static\js\datasets-data.js` → datasets (40 items)

Cross-check only (not for table data): `D:\master\My-Paper\3D_Gen_for_Embodied_AI\survey\sec\*.tex` (taxonomy is already reflected in the JS files — use the tex only to resolve ambiguity about a paper's category).

---

## 1. File to edit

Only edit `D:\master\My-Paper\3D_Gen_for_Embodied_AI\pages\3DGen4Robot\README.md`. Do not touch any other file.

Replace every `TBD | To be updated | ...` row in the tables below. Preserve the surrounding prose, headings, and non-table content unchanged.

---

## 2. Source → Destination mapping

### 2.1 Paper tables (from `collections-data.js`, field `window.COLLECTIONS_DATA.value`)

Each item has fields: `domain`, `category`, `citeKey`, `title`, `venue`, `url`, `authors`, `projectUrl`, `pdfUrl`, `codeUrl`.

Map `(domain, category)` → README subsection:

| JS `domain`             | JS `category`              | README subsection                                  | Expected count |
| ----------------------- | -------------------------- | -------------------------------------------------- | -------------- |
| Data Generator          | Articulated Objects        | ### Data Generator → Articulated Object Generation | 26             |
| Data Generator          | Physically-grounded Objects| Physically-Grounded Object Generation              | 13             |
| Data Generator          | Deformable Objects         | Deformable Object Generation                       | 5              |
| Data Generator          | End-to-End Pipelines       | End-to-End Sim-Ready Asset Pipelines               | 4              |
| Simulation Environments | Structure-Driven           | Simulation Environments → Structure-Driven Scene Generation | 8     |
| Simulation Environments | Controllable               | Controllable Scene Generation                      | 9              |
| Simulation Environments | Agentic                    | Agentic and Task-Oriented Scene Generation         | 18             |
| Sim2Real Bridge         | Digital Twin               | Sim2Real Bridge → Digital Twin Construction        | 15             |
| Sim2Real Bridge         | Data Augmentation          | Data Augmentation                                  | 10             |
| Sim2Real Bridge         | Task & Demo Generation     | Synthetic Demonstration and Task Generation        | 14             |

Total = 122. If your final count mismatches, you missed items — re-check.

### 2.2 Dataset tables (from `datasets-data.js`, field `window.DATASETS_DATA.items`)

Each item has fields: `group`, `category`, `name`, `venue`, `type`, `scale`, `summary`, `phys`, `kin`, `sim`, `url` (plus `robot` for Robot Demonstrations).

Map `group` → README subsection under `## Datasets and Benchmarks`:

| JS `group`           | README subsection            | Expected count |
| -------------------- | ---------------------------- | -------------- |
| Object Assets        | ### Object-Level Datasets    | 17             |
| Scene Datasets       | ### Scene-Level Datasets     | 11             |
| Robot Demonstrations | ### Robot Demonstration Datasets | 12         |

The fourth subsection in the README, `### Embodied Benchmarks`, is **not** a `group` in the JS. Populate it from `group == "Robot Demonstrations"` AND `category == "Sim-Based Benchmark"` (7 items: RoboTwin, RoboTwin 2.0, RoboCasa, ManiSkill2/3, RLBench, LIBERO, CALVIN). These items will therefore appear in **both** Robot Demonstration Datasets and Embodied Benchmarks — that duplication is acceptable because the two sections answer different questions (data corpus vs evaluation platform).

---

## 3. Column derivations for paper tables

Every paper table uses columns: `Year | Method | Venue | Paper | Project | Code`.

### 3.1 Year
Parse from the `venue` string by extracting the two-digit year after the apostrophe and prepending `20`. Examples:

- `"NeurIPS '23"` → `2023`
- `"CVPR '25"` → `2025`
- `"arXiv '26"` → `2026`
- `"ToG (SIG. '25)"` → `2025` (take the digits in `'25`)
- `"SIG. Asia '25"` → `2025`
- `"CVPR Find. '26"` → `2026`
- `"ICRA '26"` → `2026`

### 3.2 Method
Take the short name from the `title` (text before the first colon or dash). If the title has no colon/dash, use the leading noun phrase.

Examples:
- `"NAP: Neural 3D Articulated Object Prior"` → `NAP`
- `"CAGE: Controllable Articulation Generation"` → `CAGE`
- `"Structured 3D Latents for Scalable and Versatile 3D Generation"` (TRELLIS) → `TRELLIS` (special-case: this paper is widely known as TRELLIS; infer from URL `microsoft.github.io/TRELLIS`)
- `"Physically Compatible 3D Object Modeling from a Single Image"` → `Physically Compatible 3D` (no short name — use a concise phrase)
- `"Real2code: Reconstruct Articulated Objects via Code Generation"` → `Real2Code`

Heuristic: if the first token (before `:`) is ≤4 words and reads like a name/acronym, use it; otherwise fall back to the `citeKey` stripped of the leading author+year (e.g. `guo2024physically` → title phrase). When in doubt, prefer the short handle used on the project page URL.

### 3.3 Venue
Use the JS `venue` field **verbatim** (e.g. `NeurIPS '23`, `arXiv '25`, `ToG (SIG. '25)`).

### 3.4 Paper
Link text: `[arXiv]` if the link contains `arxiv.org`, otherwise `[Paper]`.
- If `pdfUrl` is non-empty, use it.
- Else if `url` is non-empty and looks like a paper (arxiv.org, openaccess.thecvf.com, etc.), use `url`.
- Else render `-`.

Final cell: `[arXiv](https://arxiv.org/abs/XXXX.XXXXX)` or `-`.

### 3.5 Project
- If `projectUrl` is non-empty, render `[Page](projectUrl)`.
- Else if `url` is a project-page-looking URL (github.io, custom domain, not arxiv) AND different from the paper URL, use `url`.
- Else render `-`.

### 3.6 Code
- If `codeUrl` is non-empty, render `[GitHub](codeUrl)` (or `[Code]` if it's not GitHub).
- Else `-`.

### 3.7 Empty-string rule
The JS data uses `""` (empty string) for missing links — treat that as missing and render `-`. Never emit a markdown link with an empty href.

### 3.8 Row ordering within each subsection
Sort by `Year` ascending (oldest → newest). Within the same year, preserve the order in which items appear in `collections-data.js` (that is already a meaningful curated order). Do **not** alphabetize.

### 3.9 Example row (Articulated Object Generation)

```
| 2023 | NAP | NeurIPS '23 | [arXiv](https://arxiv.org/abs/2305.16315) | [Page](https://www.cis.upenn.edu/~leijh/projects/nap) | - |
```

### 3.10 Starter row to preserve
`| 2025 | EmbodiedGen | NeurIPS | Coming soon | Coming soon | Coming soon |` already exists in the README under Articulated Object Generation, but EmbodiedGen actually belongs under **End-to-End Sim-Ready Asset Pipelines** (`citeKey: wang2025embodiedgen`, category `End-to-End Pipelines`). Remove it from Articulated and let it come in naturally in End-to-End Pipelines.

---

## 4. Column derivations for dataset tables

### 4.1 Object-Level Datasets — `| Name | Type | Scale | Physics / Articulation | Link |`
- Name: `name`
- Type: `type`  (e.g. `CAD Models`, `Real Scans`, `Mixed`, `Artist-designed`, `Sim. Env.`)
- Scale: `scale`
- Physics / Articulation: combine the `phys` and `kin` flags as `Phys: <phys>, Kin: <kin>` (e.g. `Phys: Yes, Kin: Yes`). If both are `No`, write `None`.
- Link: `[Link](url)` using `url`. If `url` empty, `-`.
- Sort by venue year ascending (parse year the same way as §3.1), ties by original order.

### 4.2 Scene-Level Datasets — `| Name | Domain | Simulator Compatibility | Link |`
- Name: `name`
- Domain: `category` (`Source Scene`, `Generated Scene`, `Domain-oriented Scene`) + ` / ` + `type` (e.g. `Source Scene / Real Scans`).
- Simulator Compatibility: `sim` (`Yes` / `No` / `Partial`).
- Link: `[Link](url)`.
- Sort by year asc.

### 4.3 Robot Demonstration Datasets — `| Name | Setting | Task Type | Link |`
- Name: `name`
- Setting: combine `type` (Real / Sim / Both) and `robot`, e.g. `Real — Franka Panda (18 robots)`.
- Task Type: `summary` (one short phrase — trim if >60 chars).
- Link: `[Link](url)`.

### 4.4 Embodied Benchmarks — `| Name | Focus | Simulator | Link |`
Source subset: `group == "Robot Demonstrations"` AND `category == "Sim-Based Benchmark"` (7 items).
- Name: `name`
- Focus: first clause of `summary` (before first comma).
- Simulator: parse from `robot` field — the parenthetical (e.g. `Franka (robosuite/MuJoCo)` → `robosuite / MuJoCo`; `SAPIEN` for RoboTwin; `Franka Panda (CoppeliaSim)` → `CoppeliaSim`; `Franka Panda (PyBullet)` → `PyBullet`; `Multi-robot (SAPIEN)` → `SAPIEN`).
- Link: `[Link](url)`.

---

## 5. Special items / known edge cases

- **EmbodiedGen**: belongs to End-to-End Pipelines, not Articulated (see §3.10).
- **RoboTwin and RoboTwin 2.0** appear in both *Robot Demonstration Datasets* and *Embodied Benchmarks* — intentional.
- **TRELLIS / TRELLIS.2**: infer the short name from the URL, not the title.
- **RoboScape** (`sim2real_bridge.Digital Twin`): `authors` is empty — still include the row; Method name = `RoboScape`.
- **TwinAligner**: `authors` is empty — OK, include it.
- **PhysPart, DSO, CAST, SceneCraft, physcensis, scenethesis, 3d-generalist, dynscene, pat3d, guo2024physically, gavryushin2025sight, liu2025robotransfer, gaf, xu2025egodemogen, manipdreamer3d, draw2act, video2act**: `pdfUrl` is empty — fall back to `url` for the Paper column (these are mostly arxiv.org links already in `url`).
- **manitwin**, **scenegen**, a few '26 papers use arxiv IDs like `2601.*` / `2602.*` / `2603.*` — these are valid post-2026 preprint IDs, keep as-is.
- **Venues containing parentheses** (`ToG (SIG. '24)`, `ToG (SIG. '25)`): preserve verbatim in the Venue column.
- **Method extraction from URL**: for TRELLIS-like cases, use the last path segment of the project URL (strip trailing slash).

---

## 6. Sections to leave untouched

Do not modify:
- Header block (title, badges, intro paragraph)
- `## Highlights`
- `## Table of Contents`
- `## Scope and Taxonomy`
- `## Simulators and Formats` (already populated)
- `## Evaluation`
- `## Citation`

Only modify the tables under `## Awesome List` and under `## Datasets and Benchmarks`.

---

## 7. Execution recipe (for Sonnet)

1. Read `collections-data.js` in full (1469 lines — use `offset`/`limit` or multiple Reads; do **not** Grep for content, you need every field).
2. Read `datasets-data.js` in full (480 lines — one Read call is fine).
3. For each of the 10 paper subsections, build the table rows in memory following §3. Verify the count matches the expected counts in §2.1.
4. For each of the 4 dataset subsections, build the rows following §4. Verify counts.
5. Apply edits to `README.md` using `Edit` with `old_string` = the existing TBD block (including the header row and separator) and `new_string` = the new populated table. One Edit per subsection.
6. After all edits, re-read the README and verify:
   - Every subsection has at least one data row (no remaining `TBD`).
   - Row counts per paper subsection match §2.1.
   - No markdown link has an empty `()`.
   - Table pipes are aligned (not strictly required for rendering, but aim for clean diff).
7. Do **not** commit. Report back what changed and any ambiguities you resolved.

---

## 8. Verification checklist

- [ ] 122 paper rows total across Awesome List
- [ ] 17 rows in Object-Level Datasets
- [ ] 11 rows in Scene-Level Datasets
- [ ] 12 rows in Robot Demonstration Datasets
- [ ] 7 rows in Embodied Benchmarks
- [ ] No `TBD` / `To be updated` strings remain under `## Awesome List` or `## Datasets and Benchmarks`
- [ ] No `[text]()` empty-link artefacts
- [ ] EmbodiedGen appears under End-to-End Pipelines, not Articulated
- [ ] Simulators and Formats / Evaluation / Citation sections unchanged

---

## 9. Out of scope for this plan

- Adding venues not in the JS (don't invent entries from the tex).
- Restructuring the taxonomy (the README headings and JS categories are the contract).
- Editing CSS/HTML of the project page — only the Markdown README.
- Writing the arXiv / bibtex citation (the citation block is already a placeholder and left as-is).
