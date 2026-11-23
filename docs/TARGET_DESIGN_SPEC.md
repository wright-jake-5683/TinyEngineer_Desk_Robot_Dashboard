# Tiny Engineer · Final physical design reference (V2)

## Source of truth

- Project: https://github.com/jamro/tiny-engineer
- Creator photo: https://github.com/jamro/tiny-engineer/blob/8821a07969788f52c232cab2c377d797524d4334/docs/tiny-engineer-preview.jpg
- Original 3D assembly: https://tinyengineer.dev/assembly/
- CAD and print source: https://github.com/jamro/tiny-engineer/tree/main/3d_models
- Mechanical assembly order: https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md
- Movement channels: https://github.com/jamro/tiny-engineer/blob/main/docs/robot-movement.md

## Appearance and actual mechanical architecture

This is the creator’s miniature seated robot with a copper/red-toned character, a dark miniature desk and an OLED face. It is **not** a walking robot or a mobile base. The printed chair supports Head, Neck, Chest and Belly, with left and right arms and hands. Props on the desk include a laptop, coffee mug, small bell and lamp. The electronics sit in the Desk/DeskTop housing and the board’s external power and data connection is USB-C.

Select **all five SG90 servos with the matching SG90 geometry**. Print the repo’s dedicated servo sizing and M2 screw-hole testers before committing to the complete print. Do not substitute another servo model without choosing and testing matching CAD/3MF geometry.

### Exact source part inventory for SG90 baseline

- **Body:** Head, Hat, Neck, Chest, Belly, BellyJoint
- **Chair:** Chair, SeatLeft, SeatRight
- **Desk:** Desk, DeskTop, DeskPad, BottomCover, AiEmblem
- **Arms:** ForearmLeft, ForearmRight, UpperArm (two)
- **Props:** LaptopCase, LaptopScreen, Mug, Coffee, Bell
- **Lamp:** LampBase, LampButton, LampDiffuser, LampCap

The parts list above is the physical **inventory target**, not a guarantee that one default 3MF export contains multiple copies where quantity 2 is needed. Check the official 3D parts index and the slicer objects and quantities before printing.

### Motor function, not arbitrary GPIO

| Control channel | Physical joint |
|---|---|
| CH0 | Head pitch |
| CH1 | Neck yaw |
| CH2 | Left hand / arm |
| CH3 | Right hand / arm |
| CH4 | Body / torso rotation |

The five PCA9685 **channels** are servo signal channels; they are not ESP32-C3 GPIO pin numbers. Use the official main-board pinout and labeling for your physical board revision.

### Assembly alignment acceptance

1. Bench-connect and flash the board, then learn safe 90° centering with space around detached servos.
2. Follow assembly §§1–11, including bench centering at §2a and fitting head, chest and belly assemblies, chair and tabletop.
3. With power off, **remove ESP32 before mounting the PCB within the Desk at §12**, then **reinsert ESP32 at §13**. Leave power off during wiring changes.
4. Finish props, joint wiring and OLED, chair-to-desk coupling, BottomCover, arm joints and lamp. Check visible routing before closing cavities.
5. Calibrate every joint on the assembled robot, set up 2.4 GHz Wi-Fi, then run the health, screen, LED, sound and movement tests documented by the project.
6. Finish with a **photo / video plus physical checklist** matching the authoritative CAD/preview. An edited/generated illustration is not an acceptable mechanical fit proof.

### What is not verified by these documents

No real board, SG90s, 3D print, electrical wiring, speaker, LED, OLED, motion or firmware have been physically verified in the dashboard creation environment. Changes upstream and unit-to-unit tolerances may affect fit. The public creator’s image is linked rather than embedded, so internet access is needed to view it in the dashboard. The offline fallback identifies the required design without substituting misleading imagery.
