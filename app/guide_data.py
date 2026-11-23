"""Original, beginner-oriented companion guide based on jamro/tiny-engineer docs.
Source docs are authoritative for hardware details. This guide does not certify hardware.
"""
BASE='https://github.com/jamro/tiny-engineer/blob/main/'
PHASES=[
 ('M01','Understand & plan','Plan the build, choose the exact hardware variant, and establish safe expectations.'),
 ('M02','Parts & printing','Acquire parts, validate fit, and prepare all printed objects.'),
 ('M03','Board & electrical checks','Order, inspect, and connect the electrical assembly safely.'),
 ('M04','Firmware & bench centering','Install stock firmware and establish the 90° mechanical reference.'),
 ('M05','Mechanical assembly','Build the robot in the repository’s canonical physical order.'),
 ('M06','Calibration & networking','Configure the assembled robot and connect to 2.4 GHz Wi-Fi.'),
 ('M07','System verification','Prove each important function and record results.'),
 ('M08','Agent integration & handoff','Connect a coding tool, back up evidence, and freeze a working baseline.'),
]
STEPS=[]
def add(phase,title,do,why,check,fix,concept='Quality gates',math='',example='',source='docs/getting-started.md',minutes=25,materials='',safety='',optional=False):
    index=len(STEPS)+1; sid=f'T{index:03d}'
    STEPS.append(dict(id=sid,phase=phase,title=title,actions=do.split('|'),purpose=why,
      exit_test=check,if_failed=fix,concept=concept,formula=math,example=example,
      source=BASE+source,minutes=minutes,materials=materials,safety=safety,optional=optional,
      depends=[STEPS[-1]['id']] if STEPS else []))
# M01 — readiness
add('M01','Identify the robot and final outcome',
'Open the creator’s photo (docs/tiny-engineer-preview.jpg) and official 3D assembly viewer. The finished object must be a seated copper-colored humanoid behind a black miniature desk, with an OLED face and miniature laptop, mug, bell, and lamp.|Open the official assembly instructions and identify the printed Head, Hat, Neck, Chest, Belly, BellyJoint, Chair, two seats, Desk, DeskTop, DeskPad, BottomCover, arm parts, laptop, mug, bell and lamp on the source parts list.|Write the five independent joint motions: head pitch, neck yaw, left hand, right hand, torso rotation.|Confirm it is a USB-powered stationary desktop animatronic, not a walking or wheeled robot. Record the official image, CAD and assembly links in your notes.',
'Establish an unambiguous physical design target before buying, printing or wiring; every later assembly step must serve this seated desk robot.',
'Your written target checklist matches the creator’s photo and assembly map, with seated figure, desk props, OLED face and five named joints. Treat photos as reference only; physical geometry comes from SG90 CAD.',
'Return to the README before changing scope. Do not invent locomotion features.','Systems engineering','Requirement → measurable acceptance test','Requirement: “respond to agent event”; proof: trigger a supported animation.',minutes=20)
add('M01','Choose one servo model and geometry',
'Choose five Tower Pro SG90 micro servos for this first build.|Write SG90 in project settings.|Use only the matching parts/sg90 print folder; do not mix compact servo models.',
'The servo pocket dimensions determine the printed robot geometry.',
'Exactly five matching servos are chosen; printed files come from parts/sg90.',
'If stock differs, stop and reselect the entire servo + CAD preset together.',
'Tolerance & compatibility','clearance = printed pocket width − actual servo width','A negative clearance means a servo cannot be inserted without force.',source='docs/shopping.md',minutes=20)
add('M01','Select the electrical architecture',
'Choose the integrated main control board for this baseline.|Write that this board already contains the PCA9685 servo driver, MAX98357A amplifier, and USB-C interface.|Keep the modular breakout wiring as an alternative only if the integrated-board plan changes.',
'One architecture keeps the build guide unambiguous and avoids mixing incompatible instructions.',
'One electrical architecture is selected; breakout-only parts are not accidentally double-purchased.',
'If you choose breakout boards, stop and follow the repository wiring and modular assembly guides.',
'Architecture & interfaces','module → interface → load','ESP32 commands PCA9685 over I²C; PCA9685 makes servo control pulses.',source='docs/shopping.md',minutes=20)
add('M01','Read the electrical safety gate',
'Use a regulated 5 V USB supply rated for at least 2 A.|Use the main board USB-C for both power and data; leave the module USB-C unpowered during normal operation.|Never connect speaker SPK− to GND; choose the speaker connector OR solder pads, not both.|Never feed servo current from ESP32 3.3 V.',
'Poor power wiring can cause brownouts or component damage.',
'All four safety rules are understood and written into your bench notes.',
'Pause construction until connector labels and power routing are clear.',
'Ohm’s law & power','P = V × I','5 V × 2 A = 10 W nominal power capability, not guaranteed continuous robot draw.',source='docs/hardware/power.md',minutes=30,safety='POWER OFF for re-wiring. No mains or Li-ion rewiring required.')
add('M01','Prepare tools and a small parts inventory',
'Get a small Phillips screwdriver, a suitable USB-C data cable, a metric caliper if available, print tools, and a labeling pen.|Confirm whether the chosen ESP32 has two soldered 1×9 male headers; plan a soldering iron if not.|Organize M2×4, M2×8, M2×16 screws and M2 nuts by size.',
'Tool and fastener readiness reduces interruption mid-assembly.',
'Tools identified, headers accounted for, and fasteners separated.',
'Do not force substitute screws; test-fit lengths first.','Fastener dimensions','M2×8 means 2 mm nominal thread diameter, 8 mm length','A too-long screw can bottom out or stress the print.',source='docs/shopping.md',minutes=30)
add('M01','Create a test and evidence plan',
'Set up a place to record observations, photos, actual measurements, and failures.|Decide what evidence counts for every exit test: a screenshot, short video, console response, or a written observation.|Mark every task as Not Started; do not mark physical tests complete before they are actually performed.',
'Engineering confidence comes from repeatable observations, not a checkbox alone.',
'You can distinguish “guide reviewed”, “software-tested”, and “physically verified”.',
'For an untestable step, record Blocked plus the precise missing dependency.',
'Verification versus validation','Verification: built as specified; validation: meets the intended need','A flashed ESP32 is verified; a robot performing a desired agent animation validates a use case.',minutes=25)
# M02
add('M02','Purchase electronics and exact screw quantities',
'Use the project shopping page and buy: main PCB, ESP32-C3-Zero, five SG90, 128×32 SSD1306 OLED, 8 Ω/1 W speaker, and 5 V/≥2 A supply.|Obtain M2 screws (source nominal counts: eight ×4, twenty-seven ×8, fifteen ×16) and six M2 nuts; get ≥10 short male–female jumpers.|Record costs as estimates until receipts arrive; log actual purchases.',
'A consistent bill of materials prevents last-minute component substitutions.',
'Inventory includes the exact five servos and power supply specification.',
'Missing items stay Not Started or Blocked; order the missing item rather than redesigning the robot.',
'Bill of materials (BOM)','extended cost = quantity × unit price','5 servos × $3 estimate = $15 before shipping.',source='docs/shopping.md',minutes=40)
add('M02','Test servo pocket fit before full printing',
'Download ServoSizingTester.3mf from the SG90 folder.|Print this tester using the same filament and slicer settings planned for the structural prints.|Insert a real SG90 with gentle pressure; check body fit, tab alignment, screw-hole positions, and shaft clearance.',
'FDM printers and servo clones differ by tolerances; fitting one sample prevents repeating a bad full print.',
'The SG90 seats without force or excessive looseness; record a photo.',
'If it jams, adjust print calibration or CAD servo parameters and repeat this tester only.',
'Dimensional error','error = measured dimension − nominal dimension','A 0.3 mm oversize on two mating features can create an unexpectedly loose joint.',source='3d_models/README.md',minutes=45,materials='3D printer + PLA/PETG + SG90 tester + caliper')
add('M02','Test M2 pilot holes',
'Print ScrewSizingTest.3mf from the same SG90 set.|Hand-drive M2 screws into its labeled pilot holes.|Identify the tightest hole that accepts the screw without cracking or spinning; record its printed diameter.|If different from default, update the Fusion screw_thread_diameter parameter and re-export before the structural parts.',
'M2 threads cut into the plastic directly; the wrong pilot hole can split the plastic or strip.',
'A physical screw test demonstrates one usable pilot diameter.',
'If all holes crack or strip, tune the printer and reprint only the test piece.',
'Screw engagement','interference = screw nominal Ø − pilot Ø','This is a qualitative guide; plastic flow and print settings determine actual grip.',source='3d_models/README.md',minutes=45)
add('M02','Print the complete matching SG90 parts set',
'Use the official Print page or parts/sg90/3mf files; prefer individual ready-oriented print files for home printing.|Print Head, Hat, Neck, Chest, Belly, BellyJoint, Chair, SeatLeft, SeatRight, Desk, DeskTop, DeskPad, BottomCover, ForearmLeft, ForearmRight, two UpperArm pieces, LaptopCase, LaptopScreen, Mug, Coffee, Bell, AiEmblem, LampBase, LampButton, LampDiffuser, LampCap, and all other pieces named by the official SG90 print folder. Confirm file names in the current upstream parts list, not only this summary.|Print LampDiffuser in translucent or white PLA/PETG; inspect slicer preview for its intentional thin wall (Arachne / thin-walls where needed).|Do not mix files from different servo folders or untracked revisions.',
'All mechanical interfaces rely on matching exported geometry.',
'All required pieces are present, clean, correctly oriented, and labeled.',
'Reprint only the failed part and check thin walls before printing LampDiffuser.',
'FDM layer adhesion','strength varies with layer direction and load direction','A protruding snap detail may break more easily across layers.',source='3d_models/README.md',minutes=240)
add('M02','Dry-fit and inspect the mechanical kit',
'Count the printed parts against the source inventory.|Clean supports/stringing without over-cutting bearing/servo pockets.|Dry-fit the desk, Head/Hat, and Chair joints without force; confirm BottomCover and the revised Chair both have matching six attachment points.',
'Dry-fitting catches geometry and print-version mismatches while reprinting is cheap.',
'No cracked, missing, warped, or incompatible structural parts remain.',
'If BottomCover does not mate to Chair, obtain both pieces from the same current SG90 version.',
'Design for assembly','fit is an interface requirement, not an aesthetic preference','Two individually good prints can still fail to assemble when exported from different revisions.',source='docs/3d/assembly.md',minutes=50)
# M03
add('M03','Obtain the main board fabrication package',
'Open the project Shop fab lane and download gerbers.zip, bom.csv, and positions.csv from the same deployment.|Keep these files together and do not mix them with files exported on a different board revision.|Use the original author’s order-main-control-board guide.',
'The fabrication layers, part list, and pick-and-place positions must describe the same PCB revision.',
'All three named manufacturing files are present and matched.',
'If any file is missing, stop the order and re-download the complete set.',
'PCB fabrication data','Gerbers = geometry; BOM = components; CPL = placement','A correct board outline cannot compensate for a wrong pick-and-place orientation.',source='docs/hardware/order-main-control-board.md',minutes=35)
add('M03','Order assembled PCB and review placement',
'For a beginner choose both-side PCBA if affordable, which includes the ESP32 female sockets; alternatively use top-side economic and solder those headers afterward.|Upload matching gerbers.zip, bom.csv and positions.csv to a board manufacturer.|Inspect orientation, part stock, board outline, quantity, assembly sides, and price before checkout.|Record the actual quote and order ID privately in the expense log, not in a public screenshot.',
'PCBA assembly saves difficult surface-mount soldering and makes costs explicit.',
'Confirmed order has the chosen assembly option and no unresolved part/rotation warnings.',
'Do not checkout while any BOM or placement warning is unresolved.',
'Manufacturing yield','usable-unit cost = total order / verified functioning boards','A five-board fab minimum does not mean five assembled boards.',source='docs/hardware/order-main-control-board.md',minutes=70)
add('M03','Receive and inspect PCB without applying power',
'Inspect both faces under good light for missing, displaced, or solder-bridged parts.|Check two ESP32 1×9 female sockets are populated on a both-sides PCBA order, or solder them on a one-side board.|Check USB-C connector integrity and identifying labels; photograph both sides.',
'Visual inspection catches many issues before a powered fault can damage components.',
'Board appears correctly populated; any uncertain orientation has been reviewed against the official board diagram.',
'Quarantine questionable boards and contact the fabricator instead of powering them.',
'Quality control','inspection is not equivalent to an electrical continuity test','No visible bridge is encouraging but not a guarantee of correct nets.',source='docs/hardware/order-main-control-board.md',minutes=35,safety='Power remains disconnected throughout the inspection.')
add('M03','Bench-connect the main board',
'With USB power disconnected, identify the PCB USB-side orientation mark and ESP32 socket directions.|Seat the ESP32 in the correct orientation; attach speaker by the provided connector OR its solder pads.|Inspect the labeled OLED header’s 3.3 V, GND, SDA, SCL order; keep the Head/OLED cable free for its final routing (temporary bench connection is optional, disconnect it again before assembly).|Check servo plugs match signal, 5 V, and GND labels; connect one servo only as needed for the later centering test.',
'Correct polarity and orientation matter more than matching wire colors.',
'Photograph labeling and verify no reversed connectors, shorts, or dual speaker wiring.',
'Disconnect power, then compare each connector with the board’s actual silkscreen and official pinout.',
'Electrical ground & reference','signal voltage is measured relative to the circuit ground','Servo PWM is a signal; it cannot replace the separately supplied 5 V motor rail.',source='docs/hardware/main-control-board.md',minutes=55,safety='SPK− IS NOT GND. Never feed servo 5 V through an ESP32 3.3 V pin.')
# M04
add('M04','Prepare host and USB flashing cable',
'Use Chrome or Edge on a computer with a USB-C data cable.|Keep the main control board with ESP32 on the workbench, not yet inside the desk.|Connect USB power/data to the main BOARD USB-C, not to the ESP32 module connector.',
'The repository’s stock web flasher uses Web Serial; a charge-only cable cannot transmit data.',
'The browser detects the proper serial device when Connect is pressed.',
'Try a known data cable/port and check serial permissions on Linux rather than altering hardware wiring.',
'USB power versus data','USB-C shape ≠ assurance of data wiring','A cable can charge a phone while missing the conductors needed for flashing.',source='docs/flash.md',minutes=30)
add('M04','Flash stock Tiny Engineer firmware',
'Open https://jamro.github.io/tiny-engineer/flash/ in Chrome/Edge.|Select the latest compatible stock release and use Connect & install.|Do not interrupt until flash completes; follow the official recovery procedure if needed.|Observe the setup access point (TinyEngineer-XXXX) or serial boot output; the stock release includes audio content.',
'A known firmware baseline reduces variables before customization.',
'Flashing completes and the powered board offers the documented setup/assembly support route.',
'If no setup AP appears, check board USB-C power, module seating, boot status LED, and flash documentation.',
'Firmware stack','host tool → bootloader → flash memory → application','An upload success proves transfer, not that the whole assembled robot works.',source='docs/flash.md',minutes=55)
add('M04','Learn and execute safe 90° servo centering',
'Join the robot setup access point and visit http://192.168.4.1/config.|In Assembly support choose Move all to 90°; optionally Identify a joint.|For each mechanical connection, attach its servo for centering, then disconnect that servo lead before completing awkward joins.|Do NOT complete full guided range calibration or home Wi-Fi now; that happens after assembly.|Between bench-centering operations, unplug USB and temporary servo leads but KEEP the ESP32 seated in the bench PCB; §3–§7 still need it for further 90° centering. In §12 you will remove the ESP32 before placing the board into the Desk; it returns from ABOVE the Desk in §13.',
'90° is a repeatable electrical midpoint so parts can be mounted with known neutral geometry.',
'A test servo moves to center and can be disconnected safely before mechanical loading.',
'If a servo twitches or resets the board, stop and check the power supply and plug orientation.',
'PWM servo position','angle ≈ normalized pulse width mapped to a calibrated range','90° is the midpoint command, not a guarantee of the output-shaft mechanical center.',source='docs/3d/assembly.md',minutes=50,safety='Keep fingers and loose cables out of moving servo shafts.')
# M05 assembly original sequence
add('M05','Assembly §1 — Populate Head',
'Remove OLED protective film and plug its cable in BEFORE seating the display.|Put one SG90 (no horn yet) and the OLED into Head pockets.|Route OLED and servo cables to opposite sides and into the rear printed clips.',
'Once Head is closed the OLED connector becomes difficult to reach.',
'Both parts seat cleanly and both cables are free of pinch points.',
'Reopen the Head and correct cable routing rather than pulling on a seated connector.',
'Cable strain relief','stress at connector ≠ stress along cable','Molded clips distribute handling loads away from tiny contact pins.',source='docs/3d/assembly.md#1-head--oled-and-servo',minutes=25)
add('M05','Assembly §2 — Close Hat',
'Align Hat on Head without forcing the display or cables.|Fasten with two M2×8 screws into printed plastic, hand snug only.',
'A correctly seated Hat fixes the display and servo geometry.',
'No cable is trapped; Hat is flush and the OLED window is unobstructed.',
'If it bows, remove and check that the OLED cable is not trapped.',
'Torque at fasteners','τ = F × r','More screwdriver force is not better when the female thread is soft PLA.',source='docs/3d/assembly.md#2-hat',minutes=20)
add('M05','Assembly §2a — Reconfirm bench-centering procedure',
'Keep board and power on the workbench rather than in the Desk cavity.|If needed use Assembly support → Move all to 90° to center each servo before installing its shaft-mounted printed part.|After each centering operation, disconnect the appropriate servo lead.',
'Assembly order and calibration order must not be accidentally reversed.',
'You can repeat the centering process without completing the whole Wi-Fi wizard.',
'If the setup hub looks different, follow its documented Assembly support path.',
'Open-loop positioning','servo target angle is not a measured external joint pose','The internal servo feedback helps position its shaft, but printed horn alignment still matters.',source='docs/3d/assembly.md#2a-bench-window-centering',minutes=20)
add('M05','Assembly §3 — Build Neck joint',
'Use a SECOND unused servo and center it to 90°.|Seat printed Neck directly on its shaft, perpendicular to servo body, bulge pointing toward cable/electronics end.|Secure using the included servo shaft screw.|Put one M2 nut in Neck’s larger-hole pocket on the ROBOT’S RIGHT; leave the smaller pocket empty.|Disconnect servo after centering.',
'The keyed shaft orientation sets the head’s yaw reference and the captured nut enables fastening.',
'Neck is perpendicular, nut is captured on correct side, and shaft screw is snug.',
'Remove and re-seat Neck at 90° if the geometry is misaligned.',
'Coordinate-frame convention','right/left are the robot’s own sides','Facing the robot reverses apparent left and right to the builder.',source='docs/3d/assembly.md#3-neck--center-a-servo-and-attach-neck',minutes=40)
add('M05','Assembly §4 — Join Neck and Head',
'Center the Head servo now in Head.|Seat Neck on Head servo shaft, then push it into the Head side assembly so the captured nut aligns.|At 90° align Neck perpendicular to Head.|Fix robot-right side with M2×8 into captured nut and robot-left with servo-bag screw.|Disconnect the Head servo.',
'Two-sided fastening resists misalignment while allowing intended shaft rotation.',
'Head and Neck join with no pinched wires or resistance at neutral.',
'Disassemble to correct trapped wiring or a nut that has fallen out.',
'Kinematics','one servo joint ideally adds one rotational degree of freedom','Head pitch and neck yaw are separate, controlled rotations.',source='docs/3d/assembly.md#4-join-neck-and-head',minutes=45)
add('M05','Assembly §5 — Mount Chest side servos',
'Insert two untouched SG90 servos into the left and right side pockets of Chest; leave horns unattached.|Route leads down the FRONT vertical tunnels so plugs exit below Chest.|Use four M2×16 screws total (two per servo).',
'The Chest secures the left/right hand actuators in predictable positions.',
'Both servos are held securely and cables exit the correct side.',
'If a cable cannot exit below, remove that servo and route before fastening.',
'Load path','mount → printed frame → desk support','Servo force pushes on both the moving arm and the stationary case.',source='docs/3d/assembly.md#5-chest--side-servos',minutes=35)
add('M05','Assembly §6 — Seat Neck servo in Chest',
'Pass the center Neck servo lead down the central front tunnel BEFORE seating it.|Keep Head facing the same direction as Chest front tunnels.|Press the Neck servo into Chest center pocket and use two M2×8 screws if accessible (one back screw accepted by source).',
'Center neck movement must be mechanically supported by the torso.',
'Neck servo does not shift in its pocket; its lead exits below.',
'Unseat the servo and reroute its cable; never pinch the lead to save time.',
'Constraints','a servo case must be restrained for output torque to move the robot','A loose case rotates instead of transmitting the intended motion.',source='docs/3d/assembly.md#6-mount-head-assembly-on-chest',minutes=35)
add('M05','Assembly §7 — Install BellyJoint onto last servo',
'Center the FIFTH unused servo to 90°.|Align BellyJoint hex with one flat parallel to the SHORT side of the servo body.|Press onto the shaft without a separate servo horn, secure with servo-bag screw, and unplug lead.',
'The hex coupler transmits torso motion and its angular alignment determines neutral posture.',
'Hex is correctly aligned and fixed; no servo is left unaccounted for.',
'If the shaft points the hex incorrectly, remove coupler and center again.',
'Rotational coupling','output angle = servo shaft angle + mechanical mounting offset','Calibration can compensate small error but not a completely wrong assembly.',source='docs/3d/assembly.md#7-belly--last-servo',minutes=30)
add('M05','Assembly §8 — Route Chest leads and attach Belly',
'Pass left-hand, Neck, right-hand servo leads through Belly’s top opening and out lower side opening.|Maintain their left→center→right order as a labeling aid only.|Face Belly rounded side backward and join Belly to Chest with four M2×8 screws.',
'Correct cable order simplifies later identification; the channels have a separate numeric sequence.',
'Four fasteners are snug and cables slide without compression.',
'Remove Belly before correcting crossed/pinched leads; do not tug connectors.',
'Signal identification','physical cable order ≠ electrical channel map','Left hand is servo channel 2, not automatically the first cable you see.',source='docs/3d/assembly.md#8-route-chest-cables-through-belly-and-join',minutes=35)
add('M05','Assembly §9 — Seat body in Chair',
'Insert the servo with BellyJoint into the Chair bottom pocket, routing its lead forward along the underside center channel.|Partially slide SeatLeft and SeatRight onto Chair dovetails, leaving a gap.|Lower Belly over the hex coupler; then close the seats without crushing wires.|Optionally use two M2×16 screws.',
'This fixes torso position while preserving a motor-driven body rotation.',
'The body stands supported and the BellyJoint is captured without strain.',
'If the seats resist sliding, inspect coupler engagement and cable path instead of forcing.',
'Dovetail connection','sliding rails constrain motion sideways','Mechanical interlocks can retain parts before or without extra fasteners.',source='docs/3d/assembly.md#9-seat-the-body-in-chair',minutes=50)
add('M05','Assembly §10 — Join DeskTop and DeskPad',
'Nest DeskTop in DeskPad.|Place both onto Desk with rounded cutout toward seated robot.|Secure four corners with M2×16 screws.',
'Correct orientation gives the body clearance toward the desk.',
'Four corners seat flush without rocking or warping.',
'Recheck the rounded cutout orientation before tightening screws.',
'Stacking tolerances','total stack height = sum of mating layer thicknesses','Mis-seated layers can cause screws to bottom out before the joint closes.',source='docs/3d/assembly.md#10-desk-top-stack',minutes=25)
add('M05','Assembly §11 — Attach front emblem',
'Place AiEmblem on Desk front.|Attach with two M2×4 screws, hand snug.',
'Decor is mounted before electronics complicate access.',
'Emblem is stable and no short screw enters the board cavity.',
'If holes are stripped, stop and assess the print; do not overtighten.',
'Assembly accessibility','fasten inaccessible parts before closing an enclosure','Assembly sequencing reduces needless disassembly.',source='docs/3d/assembly.md#11-desk-emblem',minutes=15)
add('M05','Assembly §12 — Seat PCB in Desk',
'Disconnect USB power and temporary servo/OLED leads. Gently pull the ESP32 straight out of the board sockets only NOW (after completing §3–§7 bench centering); put the ESP32 somewhere safe for §13.|Place the pre-tested main PCB without ESP32 in the Desk cavity; keep servo leads and OLED unplugged from the PCB until Assembly §15.|Place speaker inside cavity and use exactly one wiring method, connector OR pads.|Keep ESP32 module outside until it is inserted from above in step 13.',
'The board is enclosed only after it has been bench-flashed, limiting rework.',
'Board sits fully without bent wires, exposed shorts, or speaker pinch.',
'If board does not seat, check part revision and header alignment; do not bend PCB.',
'Enclosure design','clearance maintains electrical and mechanical isolation','A compressed wire can create an intermittent failure only when a cover is tightened.',source='docs/3d/assembly.md#12-electronics-inside-the-desk',minutes=35,safety='Power OFF. SPK− must never be connected to GND.')
add('M05','Assembly §13 — Seat ESP32 and LampBase',
'If needed, solder two 1×9 male pin rows straight onto the ESP32-C3-Zero; the -M variant has headers fitted.|From ABOVE the desk insert ESP32 long pins through cutout into the board sockets, using PCB USB mark to orient.|Optional smoke test: power on board USB-C, verify status LED and setup AP, power off.|Place LampButton under LampBase to reach reset button; fasten LampBase with two M2×8 screws.',
'Seating the ESP32 last avoids interference between its pins and the desk opening.',
'ESP32 is correctly oriented, flush and reachable via LampButton; no pin bends.',
'Power off, remove and correct seating; never rotate a partially inserted module.',
'Electrical connector pitch','2.54 mm header pitch is distance between adjacent pins','Misaligning one pin by a full pitch can short power and signal nets.',source='docs/3d/assembly.md#13-esp32-powerap-smoke-test-and-lampbase',minutes=55)
add('M05','Assembly §14 — Laptop, mug, and bell',
'Slide LaptopScreen into LaptopCase, seat laptop and attach with one M2×8 from underside.|Nest Coffee inside Mug; attach mug with one M2×8 from underside.|Drive an M2×16 into Bell itself first; mount Bell on desk and capture with an M2 nut underneath.',
'Props are installed while underside access remains available.',
'All three props are secure and are clear of wiring.',
'If Bell will not seat, pre-thread it before final mounting as source describes.',
'Mechanical access','an assembly operation requires tool approach clearance','Tightening from below later may be blocked by the enclosed electronics.',source='docs/3d/assembly.md#14-desk-props--laptop-mug-bell',minutes=35)
add('M05','Assembly §15 — Connect all five joints and OLED',
'Tip desk carefully forward to expose headers; keep body supported beside it.|Connect head pitch to PCA9685 CH0, neck yaw CH1, left hand CH2, right hand CH3, torso CH4.|Connect OLED to correct 3.3 V/GND/SDA/SCL header; extend leads with short M–F jumpers preserving each net end-to-end.|Power on for servo + OLED smoke test, then power down before altering plugs.',
'Explicit channel mapping prevents wrong motions and potential collisions.',
'All servos and OLED respond without unexpected reset; each channel has a written label.',
'Disconnect power and trace individual cables before moving a connector.',
'PWM controller channels','PCA9685 channel index ≠ ESP32 GPIO number','CH0 drives head pitch; GPIO0 carries I²C SDA, not the head’s PWM.',source='docs/3d/assembly.md#15-connect-servos-and-oled',minutes=55,safety='Switch OFF before swapping any plugs.')
add('M05','Assembly §16 — Attach Chair to Desk',
'Bring Desk up to Chair without pulling routed cables.|Align matching mounting holes and use six M2×8 screws, three on each side.|Keep cables away from both screw tips and mating edges.',
'The desk supports the chair and makes one stable robot body.',
'Chair/Desk are flush and rigid with no lead visible in a pinch zone.',
'Remove fasteners and reposition wires; never clamp over a lead.',
'Structural load transfer','load distributes through multiple screw locations','Six screw points improve rigidity compared with a single attachment.',source='docs/3d/assembly.md#16-fasten-chair-to-desk',minutes=40)
add('M05','Assembly §16b — Close BottomCover',
'Power down and flip robot over while supporting it safely.|Route leads inside cavities, never through cover screw paths.|Verify Chair is current revision with two reinforced rear blind pilot holes.|Fit BottomCover mating face in, screw pockets outward; install six M2×8 screws (4 desk, 2 chair) with heads ≤4 mm wide and ≤2 mm high.',
'Flat base prevents rocking and avoids severed cables.',
'No pinched cables and all six screw heads are recessed; base rests flat.',
'If rear holes do not exist, replace Chair with matching revision BEFORE closure.',
'Center of mass & support','stability requires projected center of mass within support footprint','A wobbling base makes repeatable servo motion harder to test.',source='docs/3d/assembly.md#close-the-underside-with-bottomcover',minutes=45)
add('M05','Assembly §17 — Build elbow joints',
'Use two UpperArm prints (left/right sides) and the corresponding ForearmLeft/ForearmRight.|Join each forearm to its upper arm with one M2×8 at its elbow.|Do not mount assemblies on Chest servos yet.',
'Off-body elbow work makes fastening easier and protects servo gears.',
'Two matching forearm/upper-arm assemblies articulate as intended.',
'If a joint binds, undo the screw and clean the print rather than forcing.',
'Joint friction','friction torque opposes desired rotation','Overtight screws can turn a freely rotating joint into a locked joint.',source='docs/3d/assembly.md#17-arms--elbow-joints',minutes=35)
add('M05','Assembly §18 — Attach centered arms',
'Recenter left/right hand servos via Assembly support BEFORE mounting arms.|Press each arm shaft pocket onto matching servo shaft.|At 90°, orient each hand near shoulder height with the forearm facing the desk.|Fasten each with its servo-bag screw, then repeat on the other side.',
'Attaching arms at a known neutral avoids collisions in the first commanded move.',
'Both arms align similarly, and neither hits Chest or desk at neutral.',
'Unfasten and change shaft spline indexing rather than commanding extreme angles.',
'Angular offsets','θ_world = θ_servo + θ_mounting_offset','A 20° mechanical offset changes the physical arm pose at a 90° servo command.',source='docs/3d/assembly.md#18-mount-arms-on-the-chest-servos',minutes=45)
add('M05','Assembly §19 — Finish lamp press-fit',
'Press LampCap onto LampDiffuser.|Push both into LampBase by hand, without screws or glue.|Check diffuser wall survived printing and lamp does not obstruct button.',
'The lamp completes the enclosure while leaving reset access.',
'Diffuser stays seated, is uncracked, and reset button remains operable.',
'If diffuser splits, verify Arachne/thin-wall slicing and reprint just it.',
'Interference fit','retention arises from a small elastic deformation','Thin printed walls tolerate less assembly force than thick solids.',source='docs/3d/assembly.md#19-lamp-press-fit',minutes=20)
# M06
add('M06','Complete assembled-servo calibration wizard',
'Power the complete robot through board USB-C and join TinyEngineer-XXXX if in setup mode.|Open http://192.168.4.1/config, start the full wizard, and use Calibrate servos (Body → Neck → Head → Hands).|Move joints conservatively, watching for mechanical stops or collisions.|Confirm OLED orientation, RGB color mapping, and welcome audio; the Assembly support hub is not a substitute for range calibration.',
'Calibration maps firmware commands to actual assembled joint travel limits.',
'All five joints complete guided calibration without binding or violent movement.',
'If a joint collides, stop; correct shaft seating or limits while following wizard, do not overpower the mechanism.',
'Limits and saturation','θ_safe ∈ [θ_min, θ_max]','A calibrated range must fit the actual geometry, not only servo nominal 0–180°.',source='docs/3d/assembly.md#20-setup-wizard-and-first-boot-on-wi-fi',minutes=70,safety='Hands clear of moving parts; disconnect on repeated hard stops.')
add('M06','Finish 2.4 GHz network setup',
'In the wizard choose 2.4 GHz home Wi-Fi for this specific HTTP-based guide. The official USB-only branch exists but needs different serial-based verification steps and is not part of this fixed sequence.|Finish wizard and power-cycle robot once.|Read its IP from OLED; try http://tiny-engineer.local/ in browser, or the IP if mDNS fails.|Record only nonsecret connection information; never store Wi-Fi credentials in dashboard notes.',
'Wi-Fi lets the agent send event commands to the robot REST service.',
'Robot joins the chosen 2.4 GHz network after power cycle and local web UI loads; record its IP.',
'If OLED shows setup AP again, re-enter Wi-Fi wizard and verify 2.4 GHz credentials. Mark this task Blocked rather than proceeding without a network; do not substitute the USB-only path without a separate verification plan.',
'Local networking','hostname → local IP → HTTP endpoint','mDNS resolves tiny-engineer.local to an address; direct IP bypasses mDNS problems.',source='docs/3d/assembly.md#20-setup-wizard-and-first-boot-on-wi-fi',minutes=50)
# M07
add('M07','Prove HTTP health endpoint',
'On a computer on the same network run: curl http://tiny-engineer.local/health.|If .local fails, use OLED IP address instead, optionally curl -4.|Save the response or a screenshot as evidence.',
'This tests Wi-Fi, network addressing, HTTP server, and firmware together.',
'GET /health succeeds against the real robot and is logged.',
'Check connection and OLED IP before reflashing; mDNS failure is not necessarily firmware failure.',
'Client-server communication','HTTP request → route → response','A valid health response proves the web server responds, not the servo or speaker.',source='docs/getting-started.md#7-prove-it',minutes=25)
add('M07','Run safe motion, OLED, LED and sound tests',
'With hands clear and no obstruction, test the documented firmware endpoints one at a time: POST /test/screen, POST /test/led, POST /test/audio, POST /test/movement.|Observe each result, especially brownouts or jitter when multiple servos move.|Send POST /anim?name=ring and check expected movement; sound requires audio files on flash.|Log actual pass/fail for every subsystem separately.',
'Independent subsystem tests isolate faults before full automation.',
'OLED, RGB, audio, servo movement, and ring command each have observed outcomes.',
'For sound failure, inspect firmware LittleFS/audio installation; for resets, check power and mechanical loads.',
'Integration testing','system reliability depends on individual subsystems and interfaces','/health can pass even when a speaker plug is disconnected.',source='docs/hardware/testing.md#http-tests',minutes=75,safety='The movement test actuates all five servos; keep the desk clear.')
add('M07','Run an independent power and enclosure audit',
'Operate a sequence of normal motions with the robot fully assembled and powered by 5 V/≥2 A.|Watch for voltage-related restarts, OLED flicker, servo jitter, sound dropout, and heat or cable rubbing.|Inspect bottom cover, screw heads, chair stability, arm clearance, and visible strain.|Compare finished robot to the original repo photograph and 3D assembly viewer: seated figure behind desk, OLED in Head, joint structure, laptop, mug, bell, lamp, chair seats and front emblem; record any differences.|If a failure appears, isolate it before proceeding to agent integration.',
'An assembled robot can fail under simultaneous load even if bench checks passed.',
'No reproducible reset, wiring pinch, overheating, or structural instability in normal operation, and the physical layout matches the source model or any intended deviation is documented.',
'Unplug on abnormal heat or smell. For repeatable resets review official power guide; do not simply demand a larger voltage.',
'Power budget & margin','I_total(t) = I_logic + Σ I_servos(t) + I_audio(t)','Short servo start-up peaks can matter even when average current looks modest.',source='docs/hardware/power.md',minutes=50,safety='Supply is 5 V, NOT 9 V or 12 V. Disconnect power on abnormal heating.')
# M08
add('M08','Connect coding agent events',
'Install Node.js 18+ on host if using the default setup tool.|Run npx -y tiny-engineer setup per official integration instructions (or select documented USB serial option).|Follow your tool-specific prompts for Cursor, Claude Code or Antigravity.|If using custom scripts, use the supported POST /anim route and do not send arbitrary unsafe motions.',
'The goal is to turn software events into recognizable physical behavior.',
'One real coding-agent event causes the intended real-world robot animation.',
'For silent hooks run npx -y tiny-engineer doctor and follow integration docs; cold npx hooks may require timeout ≥30 s.',
'Event-driven systems','event → handler → network request → actuator action','The robot reacts to an IDE event, rather than polling every file manually.',source='docs/integration.md',minutes=75,optional=True)
add('M08','Finalize documentation and baseline',
'Export a full working copy and step-by-step PDF from the dashboard.|Save a project version named Baseline V1; record tested endpoints, hardware variant, cost, firmware revision, and known limitations.|Use GitHub Backup only after configuring a personal repository and Git authentication; otherwise retain local JSON and ZIP backups.|Create a final target-conformance record that names every physical feature: seated figure/chair, SG90 shell geometry, five articulations, OLED face, laptop, mug, bell, lamp, desk board and bottom cover.|Write a short retrospective with successes, unsolved questions, and next modifications.',
'A reproducible baseline makes future experiments safe and comparable.',
'Version/export files exist; a final conformance checklist is signed off with physical observations or explicit unresolved differences, and the completion report distinguishes performed tests from pending tests.',
'If export fails, retain the SQLite DB and use the app working-copy JSON endpoint before troubleshooting Git.',
'Reproducibility','baseline = hardware + firmware + settings + evidence','Recording only a picture of the finished robot is insufficient to recreate the result.',source='docs/getting-started.md',minutes=50,optional=True)

BOM=[
 dict(name='Assembled main control PCB',qty=1,unit=130.00,kind='Estimate',category='Electronics',url='https://jamro.github.io/tiny-engineer/shop/'),
 dict(name='Waveshare ESP32-C3-Zero',qty=1,unit=7.00,kind='Estimate',category='Electronics',url='https://www.waveshare.com/esp32-c3-zero.htm'),
 dict(name='SG90 analog micro servo',qty=5,unit=3.00,kind='Estimate',category='Actuators',url='https://torqpro.com/product/sg90-analog/'),
 dict(name='Adafruit Mini Oval 8Ω 1W speaker',qty=1,unit=1.95,kind='Previous retail observation',category='Electronics',url='https://www.adafruit.com/product/3923'),
 dict(name='Waveshare 0.91-inch OLED 128×32',qty=1,unit=6.00,kind='Estimate',category='Electronics',url='https://www.waveshare.com/0.91inch-oled-module.htm'),
 dict(name='M2 screw/nut assortment',qty=1,unit=12.00,kind='Estimate',category='Hardware',url=BASE+'docs/shopping.md'),
 dict(name='5V ≥2A USB adapter',qty=1,unit=8.00,kind='Estimate',category='Power',url=BASE+'docs/hardware/power.md'),
 dict(name='USB-C DATA cable',qty=1,unit=4.95,kind='Previous retail observation',category='Power',url='https://www.adafruit.com/product/4474'),
 dict(name='Short M–F jumper pack (≥10)',qty=1,unit=1.95,kind='Previous retail observation',category='Hardware',url='https://www.adafruit.com/product/1953'),
 dict(name='PLA/PETG filament used per build',qty=1,unit=6.00,kind='Estimate',category='Printing',url=BASE+'3d_models/README.md')
]
SOURCE_INDEX=[
 ('Official target photograph','https://github.com/jamro/tiny-engineer/blob/main/docs/tiny-engineer-preview.jpg'),
 ('3D assembly viewer','https://tinyengineer.dev/assembly/'),
 ('Servo movements',BASE+'docs/robot-movement.md'),
 ('Build sequence',BASE+'docs/getting-started.md'),('Shopping',BASE+'docs/shopping.md'),
 ('Printed models',BASE+'3d_models/README.md'),('Assembly',BASE+'docs/3d/assembly.md'),
 ('Board connection',BASE+'docs/hardware/main-control-board.md'),
 ('PCB fabrication',BASE+'docs/hardware/order-main-control-board.md'),
 ('Firmware flash',BASE+'docs/flash.md'),('Pinout',BASE+'docs/hardware/pinout.md'),
 ('Power',BASE+'docs/hardware/power.md'),('Testing',BASE+'docs/hardware/testing.md'),
 ('Integrations',BASE+'docs/integration.md')]
