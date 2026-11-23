# Tiny Engineer · Desk Robot — V2 Beginner Build Guide

**Authoritative physical target:** the original [jamro/tiny-engineer](https://github.com/jamro/tiny-engineer) **seated desktop animatronic** behind a miniature desk, not a walking or wheeled robot. Use the creator’s [source photograph](https://github.com/jamro/tiny-engineer/blob/main/docs/tiny-engineer-preview.jpg), [interactive assembly viewer](https://tinyengineer.dev/assembly/) and [SG90 printable models](https://github.com/jamro/tiny-engineer/tree/main/3d_models) to compare the intended outcome before any fabrication.

The robot has a printed chair, seated Head/Neck/Chest/Belly assembly, two articulated hands, an OLED face, miniature desk with laptop, mug, bell, lamp and emblem, and the desk-mounted electronics. The five SG90 joints are head pitch, neck yaw, left hand, right hand and torso rotation. It is a **USB-powered, stationary robot**.

**Verification status:** the application and steps have been statically checked and tested in software. The components have **not** been physically built or tested here. Do not mark a step as physically complete until you perform its exit test and record the actual observation.

## How to use this guide

1. Work on **one numbered task at a time**. Each step is a prerequisite for the next; never jump ahead to unblock a failure.
2. Read **Purpose → Actions → Acceptance test → If it fails**. Use the engineering note to understand why the step exists.
3. Keep the project hardware consistent: **five SG90 servos, SG90 print preset, integrated main control PCB, ESP32-C3-Zero**, and a **regulated 5 V, at least 2 A** USB power supply.
4. Keep the ESP32 with the bench PCB during the original §2a–§7 servo-centering procedures. Remove it **only when powered off** just before installing the board in Desk §12, then reinstall it from above in §13.
5. The fixed guide assumes **2.4 GHz Wi-Fi**, because the later HTTP health and subsystem checks require network access. USB-only setup is an alternative branch, not interchangeable with those steps.
6. If a physical fit, wire, heat, power, servo angle or sound check fails, stop that part of the build and use its troubleshooting branch. Recheck downstream tasks after changing an earlier step.

## Final-design acceptance checklist

- [ ] **Seated humanoid:** Head, Hat, Neck, Chest, Belly, BellyJoint, chair and both side seats match the official CAD placement.
- [ ] **Miniature desk:** Desk, DeskTop, DeskPad, front emblem, bottom cover, laptop, mug, bell and lamp are assembled per source.
- [ ] **Face and sound:** SSD1306 128×32 OLED sits in the Head, and 8 Ω / 1 W speaker is wired safely to amplifier output.
- [ ] **Five movements:** Head pitch (CH0), neck yaw (CH1), left hand (CH2), right hand (CH3), torso rotation (CH4) are individually tested.
- [ ] **Electronics:** integrated PCB and ESP32-C3-Zero mount inside/through desk as shown by source, powered using board USB-C 5 V supply.
- [ ] **Evidence:** each required physical exit test was actually performed and recorded; no unresolved binding, rubbing, heating or power faults.

A match to a photograph is not a substitute for measuring mating geometry, electrical polarity, clearances or load on an actual build.

## Safety notes

- Turn **power off before connecting or disconnecting** motors, speaker, display or controller.
- Never connect **SPK− to ground**; use the speaker connector **or** the solder pads, not both.
- Never power servo motors from the ESP32’s **3.3 V** pin. Do not substitute a 9 V or 12 V adapter.
- Keep fingers, wires, printed parts and hair away from moving joints during calibration or tests.
- Inspect PCB markings and the official wiring diagram rather than relying on assumed cable colors.

## Baseline bill of materials — planning estimate only

| Item | Qty | Estimated unit cost (USD) | Extended cost (USD) |
|---|---:|---:|---:|
| Assembled main control PCB | 1 | $130.00 | $130.00 |
| Waveshare ESP32-C3-Zero | 1 | $7.00 | $7.00 |
| SG90 analog micro servo | 5 | $3.00 | $15.00 |
| Adafruit Mini Oval 8Ω 1W speaker | 1 | $1.95 | $1.95 |
| Waveshare 0.91-inch OLED 128×32 | 1 | $6.00 | $6.00 |
| M2 screw/nut assortment | 1 | $12.00 | $12.00 |
| 5V ≥2A USB adapter | 1 | $8.00 | $8.00 |
| USB-C DATA cable | 1 | $4.95 | $4.95 |
| Short M–F jumper pack (≥10) | 1 | $1.95 | $1.95 |
| PLA/PETG filament used per build | 1 | $6.00 | $6.00 |

**Estimated component subtotal: $192.85, excluding shipping, taxes and tools.** Assembled PCB price is an **unverified planning allowance**, not a supplier quote.

## Sequential build tasks

## M01 · Understand & plan

Plan the build, choose the exact hardware variant, and establish safe expectations.

### T001 · Identify the robot and final outcome

**Estimated hands-on time:** 20 min. **Depends on:** None.

**Purpose:** Establish an unambiguous physical design target before buying, printing or wiring; every later assembly step must serve this seated desk robot.

**Actions:**
1. Open the creator’s photo (docs/tiny-engineer-preview.jpg) and official 3D assembly viewer. The finished object must be a seated copper-colored humanoid behind a black miniature desk, with an OLED face and miniature laptop, mug, bell, and lamp.
2. Open the official assembly instructions and identify the printed Head, Hat, Neck, Chest, Belly, BellyJoint, Chair, two seats, Desk, DeskTop, DeskPad, BottomCover, arm parts, laptop, mug, bell and lamp on the source parts list.
3. Write the five independent joint motions: head pitch, neck yaw, left hand, right hand, torso rotation.
4. Confirm it is a USB-powered stationary desktop animatronic, not a walking or wheeled robot. Record the official image, CAD and assembly links in your notes.

**Pass condition — what you must actually verify:** Your written target checklist matches the creator’s photo and assembly map, with seated figure, desk props, OLED face and five named joints. Treat photos as reference only; physical geometry comes from SG90 CAD.

**If it does not pass:** Return to the README before changing scope. Do not invent locomotion features.

**Engineering concept:** Systems engineering

**Equation / relationship:** `Requirement → measurable acceptance test`

**Example:** Requirement: “respond to agent event”; proof: trigger a supported animation.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/getting-started.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T002 · Choose one servo model and geometry

**Estimated hands-on time:** 20 min. **Depends on:** T001.

**Purpose:** The servo pocket dimensions determine the printed robot geometry.

**Actions:**
1. Choose five Tower Pro SG90 micro servos for this first build.
2. Write SG90 in project settings.
3. Use only the matching parts/sg90 print folder; do not mix compact servo models.

**Pass condition — what you must actually verify:** Exactly five matching servos are chosen; printed files come from parts/sg90.

**If it does not pass:** If stock differs, stop and reselect the entire servo + CAD preset together.

**Engineering concept:** Tolerance & compatibility

**Equation / relationship:** `clearance = printed pocket width − actual servo width`

**Example:** A negative clearance means a servo cannot be inserted without force.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/shopping.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T003 · Select the electrical architecture

**Estimated hands-on time:** 20 min. **Depends on:** T002.

**Purpose:** One architecture keeps the build guide unambiguous and avoids mixing incompatible instructions.

**Actions:**
1. Choose the integrated main control board for this baseline.
2. Write that this board already contains the PCA9685 servo driver, MAX98357A amplifier, and USB-C interface.
3. Keep the modular breakout wiring as an alternative only if the integrated-board plan changes.

**Pass condition — what you must actually verify:** One electrical architecture is selected; breakout-only parts are not accidentally double-purchased.

**If it does not pass:** If you choose breakout boards, stop and follow the repository wiring and modular assembly guides.

**Engineering concept:** Architecture & interfaces

**Equation / relationship:** `module → interface → load`

**Example:** ESP32 commands PCA9685 over I²C; PCA9685 makes servo control pulses.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/shopping.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T004 · Read the electrical safety gate

**Estimated hands-on time:** 30 min. **Depends on:** T003.

**Purpose:** Poor power wiring can cause brownouts or component damage.

**Actions:**
1. Use a regulated 5 V USB supply rated for at least 2 A.
2. Use the main board USB-C for both power and data; leave the module USB-C unpowered during normal operation.
3. Never connect speaker SPK− to GND; choose the speaker connector OR solder pads, not both.
4. Never feed servo current from ESP32 3.3 V.

**Pass condition — what you must actually verify:** All four safety rules are understood and written into your bench notes.

**If it does not pass:** Pause construction until connector labels and power routing are clear.

**Safety:** POWER OFF for re-wiring. No mains or Li-ion rewiring required.

**Engineering concept:** Ohm’s law & power

**Equation / relationship:** `P = V × I`

**Example:** 5 V × 2 A = 10 W nominal power capability, not guaranteed continuous robot draw.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/power.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T005 · Prepare tools and a small parts inventory

**Estimated hands-on time:** 30 min. **Depends on:** T004.

**Purpose:** Tool and fastener readiness reduces interruption mid-assembly.

**Actions:**
1. Get a small Phillips screwdriver, a suitable USB-C data cable, a metric caliper if available, print tools, and a labeling pen.
2. Confirm whether the chosen ESP32 has two soldered 1×9 male headers; plan a soldering iron if not.
3. Organize M2×4, M2×8, M2×16 screws and M2 nuts by size.

**Pass condition — what you must actually verify:** Tools identified, headers accounted for, and fasteners separated.

**If it does not pass:** Do not force substitute screws; test-fit lengths first.

**Engineering concept:** Fastener dimensions

**Equation / relationship:** `M2×8 means 2 mm nominal thread diameter, 8 mm length`

**Example:** A too-long screw can bottom out or stress the print.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/shopping.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T006 · Create a test and evidence plan

**Estimated hands-on time:** 25 min. **Depends on:** T005.

**Purpose:** Engineering confidence comes from repeatable observations, not a checkbox alone.

**Actions:**
1. Set up a place to record observations, photos, actual measurements, and failures.
2. Decide what evidence counts for every exit test: a screenshot, short video, console response, or a written observation.
3. Mark every task as Not Started; do not mark physical tests complete before they are actually performed.

**Pass condition — what you must actually verify:** You can distinguish “guide reviewed”, “software-tested”, and “physically verified”.

**If it does not pass:** For an untestable step, record Blocked plus the precise missing dependency.

**Engineering concept:** Verification versus validation

**Equation / relationship:** `Verification: built as specified; validation: meets the intended need`

**Example:** A flashed ESP32 is verified; a robot performing a desired agent animation validates a use case.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/getting-started.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

## M02 · Parts & printing

Acquire parts, validate fit, and prepare all printed objects.

### T007 · Purchase electronics and exact screw quantities

**Estimated hands-on time:** 40 min. **Depends on:** T006.

**Purpose:** A consistent bill of materials prevents last-minute component substitutions.

**Actions:**
1. Use the project shopping page and buy: main PCB, ESP32-C3-Zero, five SG90, 128×32 SSD1306 OLED, 8 Ω/1 W speaker, and 5 V/≥2 A supply.
2. Obtain M2 screws (source nominal counts: eight ×4, twenty-seven ×8, fifteen ×16) and six M2 nuts; get ≥10 short male–female jumpers.
3. Record costs as estimates until receipts arrive; log actual purchases.

**Pass condition — what you must actually verify:** Inventory includes the exact five servos and power supply specification.

**If it does not pass:** Missing items stay Not Started or Blocked; order the missing item rather than redesigning the robot.

**Engineering concept:** Bill of materials (BOM)

**Equation / relationship:** `extended cost = quantity × unit price`

**Example:** 5 servos × $3 estimate = $15 before shipping.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/shopping.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T008 · Test servo pocket fit before full printing

**Estimated hands-on time:** 45 min. **Depends on:** T007.

**Purpose:** FDM printers and servo clones differ by tolerances; fitting one sample prevents repeating a bad full print.

**Actions:**
1. Download ServoSizingTester.3mf from the SG90 folder.
2. Print this tester using the same filament and slicer settings planned for the structural prints.
3. Insert a real SG90 with gentle pressure; check body fit, tab alignment, screw-hole positions, and shaft clearance.

**Pass condition — what you must actually verify:** The SG90 seats without force or excessive looseness; record a photo.

**If it does not pass:** If it jams, adjust print calibration or CAD servo parameters and repeat this tester only.

**Materials:** 3D printer + PLA/PETG + SG90 tester + caliper

**Engineering concept:** Dimensional error

**Equation / relationship:** `error = measured dimension − nominal dimension`

**Example:** A 0.3 mm oversize on two mating features can create an unexpectedly loose joint.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/3d_models/README.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T009 · Test M2 pilot holes

**Estimated hands-on time:** 45 min. **Depends on:** T008.

**Purpose:** M2 threads cut into the plastic directly; the wrong pilot hole can split the plastic or strip.

**Actions:**
1. Print ScrewSizingTest.3mf from the same SG90 set.
2. Hand-drive M2 screws into its labeled pilot holes.
3. Identify the tightest hole that accepts the screw without cracking or spinning; record its printed diameter.
4. If different from default, update the Fusion screw_thread_diameter parameter and re-export before the structural parts.

**Pass condition — what you must actually verify:** A physical screw test demonstrates one usable pilot diameter.

**If it does not pass:** If all holes crack or strip, tune the printer and reprint only the test piece.

**Engineering concept:** Screw engagement

**Equation / relationship:** `interference = screw nominal Ø − pilot Ø`

**Example:** This is a qualitative guide; plastic flow and print settings determine actual grip.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/3d_models/README.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T010 · Print the complete matching SG90 parts set

**Estimated hands-on time:** 240 min. **Depends on:** T009.

**Purpose:** All mechanical interfaces rely on matching exported geometry.

**Actions:**
1. Use the official Print page or parts/sg90/3mf files; prefer individual ready-oriented print files for home printing.
2. Print Head, Hat, Neck, Chest, Belly, BellyJoint, Chair, SeatLeft, SeatRight, Desk, DeskTop, DeskPad, BottomCover, ForearmLeft, ForearmRight, two UpperArm pieces, LaptopCase, LaptopScreen, Mug, Coffee, Bell, AiEmblem, LampBase, LampButton, LampDiffuser, LampCap, and all other pieces named by the official SG90 print folder. Confirm file names in the current upstream parts list, not only this summary.
3. Print LampDiffuser in translucent or white PLA/PETG; inspect slicer preview for its intentional thin wall (Arachne / thin-walls where needed).
4. Do not mix files from different servo folders or untracked revisions.

**Pass condition — what you must actually verify:** All required pieces are present, clean, correctly oriented, and labeled.

**If it does not pass:** Reprint only the failed part and check thin walls before printing LampDiffuser.

**Engineering concept:** FDM layer adhesion

**Equation / relationship:** `strength varies with layer direction and load direction`

**Example:** A protruding snap detail may break more easily across layers.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/3d_models/README.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T011 · Dry-fit and inspect the mechanical kit

**Estimated hands-on time:** 50 min. **Depends on:** T010.

**Purpose:** Dry-fitting catches geometry and print-version mismatches while reprinting is cheap.

**Actions:**
1. Count the printed parts against the source inventory.
2. Clean supports/stringing without over-cutting bearing/servo pockets.
3. Dry-fit the desk, Head/Hat, and Chair joints without force; confirm BottomCover and the revised Chair both have matching six attachment points.

**Pass condition — what you must actually verify:** No cracked, missing, warped, or incompatible structural parts remain.

**If it does not pass:** If BottomCover does not mate to Chair, obtain both pieces from the same current SG90 version.

**Engineering concept:** Design for assembly

**Equation / relationship:** `fit is an interface requirement, not an aesthetic preference`

**Example:** Two individually good prints can still fail to assemble when exported from different revisions.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

## M03 · Board & electrical checks

Order, inspect, and connect the electrical assembly safely.

### T012 · Obtain the main board fabrication package

**Estimated hands-on time:** 35 min. **Depends on:** T011.

**Purpose:** The fabrication layers, part list, and pick-and-place positions must describe the same PCB revision.

**Actions:**
1. Open the project Shop fab lane and download gerbers.zip, bom.csv, and positions.csv from the same deployment.
2. Keep these files together and do not mix them with files exported on a different board revision.
3. Use the original author’s order-main-control-board guide.

**Pass condition — what you must actually verify:** All three named manufacturing files are present and matched.

**If it does not pass:** If any file is missing, stop the order and re-download the complete set.

**Engineering concept:** PCB fabrication data

**Equation / relationship:** `Gerbers = geometry; BOM = components; CPL = placement`

**Example:** A correct board outline cannot compensate for a wrong pick-and-place orientation.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/order-main-control-board.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T013 · Order assembled PCB and review placement

**Estimated hands-on time:** 70 min. **Depends on:** T012.

**Purpose:** PCBA assembly saves difficult surface-mount soldering and makes costs explicit.

**Actions:**
1. For a beginner choose both-side PCBA if affordable, which includes the ESP32 female sockets; alternatively use top-side economic and solder those headers afterward.
2. Upload matching gerbers.zip, bom.csv and positions.csv to a board manufacturer.
3. Inspect orientation, part stock, board outline, quantity, assembly sides, and price before checkout.
4. Record the actual quote and order ID privately in the expense log, not in a public screenshot.

**Pass condition — what you must actually verify:** Confirmed order has the chosen assembly option and no unresolved part/rotation warnings.

**If it does not pass:** Do not checkout while any BOM or placement warning is unresolved.

**Engineering concept:** Manufacturing yield

**Equation / relationship:** `usable-unit cost = total order / verified functioning boards`

**Example:** A five-board fab minimum does not mean five assembled boards.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/order-main-control-board.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T014 · Receive and inspect PCB without applying power

**Estimated hands-on time:** 35 min. **Depends on:** T013.

**Purpose:** Visual inspection catches many issues before a powered fault can damage components.

**Actions:**
1. Inspect both faces under good light for missing, displaced, or solder-bridged parts.
2. Check two ESP32 1×9 female sockets are populated on a both-sides PCBA order, or solder them on a one-side board.
3. Check USB-C connector integrity and identifying labels; photograph both sides.

**Pass condition — what you must actually verify:** Board appears correctly populated; any uncertain orientation has been reviewed against the official board diagram.

**If it does not pass:** Quarantine questionable boards and contact the fabricator instead of powering them.

**Safety:** Power remains disconnected throughout the inspection.

**Engineering concept:** Quality control

**Equation / relationship:** `inspection is not equivalent to an electrical continuity test`

**Example:** No visible bridge is encouraging but not a guarantee of correct nets.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/order-main-control-board.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T015 · Bench-connect the main board

**Estimated hands-on time:** 55 min. **Depends on:** T014.

**Purpose:** Correct polarity and orientation matter more than matching wire colors.

**Actions:**
1. With USB power disconnected, identify the PCB USB-side orientation mark and ESP32 socket directions.
2. Seat the ESP32 in the correct orientation; attach speaker by the provided connector OR its solder pads.
3. Inspect the labeled OLED header’s 3.3 V, GND, SDA, SCL order; keep the Head/OLED cable free for its final routing (temporary bench connection is optional, disconnect it again before assembly).
4. Check servo plugs match signal, 5 V, and GND labels; connect one servo only as needed for the later centering test.

**Pass condition — what you must actually verify:** Photograph labeling and verify no reversed connectors, shorts, or dual speaker wiring.

**If it does not pass:** Disconnect power, then compare each connector with the board’s actual silkscreen and official pinout.

**Safety:** SPK− IS NOT GND. Never feed servo 5 V through an ESP32 3.3 V pin.

**Engineering concept:** Electrical ground & reference

**Equation / relationship:** `signal voltage is measured relative to the circuit ground`

**Example:** Servo PWM is a signal; it cannot replace the separately supplied 5 V motor rail.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/main-control-board.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

## M04 · Firmware & bench centering

Install stock firmware and establish the 90° mechanical reference.

### T016 · Prepare host and USB flashing cable

**Estimated hands-on time:** 30 min. **Depends on:** T015.

**Purpose:** The repository’s stock web flasher uses Web Serial; a charge-only cable cannot transmit data.

**Actions:**
1. Use Chrome or Edge on a computer with a USB-C data cable.
2. Keep the main control board with ESP32 on the workbench, not yet inside the desk.
3. Connect USB power/data to the main BOARD USB-C, not to the ESP32 module connector.

**Pass condition — what you must actually verify:** The browser detects the proper serial device when Connect is pressed.

**If it does not pass:** Try a known data cable/port and check serial permissions on Linux rather than altering hardware wiring.

**Engineering concept:** USB power versus data

**Equation / relationship:** `USB-C shape ≠ assurance of data wiring`

**Example:** A cable can charge a phone while missing the conductors needed for flashing.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/flash.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T017 · Flash stock Tiny Engineer firmware

**Estimated hands-on time:** 55 min. **Depends on:** T016.

**Purpose:** A known firmware baseline reduces variables before customization.

**Actions:**
1. Open https://jamro.github.io/tiny-engineer/flash/ in Chrome/Edge.
2. Select the latest compatible stock release and use Connect & install.
3. Do not interrupt until flash completes; follow the official recovery procedure if needed.
4. Observe the setup access point (TinyEngineer-XXXX) or serial boot output; the stock release includes audio content.

**Pass condition — what you must actually verify:** Flashing completes and the powered board offers the documented setup/assembly support route.

**If it does not pass:** If no setup AP appears, check board USB-C power, module seating, boot status LED, and flash documentation.

**Engineering concept:** Firmware stack

**Equation / relationship:** `host tool → bootloader → flash memory → application`

**Example:** An upload success proves transfer, not that the whole assembled robot works.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/flash.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T018 · Learn and execute safe 90° servo centering

**Estimated hands-on time:** 50 min. **Depends on:** T017.

**Purpose:** 90° is a repeatable electrical midpoint so parts can be mounted with known neutral geometry.

**Actions:**
1. Join the robot setup access point and visit http://192.168.4.1/config.
2. In Assembly support choose Move all to 90°; optionally Identify a joint.
3. For each mechanical connection, attach its servo for centering, then disconnect that servo lead before completing awkward joins.
4. Do NOT complete full guided range calibration or home Wi-Fi now; that happens after assembly.
5. Between bench-centering operations, unplug USB and temporary servo leads but KEEP the ESP32 seated in the bench PCB; §3–§7 still need it for further 90° centering. In §12 you will remove the ESP32 before placing the board into the Desk; it returns from ABOVE the Desk in §13.

**Pass condition — what you must actually verify:** A test servo moves to center and can be disconnected safely before mechanical loading.

**If it does not pass:** If a servo twitches or resets the board, stop and check the power supply and plug orientation.

**Safety:** Keep fingers and loose cables out of moving servo shafts.

**Engineering concept:** PWM servo position

**Equation / relationship:** `angle ≈ normalized pulse width mapped to a calibrated range`

**Example:** 90° is the midpoint command, not a guarantee of the output-shaft mechanical center.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

## M05 · Mechanical assembly

Build the robot in the repository’s canonical physical order.

### T019 · Assembly §1 — Populate Head

**Estimated hands-on time:** 25 min. **Depends on:** T018.

**Purpose:** Once Head is closed the OLED connector becomes difficult to reach.

**Actions:**
1. Remove OLED protective film and plug its cable in BEFORE seating the display.
2. Put one SG90 (no horn yet) and the OLED into Head pockets.
3. Route OLED and servo cables to opposite sides and into the rear printed clips.

**Pass condition — what you must actually verify:** Both parts seat cleanly and both cables are free of pinch points.

**If it does not pass:** Reopen the Head and correct cable routing rather than pulling on a seated connector.

**Engineering concept:** Cable strain relief

**Equation / relationship:** `stress at connector ≠ stress along cable`

**Example:** Molded clips distribute handling loads away from tiny contact pins.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#1-head--oled-and-servo

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T020 · Assembly §2 — Close Hat

**Estimated hands-on time:** 20 min. **Depends on:** T019.

**Purpose:** A correctly seated Hat fixes the display and servo geometry.

**Actions:**
1. Align Hat on Head without forcing the display or cables.
2. Fasten with two M2×8 screws into printed plastic, hand snug only.

**Pass condition — what you must actually verify:** No cable is trapped; Hat is flush and the OLED window is unobstructed.

**If it does not pass:** If it bows, remove and check that the OLED cable is not trapped.

**Engineering concept:** Torque at fasteners

**Equation / relationship:** `τ = F × r`

**Example:** More screwdriver force is not better when the female thread is soft PLA.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#2-hat

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T021 · Assembly §2a — Reconfirm bench-centering procedure

**Estimated hands-on time:** 20 min. **Depends on:** T020.

**Purpose:** Assembly order and calibration order must not be accidentally reversed.

**Actions:**
1. Keep board and power on the workbench rather than in the Desk cavity.
2. If needed use Assembly support → Move all to 90° to center each servo before installing its shaft-mounted printed part.
3. After each centering operation, disconnect the appropriate servo lead.

**Pass condition — what you must actually verify:** You can repeat the centering process without completing the whole Wi-Fi wizard.

**If it does not pass:** If the setup hub looks different, follow its documented Assembly support path.

**Engineering concept:** Open-loop positioning

**Equation / relationship:** `servo target angle is not a measured external joint pose`

**Example:** The internal servo feedback helps position its shaft, but printed horn alignment still matters.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#2a-bench-window-centering

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T022 · Assembly §3 — Build Neck joint

**Estimated hands-on time:** 40 min. **Depends on:** T021.

**Purpose:** The keyed shaft orientation sets the head’s yaw reference and the captured nut enables fastening.

**Actions:**
1. Use a SECOND unused servo and center it to 90°.
2. Seat printed Neck directly on its shaft, perpendicular to servo body, bulge pointing toward cable/electronics end.
3. Secure using the included servo shaft screw.
4. Put one M2 nut in Neck’s larger-hole pocket on the ROBOT’S RIGHT; leave the smaller pocket empty.
5. Disconnect servo after centering.

**Pass condition — what you must actually verify:** Neck is perpendicular, nut is captured on correct side, and shaft screw is snug.

**If it does not pass:** Remove and re-seat Neck at 90° if the geometry is misaligned.

**Engineering concept:** Coordinate-frame convention

**Equation / relationship:** `right/left are the robot’s own sides`

**Example:** Facing the robot reverses apparent left and right to the builder.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#3-neck--center-a-servo-and-attach-neck

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T023 · Assembly §4 — Join Neck and Head

**Estimated hands-on time:** 45 min. **Depends on:** T022.

**Purpose:** Two-sided fastening resists misalignment while allowing intended shaft rotation.

**Actions:**
1. Center the Head servo now in Head.
2. Seat Neck on Head servo shaft, then push it into the Head side assembly so the captured nut aligns.
3. At 90° align Neck perpendicular to Head.
4. Fix robot-right side with M2×8 into captured nut and robot-left with servo-bag screw.
5. Disconnect the Head servo.

**Pass condition — what you must actually verify:** Head and Neck join with no pinched wires or resistance at neutral.

**If it does not pass:** Disassemble to correct trapped wiring or a nut that has fallen out.

**Engineering concept:** Kinematics

**Equation / relationship:** `one servo joint ideally adds one rotational degree of freedom`

**Example:** Head pitch and neck yaw are separate, controlled rotations.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#4-join-neck-and-head

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T024 · Assembly §5 — Mount Chest side servos

**Estimated hands-on time:** 35 min. **Depends on:** T023.

**Purpose:** The Chest secures the left/right hand actuators in predictable positions.

**Actions:**
1. Insert two untouched SG90 servos into the left and right side pockets of Chest; leave horns unattached.
2. Route leads down the FRONT vertical tunnels so plugs exit below Chest.
3. Use four M2×16 screws total (two per servo).

**Pass condition — what you must actually verify:** Both servos are held securely and cables exit the correct side.

**If it does not pass:** If a cable cannot exit below, remove that servo and route before fastening.

**Engineering concept:** Load path

**Equation / relationship:** `mount → printed frame → desk support`

**Example:** Servo force pushes on both the moving arm and the stationary case.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#5-chest--side-servos

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T025 · Assembly §6 — Seat Neck servo in Chest

**Estimated hands-on time:** 35 min. **Depends on:** T024.

**Purpose:** Center neck movement must be mechanically supported by the torso.

**Actions:**
1. Pass the center Neck servo lead down the central front tunnel BEFORE seating it.
2. Keep Head facing the same direction as Chest front tunnels.
3. Press the Neck servo into Chest center pocket and use two M2×8 screws if accessible (one back screw accepted by source).

**Pass condition — what you must actually verify:** Neck servo does not shift in its pocket; its lead exits below.

**If it does not pass:** Unseat the servo and reroute its cable; never pinch the lead to save time.

**Engineering concept:** Constraints

**Equation / relationship:** `a servo case must be restrained for output torque to move the robot`

**Example:** A loose case rotates instead of transmitting the intended motion.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#6-mount-head-assembly-on-chest

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T026 · Assembly §7 — Install BellyJoint onto last servo

**Estimated hands-on time:** 30 min. **Depends on:** T025.

**Purpose:** The hex coupler transmits torso motion and its angular alignment determines neutral posture.

**Actions:**
1. Center the FIFTH unused servo to 90°.
2. Align BellyJoint hex with one flat parallel to the SHORT side of the servo body.
3. Press onto the shaft without a separate servo horn, secure with servo-bag screw, and unplug lead.

**Pass condition — what you must actually verify:** Hex is correctly aligned and fixed; no servo is left unaccounted for.

**If it does not pass:** If the shaft points the hex incorrectly, remove coupler and center again.

**Engineering concept:** Rotational coupling

**Equation / relationship:** `output angle = servo shaft angle + mechanical mounting offset`

**Example:** Calibration can compensate small error but not a completely wrong assembly.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#7-belly--last-servo

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T027 · Assembly §8 — Route Chest leads and attach Belly

**Estimated hands-on time:** 35 min. **Depends on:** T026.

**Purpose:** Correct cable order simplifies later identification; the channels have a separate numeric sequence.

**Actions:**
1. Pass left-hand, Neck, right-hand servo leads through Belly’s top opening and out lower side opening.
2. Maintain their left→center→right order as a labeling aid only.
3. Face Belly rounded side backward and join Belly to Chest with four M2×8 screws.

**Pass condition — what you must actually verify:** Four fasteners are snug and cables slide without compression.

**If it does not pass:** Remove Belly before correcting crossed/pinched leads; do not tug connectors.

**Engineering concept:** Signal identification

**Equation / relationship:** `physical cable order ≠ electrical channel map`

**Example:** Left hand is servo channel 2, not automatically the first cable you see.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#8-route-chest-cables-through-belly-and-join

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T028 · Assembly §9 — Seat body in Chair

**Estimated hands-on time:** 50 min. **Depends on:** T027.

**Purpose:** This fixes torso position while preserving a motor-driven body rotation.

**Actions:**
1. Insert the servo with BellyJoint into the Chair bottom pocket, routing its lead forward along the underside center channel.
2. Partially slide SeatLeft and SeatRight onto Chair dovetails, leaving a gap.
3. Lower Belly over the hex coupler; then close the seats without crushing wires.
4. Optionally use two M2×16 screws.

**Pass condition — what you must actually verify:** The body stands supported and the BellyJoint is captured without strain.

**If it does not pass:** If the seats resist sliding, inspect coupler engagement and cable path instead of forcing.

**Engineering concept:** Dovetail connection

**Equation / relationship:** `sliding rails constrain motion sideways`

**Example:** Mechanical interlocks can retain parts before or without extra fasteners.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#9-seat-the-body-in-chair

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T029 · Assembly §10 — Join DeskTop and DeskPad

**Estimated hands-on time:** 25 min. **Depends on:** T028.

**Purpose:** Correct orientation gives the body clearance toward the desk.

**Actions:**
1. Nest DeskTop in DeskPad.
2. Place both onto Desk with rounded cutout toward seated robot.
3. Secure four corners with M2×16 screws.

**Pass condition — what you must actually verify:** Four corners seat flush without rocking or warping.

**If it does not pass:** Recheck the rounded cutout orientation before tightening screws.

**Engineering concept:** Stacking tolerances

**Equation / relationship:** `total stack height = sum of mating layer thicknesses`

**Example:** Mis-seated layers can cause screws to bottom out before the joint closes.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#10-desk-top-stack

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T030 · Assembly §11 — Attach front emblem

**Estimated hands-on time:** 15 min. **Depends on:** T029.

**Purpose:** Decor is mounted before electronics complicate access.

**Actions:**
1. Place AiEmblem on Desk front.
2. Attach with two M2×4 screws, hand snug.

**Pass condition — what you must actually verify:** Emblem is stable and no short screw enters the board cavity.

**If it does not pass:** If holes are stripped, stop and assess the print; do not overtighten.

**Engineering concept:** Assembly accessibility

**Equation / relationship:** `fasten inaccessible parts before closing an enclosure`

**Example:** Assembly sequencing reduces needless disassembly.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#11-desk-emblem

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T031 · Assembly §12 — Seat PCB in Desk

**Estimated hands-on time:** 35 min. **Depends on:** T030.

**Purpose:** The board is enclosed only after it has been bench-flashed, limiting rework.

**Actions:**
1. Disconnect USB power and temporary servo/OLED leads. Gently pull the ESP32 straight out of the board sockets only NOW (after completing §3–§7 bench centering); put the ESP32 somewhere safe for §13.
2. Place the pre-tested main PCB without ESP32 in the Desk cavity; keep servo leads and OLED unplugged from the PCB until Assembly §15.
3. Place speaker inside cavity and use exactly one wiring method, connector OR pads.
4. Keep ESP32 module outside until it is inserted from above in step 13.

**Pass condition — what you must actually verify:** Board sits fully without bent wires, exposed shorts, or speaker pinch.

**If it does not pass:** If board does not seat, check part revision and header alignment; do not bend PCB.

**Safety:** Power OFF. SPK− must never be connected to GND.

**Engineering concept:** Enclosure design

**Equation / relationship:** `clearance maintains electrical and mechanical isolation`

**Example:** A compressed wire can create an intermittent failure only when a cover is tightened.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#12-electronics-inside-the-desk

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T032 · Assembly §13 — Seat ESP32 and LampBase

**Estimated hands-on time:** 55 min. **Depends on:** T031.

**Purpose:** Seating the ESP32 last avoids interference between its pins and the desk opening.

**Actions:**
1. If needed, solder two 1×9 male pin rows straight onto the ESP32-C3-Zero; the -M variant has headers fitted.
2. From ABOVE the desk insert ESP32 long pins through cutout into the board sockets, using PCB USB mark to orient.
3. Optional smoke test: power on board USB-C, verify status LED and setup AP, power off.
4. Place LampButton under LampBase to reach reset button; fasten LampBase with two M2×8 screws.

**Pass condition — what you must actually verify:** ESP32 is correctly oriented, flush and reachable via LampButton; no pin bends.

**If it does not pass:** Power off, remove and correct seating; never rotate a partially inserted module.

**Engineering concept:** Electrical connector pitch

**Equation / relationship:** `2.54 mm header pitch is distance between adjacent pins`

**Example:** Misaligning one pin by a full pitch can short power and signal nets.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#13-esp32-powerap-smoke-test-and-lampbase

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T033 · Assembly §14 — Laptop, mug, and bell

**Estimated hands-on time:** 35 min. **Depends on:** T032.

**Purpose:** Props are installed while underside access remains available.

**Actions:**
1. Slide LaptopScreen into LaptopCase, seat laptop and attach with one M2×8 from underside.
2. Nest Coffee inside Mug; attach mug with one M2×8 from underside.
3. Drive an M2×16 into Bell itself first; mount Bell on desk and capture with an M2 nut underneath.

**Pass condition — what you must actually verify:** All three props are secure and are clear of wiring.

**If it does not pass:** If Bell will not seat, pre-thread it before final mounting as source describes.

**Engineering concept:** Mechanical access

**Equation / relationship:** `an assembly operation requires tool approach clearance`

**Example:** Tightening from below later may be blocked by the enclosed electronics.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#14-desk-props--laptop-mug-bell

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T034 · Assembly §15 — Connect all five joints and OLED

**Estimated hands-on time:** 55 min. **Depends on:** T033.

**Purpose:** Explicit channel mapping prevents wrong motions and potential collisions.

**Actions:**
1. Tip desk carefully forward to expose headers; keep body supported beside it.
2. Connect head pitch to PCA9685 CH0, neck yaw CH1, left hand CH2, right hand CH3, torso CH4.
3. Connect OLED to correct 3.3 V/GND/SDA/SCL header; extend leads with short M–F jumpers preserving each net end-to-end.
4. Power on for servo + OLED smoke test, then power down before altering plugs.

**Pass condition — what you must actually verify:** All servos and OLED respond without unexpected reset; each channel has a written label.

**If it does not pass:** Disconnect power and trace individual cables before moving a connector.

**Safety:** Switch OFF before swapping any plugs.

**Engineering concept:** PWM controller channels

**Equation / relationship:** `PCA9685 channel index ≠ ESP32 GPIO number`

**Example:** CH0 drives head pitch; GPIO0 carries I²C SDA, not the head’s PWM.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#15-connect-servos-and-oled

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T035 · Assembly §16 — Attach Chair to Desk

**Estimated hands-on time:** 40 min. **Depends on:** T034.

**Purpose:** The desk supports the chair and makes one stable robot body.

**Actions:**
1. Bring Desk up to Chair without pulling routed cables.
2. Align matching mounting holes and use six M2×8 screws, three on each side.
3. Keep cables away from both screw tips and mating edges.

**Pass condition — what you must actually verify:** Chair/Desk are flush and rigid with no lead visible in a pinch zone.

**If it does not pass:** Remove fasteners and reposition wires; never clamp over a lead.

**Engineering concept:** Structural load transfer

**Equation / relationship:** `load distributes through multiple screw locations`

**Example:** Six screw points improve rigidity compared with a single attachment.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#16-fasten-chair-to-desk

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T036 · Assembly §16b — Close BottomCover

**Estimated hands-on time:** 45 min. **Depends on:** T035.

**Purpose:** Flat base prevents rocking and avoids severed cables.

**Actions:**
1. Power down and flip robot over while supporting it safely.
2. Route leads inside cavities, never through cover screw paths.
3. Verify Chair is current revision with two reinforced rear blind pilot holes.
4. Fit BottomCover mating face in, screw pockets outward; install six M2×8 screws (4 desk, 2 chair) with heads ≤4 mm wide and ≤2 mm high.

**Pass condition — what you must actually verify:** No pinched cables and all six screw heads are recessed; base rests flat.

**If it does not pass:** If rear holes do not exist, replace Chair with matching revision BEFORE closure.

**Engineering concept:** Center of mass & support

**Equation / relationship:** `stability requires projected center of mass within support footprint`

**Example:** A wobbling base makes repeatable servo motion harder to test.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#close-the-underside-with-bottomcover

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T037 · Assembly §17 — Build elbow joints

**Estimated hands-on time:** 35 min. **Depends on:** T036.

**Purpose:** Off-body elbow work makes fastening easier and protects servo gears.

**Actions:**
1. Use two UpperArm prints (left/right sides) and the corresponding ForearmLeft/ForearmRight.
2. Join each forearm to its upper arm with one M2×8 at its elbow.
3. Do not mount assemblies on Chest servos yet.

**Pass condition — what you must actually verify:** Two matching forearm/upper-arm assemblies articulate as intended.

**If it does not pass:** If a joint binds, undo the screw and clean the print rather than forcing.

**Engineering concept:** Joint friction

**Equation / relationship:** `friction torque opposes desired rotation`

**Example:** Overtight screws can turn a freely rotating joint into a locked joint.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#17-arms--elbow-joints

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T038 · Assembly §18 — Attach centered arms

**Estimated hands-on time:** 45 min. **Depends on:** T037.

**Purpose:** Attaching arms at a known neutral avoids collisions in the first commanded move.

**Actions:**
1. Recenter left/right hand servos via Assembly support BEFORE mounting arms.
2. Press each arm shaft pocket onto matching servo shaft.
3. At 90°, orient each hand near shoulder height with the forearm facing the desk.
4. Fasten each with its servo-bag screw, then repeat on the other side.

**Pass condition — what you must actually verify:** Both arms align similarly, and neither hits Chest or desk at neutral.

**If it does not pass:** Unfasten and change shaft spline indexing rather than commanding extreme angles.

**Engineering concept:** Angular offsets

**Equation / relationship:** `θ_world = θ_servo + θ_mounting_offset`

**Example:** A 20° mechanical offset changes the physical arm pose at a 90° servo command.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#18-mount-arms-on-the-chest-servos

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T039 · Assembly §19 — Finish lamp press-fit

**Estimated hands-on time:** 20 min. **Depends on:** T038.

**Purpose:** The lamp completes the enclosure while leaving reset access.

**Actions:**
1. Press LampCap onto LampDiffuser.
2. Push both into LampBase by hand, without screws or glue.
3. Check diffuser wall survived printing and lamp does not obstruct button.

**Pass condition — what you must actually verify:** Diffuser stays seated, is uncracked, and reset button remains operable.

**If it does not pass:** If diffuser splits, verify Arachne/thin-wall slicing and reprint just it.

**Engineering concept:** Interference fit

**Equation / relationship:** `retention arises from a small elastic deformation`

**Example:** Thin printed walls tolerate less assembly force than thick solids.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#19-lamp-press-fit

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

## M06 · Calibration & networking

Configure the assembled robot and connect to 2.4 GHz Wi-Fi.

### T040 · Complete assembled-servo calibration wizard

**Estimated hands-on time:** 70 min. **Depends on:** T039.

**Purpose:** Calibration maps firmware commands to actual assembled joint travel limits.

**Actions:**
1. Power the complete robot through board USB-C and join TinyEngineer-XXXX if in setup mode.
2. Open http://192.168.4.1/config, start the full wizard, and use Calibrate servos (Body → Neck → Head → Hands).
3. Move joints conservatively, watching for mechanical stops or collisions.
4. Confirm OLED orientation, RGB color mapping, and welcome audio; the Assembly support hub is not a substitute for range calibration.

**Pass condition — what you must actually verify:** All five joints complete guided calibration without binding or violent movement.

**If it does not pass:** If a joint collides, stop; correct shaft seating or limits while following wizard, do not overpower the mechanism.

**Safety:** Hands clear of moving parts; disconnect on repeated hard stops.

**Engineering concept:** Limits and saturation

**Equation / relationship:** `θ_safe ∈ [θ_min, θ_max]`

**Example:** A calibrated range must fit the actual geometry, not only servo nominal 0–180°.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#20-setup-wizard-and-first-boot-on-wi-fi

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T041 · Finish 2.4 GHz network setup

**Estimated hands-on time:** 50 min. **Depends on:** T040.

**Purpose:** Wi-Fi lets the agent send event commands to the robot REST service.

**Actions:**
1. In the wizard choose 2.4 GHz home Wi-Fi for this specific HTTP-based guide. The official USB-only branch exists but needs different serial-based verification steps and is not part of this fixed sequence.
2. Finish wizard and power-cycle robot once.
3. Read its IP from OLED; try http://tiny-engineer.local/ in browser, or the IP if mDNS fails.
4. Record only nonsecret connection information; never store Wi-Fi credentials in dashboard notes.

**Pass condition — what you must actually verify:** Robot joins the chosen 2.4 GHz network after power cycle and local web UI loads; record its IP.

**If it does not pass:** If OLED shows setup AP again, re-enter Wi-Fi wizard and verify 2.4 GHz credentials. Mark this task Blocked rather than proceeding without a network; do not substitute the USB-only path without a separate verification plan.

**Engineering concept:** Local networking

**Equation / relationship:** `hostname → local IP → HTTP endpoint`

**Example:** mDNS resolves tiny-engineer.local to an address; direct IP bypasses mDNS problems.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#20-setup-wizard-and-first-boot-on-wi-fi

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

## M07 · System verification

Prove each important function and record results.

### T042 · Prove HTTP health endpoint

**Estimated hands-on time:** 25 min. **Depends on:** T041.

**Purpose:** This tests Wi-Fi, network addressing, HTTP server, and firmware together.

**Actions:**
1. On a computer on the same network run: curl http://tiny-engineer.local/health.
2. If .local fails, use OLED IP address instead, optionally curl -4.
3. Save the response or a screenshot as evidence.

**Pass condition — what you must actually verify:** GET /health succeeds against the real robot and is logged.

**If it does not pass:** Check connection and OLED IP before reflashing; mDNS failure is not necessarily firmware failure.

**Engineering concept:** Client-server communication

**Equation / relationship:** `HTTP request → route → response`

**Example:** A valid health response proves the web server responds, not the servo or speaker.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/getting-started.md#7-prove-it

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T043 · Run safe motion, OLED, LED and sound tests

**Estimated hands-on time:** 75 min. **Depends on:** T042.

**Purpose:** Independent subsystem tests isolate faults before full automation.

**Actions:**
1. With hands clear and no obstruction, test the documented firmware endpoints one at a time: POST /test/screen, POST /test/led, POST /test/audio, POST /test/movement.
2. Observe each result, especially brownouts or jitter when multiple servos move.
3. Send POST /anim?name=ring and check expected movement; sound requires audio files on flash.
4. Log actual pass/fail for every subsystem separately.

**Pass condition — what you must actually verify:** OLED, RGB, audio, servo movement, and ring command each have observed outcomes.

**If it does not pass:** For sound failure, inspect firmware LittleFS/audio installation; for resets, check power and mechanical loads.

**Safety:** The movement test actuates all five servos; keep the desk clear.

**Engineering concept:** Integration testing

**Equation / relationship:** `system reliability depends on individual subsystems and interfaces`

**Example:** /health can pass even when a speaker plug is disconnected.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/testing.md#http-tests

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T044 · Run an independent power and enclosure audit

**Estimated hands-on time:** 50 min. **Depends on:** T043.

**Purpose:** An assembled robot can fail under simultaneous load even if bench checks passed.

**Actions:**
1. Operate a sequence of normal motions with the robot fully assembled and powered by 5 V/≥2 A.
2. Watch for voltage-related restarts, OLED flicker, servo jitter, sound dropout, and heat or cable rubbing.
3. Inspect bottom cover, screw heads, chair stability, arm clearance, and visible strain.
4. Compare finished robot to the original repo photograph and 3D assembly viewer: seated figure behind desk, OLED in Head, joint structure, laptop, mug, bell, lamp, chair seats and front emblem; record any differences.
5. If a failure appears, isolate it before proceeding to agent integration.

**Pass condition — what you must actually verify:** No reproducible reset, wiring pinch, overheating, or structural instability in normal operation, and the physical layout matches the source model or any intended deviation is documented.

**If it does not pass:** Unplug on abnormal heat or smell. For repeatable resets review official power guide; do not simply demand a larger voltage.

**Safety:** Supply is 5 V, NOT 9 V or 12 V. Disconnect power on abnormal heating.

**Engineering concept:** Power budget & margin

**Equation / relationship:** `I_total(t) = I_logic + Σ I_servos(t) + I_audio(t)`

**Example:** Short servo start-up peaks can matter even when average current looks modest.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/power.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

## M08 · Agent integration & handoff

Connect a coding tool, back up evidence, and freeze a working baseline.

### T045 · Connect coding agent events

**Estimated hands-on time:** 75 min. **Depends on:** T044. **Optional extension.**

**Purpose:** The goal is to turn software events into recognizable physical behavior.

**Actions:**
1. Install Node.js 18+ on host if using the default setup tool.
2. Run npx -y tiny-engineer setup per official integration instructions (or select documented USB serial option).
3. Follow your tool-specific prompts for Cursor, Claude Code or Antigravity.
4. If using custom scripts, use the supported POST /anim route and do not send arbitrary unsafe motions.

**Pass condition — what you must actually verify:** One real coding-agent event causes the intended real-world robot animation.

**If it does not pass:** For silent hooks run npx -y tiny-engineer doctor and follow integration docs; cold npx hooks may require timeout ≥30 s.

**Engineering concept:** Event-driven systems

**Equation / relationship:** `event → handler → network request → actuator action`

**Example:** The robot reacts to an IDE event, rather than polling every file manually.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/integration.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

### T046 · Finalize documentation and baseline

**Estimated hands-on time:** 50 min. **Depends on:** T045. **Optional extension.**

**Purpose:** A reproducible baseline makes future experiments safe and comparable.

**Actions:**
1. Export a full working copy and step-by-step PDF from the dashboard.
2. Save a project version named Baseline V1; record tested endpoints, hardware variant, cost, firmware revision, and known limitations.
3. Use GitHub Backup only after configuring a personal repository and Git authentication; otherwise retain local JSON and ZIP backups.
4. Create a final target-conformance record that names every physical feature: seated figure/chair, SG90 shell geometry, five articulations, OLED face, laptop, mug, bell, lamp, desk board and bottom cover.
5. Write a short retrospective with successes, unsolved questions, and next modifications.

**Pass condition — what you must actually verify:** Version/export files exist; a final conformance checklist is signed off with physical observations or explicit unresolved differences, and the completion report distinguishes performed tests from pending tests.

**If it does not pass:** If export fails, retain the SQLite DB and use the app working-copy JSON endpoint before troubleshooting Git.

**Engineering concept:** Reproducibility

**Equation / relationship:** `baseline = hardware + firmware + settings + evidence`

**Example:** Recording only a picture of the finished robot is insufficient to recreate the result.

**Upstream reference:** https://github.com/jamro/tiny-engineer/blob/main/docs/getting-started.md

**My observed result:** ____________________   **Status:** Not started / Blocked / Passed

---

## Upstream references

- [Official target photograph](https://github.com/jamro/tiny-engineer/blob/main/docs/tiny-engineer-preview.jpg)
- [3D assembly viewer](https://tinyengineer.dev/assembly/)
- [Servo movements](https://github.com/jamro/tiny-engineer/blob/main/docs/robot-movement.md)
- [Build sequence](https://github.com/jamro/tiny-engineer/blob/main/docs/getting-started.md)
- [Shopping](https://github.com/jamro/tiny-engineer/blob/main/docs/shopping.md)
- [Printed models](https://github.com/jamro/tiny-engineer/blob/main/3d_models/README.md)
- [Assembly](https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md)
- [Board connection](https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/main-control-board.md)
- [PCB fabrication](https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/order-main-control-board.md)
- [Firmware flash](https://github.com/jamro/tiny-engineer/blob/main/docs/flash.md)
- [Pinout](https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/pinout.md)
- [Power](https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/power.md)
- [Testing](https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/testing.md)
- [Integrations](https://github.com/jamro/tiny-engineer/blob/main/docs/integration.md)

## Physical validation boundary

These procedures have not been certified against a real assembled unit in this workspace. Start with the actual supplier boards and printed parts, and do not infer that a software green check proves a physical connection or moving joint.
