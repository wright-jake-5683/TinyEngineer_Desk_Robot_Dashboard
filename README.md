# Tiny Engineer — Desk Robot Studio · Copper Dark V2.1

A **local, persistent dark-mode project dashboard and beginner build course** for the open-source [jamro/tiny-engineer](https://github.com/jamro/tiny-engineer) desktop animatronic robot. Created November 2026. This is an **independent companion**, not the upstream firmware, and it is not affiliated with the upstream author.

**The exact build target is the jamro Tiny Engineer figure seated in a chair behind its miniature desk**: copper/red 3D-printed humanoid, OLED eyes, miniature laptop, coffee mug, service bell and desk lamp. The body has five servo motions (head pitch, neck yaw, left hand, right hand, torso yaw), an OLED face and a speaker. **This is not a walking or wheeled robot.** Visual cross-check: [creator photo](https://github.com/jamro/tiny-engineer/blob/main/docs/tiny-engineer-preview.jpg) · [official 3D assembly](https://tinyengineer.dev/assembly/) · [print part inventory](https://github.com/jamro/tiny-engineer/blob/main/3d_models/README.md). The reference photo loads from GitHub while online; the target checklist and the rest of the dashboard work offline. The default guide targets **five SG90 servos plus the integrated assembled main PCB** and a **2.4 GHz Wi-Fi network** for the later HTTP acceptance tests. The documentation and mechanical steps follow the public author's sequence, including its twenty mechanical sections. Cross-check the official source pages and photos linked on each step, especially if the project is updated.

## Start on Ubuntu / Linux / macOS / Windows

1. Extract the **entire** ZIP to a permanent folder, for example `~/Projects/TinyEngineer_Dashboard/`. Do not run it directly inside the compressed archive. Keep the `app/` directory and the scripts together.
2. Install **Python 3.9 or newer**. No JavaScript framework, Node, cloud account or database server is required for the dashboard itself.
3. Open a terminal in the extracted folder and run:

   ```bash
   python3 start_dashboard.py
   ```

   On Windows, use `py start_dashboard.py` if `python3` is unavailable. A local browser tab should open to **http://127.0.0.1:8782**. If not, enter that exact address manually. Leave the terminal running to keep the server available. Press **Ctrl+C** to stop.
4. Optional but recommended: enable PDF export:

   ```bash
   python3 -m pip install reportlab
   ```

   If your Ubuntu Python installation blocks global package installs, create a virtual environment: `python3 -m venv .venv`, then `.venv/bin/python -m pip install reportlab` and `.venv/bin/python start_dashboard.py`. The included static PDF guide is readable without installing anything.
5. On Ubuntu/GNOME, install **the corrected V2.1 launcher** after extracting to its **permanent** location:

   ```bash
   python3 install_desktop_shortcut.py
   ```

   Find **Tiny Engineer Desk Robot Studio** in Applications, open it, and pin it to your Dock. If a Desktop shortcut appears but is not trusted, right-click and choose **Allow Launching**. The installer replaces `tiny-engineer-dashboard.desktop` in the application menu and, if present, on your Desktop. If you pinned an older application shortcut and it still does nothing, unpin the old icon and pin the newly installed entry. Do not move the extracted project folder after installing the launcher; reinstall it if the folder moves.

   **What changed in V2.1:** the shortcut now executes `launch_dashboard.py`, which launches the server **detached from the desktop icon**, waits for `/api/health`, and uses `xdg-open` (or `gio open`) to launch the default browser. Clicking twice opens the already-running **V2.1** server instead of failing with an occupied-port error. If an older dashboard owns port 8782, V2.1 tries the next free local port.

   **If it still does not open**, run the same launcher in a terminal to see an error or copy the log path:

   ```bash
   python3 launch_dashboard.py
   cat ~/.local/state/tiny-engineer-dashboard/launcher.log
   tail -n 40 ~/.local/state/tiny-engineer-dashboard/server.log
   ```

   For systems with `XDG_STATE_HOME` configured, the log folder is `$XDG_STATE_HOME/tiny-engineer-dashboard/`. You can also open `http://127.0.0.1:8782/` manually if the server is running on the default port. `xdg-open` and a logged-in graphical desktop session are required for automatic browser opening on most Linux desktops. If you previously launched V2, close the old instance before relying on V2.1 data changes; both versions share the same SQLite path.

### Alternate port and data folder

```bash
python3 start_dashboard.py --port 8783
python3 start_dashboard.py --data-dir ~/Projects/tiny-engineer-progress
python3 start_dashboard.py --no-browser
```

These flags may be combined. Do not expose this development-only local app to the public Internet or forward its port on your router.

## First session — a recommended path

1. Open **Build Guide → T001**. Read the purpose, precise instructions, safety restrictions, exit test, failure procedure and engineering example.
2. Review **M01** before buying anything. Keep the default **SG90 + integrated main PCB** architecture unless you deliberately fork the project plan. Changing the servo label in Settings does **not** regenerate the physical guide for a different servo model.
3. Complete tasks **in order**. To mark one `Done`, check Prepared, Performed and Verified and write your **own observed evidence**. An unfinished previous task blocks premature completion.
4. Log your shopping receipts in **Parts & Expenses**, note print fits/measurements and experiments in the **Task Chat & Engineering Journal**, and save a version at important checkpoints.
5. Use **Engineering Lab** to understand torque, PWM, bus wiring, electrical power and tolerance. Its calculators are illustrative and never stand in for measurement.
6. Keep your work: **Project Library → Export All** generates JSON, Markdown, HTML, PDF and CSV in one ZIP. **Settings → Create Project Version** stores a local snapshot, while **Backup Local** saves a JSON file to the backups folder. **GitHub Backup** is optional and needs a configured private GitHub repository and working external Git authentication.

## Features

- Overview: real official-design source photograph and physical acceptance checklist, next task, quiet project pulse; expandable full goal, completion trend, forecast, budget, recent steps and milestones.
- Today: suggested tasks, schedule/evidence, save point and recent completed tasks.
- Next Day: scheduled tasks and three-item Work Carrying Forward with duration estimates.
- Build Guide: **46 sequential steps across eight milestones**, with prominent actions and physical exit tests, collapsible engineering and references, an optional full task index, manual evidence gates and task journal.
- Engineering Lab: **14 beginner engineering lessons**, power and gravity-torque calculators and verified project pin/channel assignments.
- Roadmap: interactive milestone detail, dependencies and time estimates.
- Project Library: per-milestone folders, automatically written completion summaries, editable records and individual/all export formats.
- Parts & Expenses: itemized estimated purchasing list, editable actual prices, purchased flags, running receipts, target budget and remaining balance.
- Decisions & Risks: maintainable records with status and ownership by milestone.
- Project Settings: editable budget, dates, scope, baseline and weekly hours; version snapshots/restore; storage monitor and threshold warnings; WAL checkpoint/SQLite VACUUM; local JSON export/import; optional GitHub backup; desktop launcher instructions.

## Persistence, location and backups

Your live data is stored in **SQLite** on your own machine, by default:

```
~/.local/share/tiny-engineer-dashboard/project.sqlite3
```

This is not the same directory as the app source. Unzipping or upgrading the app in a different directory does not destroy the original SQLite database. Do not delete SQLite `-wal` or `-shm` files while the app is running. Backups are written in `~/.local/share/tiny-engineer-dashboard/backups/`. A JSON export can be imported on another machine running a compatible dashboard version. Before any import, the app automatically writes a pre-import JSON backup.

Because the app runs on `127.0.0.1`, the data cannot be reached directly from other devices. **This is not a hardened multi-user server**, and its automatic GitHub backup may include private journal notes. Back up to a **private** repository if notes contain personal information. Do not type passwords, access tokens or secrets into the dashboard.

## Critical power and hardware safety

- Use **regulated 5 V and at least 2 A** to the **main PCB's USB-C**. Do not power servos through the ESP32's 3.3 V output.
- The amplifier speaker output is **SPK+ / SPK−**; **SPK− is not ground**. Use the speaker plug **or** the solder pads, never both.
- Power **off before rewiring**. Test servo movement with mechanical space and no fingers near joints. Check orientation using board silkscreen rather than color alone.
- Flash the stock firmware and center servos **on the bench** before building the enclosure. Leave the ESP32 seated in the bench PCB throughout the early §3–§7 centering. Only after those operations, power off and remove the module before placing the PCB inside the Desk at §12, then reinstall the ESP32 from above the Desk at §13. Avoid trapped cables.
- The guide is **not** a guarantee of correct wiring, correct fabrication, sufficient servo torque, or safety in physical operation. Validate the actual boards, printed dimensions and motion in person.

## Pricing and printing caveats

The starter BOM totals **$192.85 (estimate, USD, before tax/shipping)** and assumes access to a 3D printer. The assembled board is a **$130 planning allowance, not a verified JLCPCB checkout quote**. Actual costs may be much higher; enter receipts in Parts & Expenses to replace estimates. You must download the official PCB manufacturing files, project firmware and printable models from the **upstream GitHub/project website**; this companion does not redistribute or change them.

## Quality assurance and known limits

Run software tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

For an optional Chromium end-to-end test against a real local server and SQLite database, install Playwright and Chromium, then run:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
python3 tests/e2e_chromium.py
```

Playwright is **not** needed to run the normal dashboard. The browser test uses a local request bridge for compatibility with restricted test environments.

**What has been tested:** HTTP routes, SQLite persistence, prerequisite quality gates, automatic downstream invalidation, task journals, expense logging, version restore, backups, JSON import guards, and JSON/PDF/HTML/Markdown/CSV/all-formats exports; all ten screens were rendered in a Chromium browser and interactive calculator/task controls checked. The testing report is in `docs/TEST_REPORT.md`.

**What is not tested:** fabricating JLCPCB boards, plugging actual physical parts, printing/assembling STL/3MF models, the stock firmware's current release against your exact hardware, network setup on your router, and live servo/LED/OLED/audio behavior. These require real hardware, and **100% build certainty is not technically credible without those tests**. The pass conditions and failure branches in the guide help you test that yourself.

## Contents

- `start_dashboard.py` — direct server launcher (terminal use).
- `launch_dashboard.py` — resilient detached desktop launcher, local-port detection, default-browser opener, diagnostics.
- `install_desktop_shortcut.py` — Ubuntu/GNOME launcher installer (V2.1).
- `app/server.py` — local HTTP API, persistent SQLite and exports.
- `app/index.html`, `app/app.js`, `app/style.css`, `app/concepts.js` — interface and engineering course.
- `app/guide_data.py` — complete task/lesson seed content.
- `docs/BEGINNER_BUILD_GUIDE.md` and `.pdf` — synchronized printable 46-step reference guide.
- `docs/TARGET_DESIGN_SPEC.md` — source-locked final design, exact printable inventory, visual/electrical acceptance.
- `scripts/generate_build_docs.py` — rebuilds the Markdown and PDF guides from the dashboard task definitions (requires ReportLab).
- `docs/ENGINEERING_REFERENCE.md` — concepts without opening the dashboard.
- `docs/TEST_REPORT.md` — software test evidence and hardware limitations.
- `dashboard_preview.png` — screenshot of the completed overview.

## Upstream source

- [jamro/tiny-engineer](https://github.com/jamro/tiny-engineer)
- [Getting started](https://github.com/jamro/tiny-engineer/blob/main/docs/getting-started.md)
- [Shopping list](https://github.com/jamro/tiny-engineer/blob/main/docs/shopping.md)
- [Mechanical assembly](https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md)
- [Power](https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/power.md)
- [Testing](https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/testing.md)

Original reference palette (still visible under project details): Night Rider `#22100E`; Dark Sienna `#421414`; Cigar Brown `#7A3D1B`; Toffee `#BD832D`; Camouflage `#796925`; Gray Green `#494437`.

## Upgrade from Autumn Lab V1

The V2 dashboard uses the **same SQLite schema and default data folder** as V1. Before launching V2, quit V1, use Settings → Export All ZIP or JSON Working Copy, and keep the backup. Then run the V2 folder. Old task statuses, notes and expenses persist. The 46 task IDs are unchanged, though T001, T010, T044 and T046 now emphasize conformance to the source design. Previously marked completion is **not** independent proof that the newly emphasized target inspection has been performed; explicitly revisit those steps and mark Needs Recheck if required.

### Provenance / limitations

- Authoritative source: [jamro/tiny-engineer](https://github.com/jamro/tiny-engineer), with [creator target photo](https://github.com/jamro/tiny-engineer/blob/8821a07969788f52c232cab2c377d797524d4334/docs/tiny-engineer-preview.jpg).
- Dashboard is an independent companion. Official geometry and assembly win if the repository changes.
- Browser, persistence, exports, and prerequisite tests are software checks only. Physical dimensions, fastener engagement, electrical safety and motion clearance require hands-on testing with your exact prints, PCB and servos.
- V2.1 uses charcoal panels and **copper/rust-red** `#C56A4C` for action buttons, active navigation, charts, icon, focus outlines and progress. Its hover color is `#E38D71`. The original six-color autumn photograph's exact Toffee `#BD832D` swatch is retained in the optional reference panel, not the primary accent.

## V2.1 shortcut and copper fixes

- Installer now uses a quoted, absolute path to `launch_dashboard.py` and the installed Python interpreter, supports spaces in folder paths, uses the XDG applications folder and installs a user-executable `.desktop` file.
- V2.1 launcher starts an independent HTTP server, checks startup health, reuses its running process when clicked repeatedly, tries the next available port when another application occupies the default, and opens the browser with OS tools.
- Failures and startup information are written to `~/.local/state/tiny-engineer-dashboard/launcher.log` and `server.log`. The desktop shortcut remains functional after its starter process exits.
- Interface accent `#C56A4C` (copper red), bright hover `#E38D71`; charcoal card backgrounds and the 46 build steps remain unchanged.
- Run `python3 -m unittest discover -s tests -p 'test_*.py' -v` to include desktop-launcher regression tests. The installer tests use a fake browser and isolated HOME; they do not modify your actual desktop or SQLite data. GNOME trust prompts and real local browsers should still be verified on your machine.
