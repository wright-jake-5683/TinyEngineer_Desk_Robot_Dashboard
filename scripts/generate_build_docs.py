#!/usr/bin/env python3
"""Regenerate the standalone guide from the app's single source of truth.
Physical hardware acceptance is explicitly outside the scope of this script.
"""
from pathlib import Path
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
from guide_data import STEPS, PHASES, BOM, SOURCE_INDEX
DOCS=ROOT/'docs'; DOCS.mkdir(exist_ok=True)

INTRO = '''# Tiny Engineer · Desk Robot — V2 Beginner Build Guide

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
'''
lines=[INTRO]
for x in BOM:
    name=x['name'].replace('|','/')
    lines.append(f"| {name} | {x['qty']} | ${x['unit']:.2f} | ${x['qty']*x['unit']:.2f} |\n")
total=sum(x['qty']*x['unit'] for x in BOM)
lines.extend([f"\n**Estimated component subtotal: ${total:.2f}, excluding shipping, taxes and tools.** Assembled PCB price is an **unverified planning allowance**, not a supplier quote.\n\n",'## Sequential build tasks\n\n'])
for phase, name, description in PHASES:
    lines.append(f'## {phase} · {name}\n\n{description}\n\n')
    for s in (p for p in STEPS if p['phase']==phase):
        lines.append(f"### {s['id']} · {s['title']}\n\n")
        lines.append(f"**Estimated hands-on time:** {s['minutes']} min. **Depends on:** {', '.join(s['depends']) or 'None'}.{' **Optional extension.**' if s['optional'] else ''}\n\n")
        lines.append(f"**Purpose:** {s['purpose']}\n\n")
        lines.append('**Actions:**\n')
        for i,a in enumerate(s['actions'],1): lines.append(f'{i}. {a.strip()}\n')
        lines.append(f"\n**Pass condition — what you must actually verify:** {s['exit_test']}\n\n")
        lines.append(f"**If it does not pass:** {s['if_failed']}\n\n")
        if s['safety']: lines.append(f"**Safety:** {s['safety']}\n\n")
        if s['materials']: lines.append(f"**Materials:** {s['materials']}\n\n")
        lines.append(f"**Engineering concept:** {s['concept']}\n\n")
        if s['formula']: lines.append(f"**Equation / relationship:** `{s['formula']}`\n\n")
        if s['example']: lines.append(f"**Example:** {s['example']}\n\n")
        lines.append(f"**Upstream reference:** {s['source']}\n\n")
        lines.append('**My observed result:** ____________________   **Status:** Not started / Blocked / Passed\n\n---\n\n')
lines.append('## Upstream references\n\n')
for name,url in SOURCE_INDEX: lines.append(f'- [{name}]({url})\n')
lines.append('\n## Physical validation boundary\n\nThese procedures have not been certified against a real assembled unit in this workspace. Start with the actual supplier boards and printed parts, and do not infer that a software green check proves a physical connection or moving joint.\n')
md=''.join(lines)
(DOCS/'BEGINNER_BUILD_GUIDE.md').write_text(md,encoding='utf-8')

# Reference target spec, so the dashboard and printable docs can be independently audited.
target='''# Tiny Engineer · Final physical design reference (V2)

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
'''
(DOCS/'TARGET_DESIGN_SPEC.md').write_text(target,encoding='utf-8')

# Printable PDF. The source content and task order come solely from guide_data.STEPS.
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DejaVu',font));pdfmetrics.registerFont(TTFont('DejaVuBold',bold))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold',italic='DejaVu',boldItalic='DejaVuBold')
dark=colors.HexColor('#161b1f'); gold=colors.HexColor('#BD832D'); muted=colors.HexColor('#556069')
styles={
'title':ParagraphStyle('title',fontName='DejaVuBold',fontSize=23,leading=32,spaceAfter=18,textColor=dark),
'section':ParagraphStyle('section',fontName='DejaVuBold',fontSize=15,leading=22,spaceBefore=18,spaceAfter=11,textColor=dark),
'step':ParagraphStyle('step',fontName='DejaVuBold',fontSize=12,leading=18,spaceBefore=12,spaceAfter=9,textColor=dark),
'body':ParagraphStyle('body',fontName='DejaVu',fontSize=8.8,leading=14.4,spaceAfter=8,textColor=dark),
'small':ParagraphStyle('small',fontName='DejaVu',fontSize=7.5,leading=11.5,spaceAfter=6,textColor=muted),
'num':ParagraphStyle('num',fontName='DejaVu',fontSize=8.8,leading=15,leftIndent=17,firstLineIndent=-17,spaceAfter=4,textColor=dark),
'flag':ParagraphStyle('flag',fontName='DejaVu',fontSize=8.6,leading=13.5,spaceBefore=10,spaceAfter=11,textColor=colors.HexColor('#7A3D1B'),leftIndent=10),
}
p=DOCS/'BEGINNER_BUILD_GUIDE.pdf'
doc=SimpleDocTemplate(str(p),pagesize=letter,leftMargin=52,rightMargin=52,topMargin=64,bottomMargin=52,title='Tiny Engineer Desk Robot | V2 Build Guide',author='Independent Tiny Engineer companion')
flow=[]
def pg(t,style='body'):
    return Paragraph(escape(str(t)).replace('\n','<br/>'),styles[style])
flow.append(pg('TINY ENGINEER','small'));flow.append(pg('Desk Robot · Beginner Build Guide','title'))
flow.append(pg('V2 · official seated desktop animatronic · fixed SG90 + integrated PCB baseline','small'))
flow.append(pg('Physical target','section'))
flow.append(pg('Build the seated humanoid in its chair behind a miniature desk with an OLED face, two arms, laptop, mug, bell, lamp, front emblem, bottom cover and five independent servo movements. Follow the creator’s CAD and assembly viewer, not a generic robot photograph.'))
flow.append(pg('The application was tested in software. No physical robot, fabricated board, servo or 3D-printed piece has been tested here; the pass conditions in this guide must be performed on your actual hardware.','flag'))
flow.append(pg('Project references','section'))
for name,url in SOURCE_INDEX[:4]: flow.append(Paragraph(f'<b>{escape(name)}</b>: <link href="{escape(url)}" color="#7A3D1B">{escape(url)}</link>',styles['small']))
flow.append(pg('How to work through each step','section'))
for i,s in enumerate(['Use one numbered task at a time, and perform the actual exit test before marking Done.','Keep exactly five SG90 servos, matching printed parts and an integrated main control PCB for this baseline.','Use regulated 5 V / at least 2 A power; never power servos from ESP32 3.3 V and never tie speaker SPK− to ground.','Center servos on the bench, then mount the electronics in the official assembly order. Power off before moving wires or modules.','The fixed verification sequence requires 2.4 GHz Wi-Fi, not the USB-only branch.','Log real measurements, photos, tests and failures, and recheck downstream work after changing an earlier step.'],1):
    flow.append(pg(f'{i}. {s}','num'))
flow.append(pg('Physical finish-line checklist','section'))
for item in ['Seated character, chair and two side seats','Desk, laptop, coffee mug, bell, lamp and emblem','OLED face and properly wired speaker','Head pitch CH0, neck yaw CH1, left arm CH2, right arm CH3 and torso CH4','5 V main-board USB-C and enclosed electronics','Actual observed movement, fit, safe wiring and power test evidence']:
    flow.append(pg('☐ '+item))
flow.append(Spacer(1, 6))
for pid,name,desc in PHASES:
    flow.append(pg(f'{pid} · {name}','section'));flow.append(pg(desc,'body'))
    for s in (x for x in STEPS if x['phase']==pid):
        # keep task heading + first two paragraphs on one page when possible
        flow.append(KeepTogether([pg(f"{s['id']} · {s['title']}",'step'),pg(f"Estimate {s['minutes']} min   •   Prerequisite: {', '.join(s['depends']) or 'None'}{'   •   Optional' if s['optional'] else ''}",'small'),pg('Purpose: '+s['purpose'])]))
        flow.append(pg('Actions','step'))
        for i,action in enumerate(s['actions'],1): flow.append(pg(f'{i}. {action.strip()}','num'))
        flow.append(pg('PASS CHECK: '+s['exit_test'],'flag'))
        flow.append(pg('IF BLOCKED: '+s['if_failed']))
        if s['safety']: flow.append(pg('SAFETY: '+s['safety'],'flag'))
        if s['materials']: flow.append(pg('Materials: '+s['materials']))
        flow.append(pg('ENGINEERING: '+s['concept']))
        if s['formula']: flow.append(pg('Relationship: '+s['formula']))
        if s['example']: flow.append(pg('Example: '+s['example']))
        flow.append(Paragraph('<b>Source:</b> <link href="'+escape(s['source'])+'" color="#7A3D1B">'+escape(s['source'])+'</link>',styles['small']))
        flow.append(pg('My observed result: _______________________    Date: ____________','small'))
        flow.append(HRFlowable(width='100%',thickness=0.5,color=colors.HexColor('#dadada'),spaceBefore=6,spaceAfter=6))
flow.append(pg('Final evidence boundary','section'));flow.append(pg('This document describes source-derived procedures; software tests and document review do not certify mechanical fit, electrical safety, firmware compatibility or actual servo loads. Retain original project docs and record differences in a versioned project decision.'))
def page(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#dce1e3')); canvas.line(52,49,560,49)
    canvas.setFont('DejaVu',7);canvas.setFillColor(muted)
    canvas.drawString(52,37,'TINY ENGINEER  /  DESK ROBOT  /  AUTUMN V2')
    canvas.drawRightString(560,37,f'{doc.page}')
    canvas.setStrokeColor(gold);canvas.setLineWidth(2);canvas.line(52,750,130,750)
doc.build(flow,onFirstPage=page,onLaterPages=page)
print('Written:',DOCS/'BEGINNER_BUILD_GUIDE.md', (DOCS/'BEGINNER_BUILD_GUIDE.md').stat().st_size, 'bytes')
print('Written:',p, p.stat().st_size,'bytes')
print('Written:',DOCS/'TARGET_DESIGN_SPEC.md')
