# Verification report — Tiny Engineer Autumn Lab

**Scope:** local dashboard software and inspection of the publicly available author's documentation. **Not:** physical fabrication/assembly qualification.

## Automated checks

Run from the root of the extracted dashboard:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The package includes integration tests that start a real local HTTP server and use a temporary on-disk SQLite database. Covered: 46 steps/8 milestones; strict non-circular previous-step prerequisites; mandatory 3 quality gates + textual evidence; automatic Needs Recheck cascade and library summaries; persistence across connections; invalid dates/settings; inventory; expenses; task journal; create/edit/delete records; version snapshots and restore; JSON backup/import with invalid-import guard; storage optimization; local backups; GitHub configuration guard; JSON/Markdown/HTML/PDF/CSV/all-formats ZIP; invalid milestone; safe static routing and response security headers.

The `tests/e2e_chromium.py` test opens all **ten** screens in Chromium, drives the **actual HTTP server and SQLite backend** using a browser-to-localhost bridge (the browser test environment blocks direct loopback navigation), and checks prerequisite rejection, two-step completion, downstream Needs Recheck, permanent notes/expenses/version snapshots, and the 5 V × 2.5 A power calculation (12.5 W). It re-renders every screen at **390 px mobile width** and asserts no body-level horizontal overflow or browser script errors. This is software end-to-end coverage, not a comprehensive accessibility audit.

## Static evidence for guide structure

- Every numbered task contains an explicit purpose, imperative actions, a pass condition, a troubleshooting branch, an engineering concept and a link to upstream documentation.
- Each task except T001 requires the previous task. The graph is linear and acyclic. Imported backups also reject forged Done tasks that violate prerequisite/evidence gates.
- Steps T019–T039 cover assembly parts §§1–19, including the author's added §2a and §16b sections, and are ordered to respect bench centering, removal of the ESP32 only at §12, reinsertion at §13, and final Desk cable placement. The default runbook uses 2.4 GHz Wi-Fi; the source also offers a USB-only variant, which would require a separate serial verification plan rather than using the HTTP milestones.
- Five motor control positions are mapped to channels CH0–CH4, distinct from ESP32 GPIO numbering.
- Power and SPK− precautions appear before wiring is performed.

## The limits of this verification

The included software was not connected to any real custom PCB, servo, speaker, display or printer. A passed browser/API test cannot prove the CAD prints fit your selected servo clone, JLCPCB placement is correct, the flashed release matches your board, there is sufficient current, or the robot is mechanically safe. Confidence must be established progressively with the **physical pass tests** shown in the guide. Board-manufacturer prices, exact source files and official firmware releases can change. If official sources change, treat the upstream revision as authoritative and record the difference in a project risk/decision entry.

No user-owned repository was modified; the application ships as a separate, independent companion.

## V2 source design and presentation regression (latest run)

- **11/11 Python test cases passed** after adding `test_correct_robot_target_and_offline_docs`. That regression test checks the pinned `jamro/tiny-engineer` source photo link and descriptive offline fallback, assembly/CAD links, 46 current task headings in the standalone Markdown, source-preserving 3MF and §12/§13 transitions, the exact no-walking architecture, the autumn accent palette and neutral charcoal backdrop, the official image CSP allowance and generated PDF file header.
- **Chromium end-to-end test passed** again with the real HTTP backend and temporary SQLite database. All ten screens rendered at desktop and 390 px mobile viewport width; none introduced body horizontal overflow or JavaScript exceptions. The test opened the physical Build Guide task picker, jumped from M01 into M05/T033 and back, checked prerequisites still guard completion, expanded the 14-lesson engineering index, saved and invalidated tasks, submitted journal and expense records, created a version and computed 5 V × 2.5 A = 12.5 W.
- **Documentation consistency checked:** `scripts/generate_build_docs.py` recreates the standalone `docs/BEGINNER_BUILD_GUIDE.md` and `.pdf` from exactly the same 46-step `app/guide_data.py` as the browser guide. All T001–T046 headings and target/assembly milestones appeared in the extracted PDF. The generated PDF is US Letter, with page numbers and visible task-specific pass/fail conditions. First pages were rasterized and visually inspected to address text collision and spacing.
- **Reference photograph limitation:** the official creator image is requested over HTTPS from GitHub at runtime. The isolated test browser could not retrieve it; the intended fallback appeared, with a clearly labeled link to the actual official photograph. No unrelated generic robot image is distributed. The photo rendering itself has **not** been proved on an online browser in this environment.
- **Hardware qualification remains unperformed:** no assembled physical Tiny Engineer unit was present. Visual source conformance and software workflows can be checked, but print fit, torque, current, firmware-to-hardware compatibility and motion must be confirmed against physical parts before marking steps verified.

The last successful run is evidence for this **specific packaged source tree**, not for every future browser, operating system, supplier revision or user modification.

## V2.1: Desktop shortcut + copper theme regression

- Added a short-lived `launch_dashboard.py` entrypoint for Ubuntu `.desktop` launchers with detached server startup, health/readiness polling, port reuse/fallback, browser opener fallbacks and persistent per-user logs.
- Added isolated launcher tests that install a real `.desktop` entry in a temporary HOME, run its generated Exec command with a fake `xdg-open`, confirm a real HTTP server serves `/api/health` and `/`, check that a second click reuses the same process, and check that an occupied port shifts the new server to another port. The tests do not modify the test runner's own GUI or home folder.
- Source theme changed from yellow/gold CTA accents to `#C56A4C` copper with `#E38D71` hover, including the SVG shortcut icon. The original autumn-reference Toffee swatch remains in the optional palette display.
- 14/14 Python tests passed; Chromium end-to-end run passed all 10 desktop and mobile views, interactive state persistence and prerequisite checks. The isolated browser cannot show the remote author image; this is covered by the existing explicit fallback.
- **Remaining environment-dependent check:** launching via an actual Ubuntu/GNOME Dock and opening the user's preferred browser must be verified on the target machine. Automated tests cover desktop-entry generation and the server/browser-opener execution path but cannot reproduce every distribution's desktop trust policies, default-browser registration, or session environment.
