# Engineering reference — Tiny Engineer

This is the offline, readable companion to the 14 lessons inside **Engineering Lab**. Definitions and examples are project-specific and educational, not safety certifications.

## 01 · The whole electrical system — What is actually controlling what?

**Definition:** The ESP32-C3 is the computer that interprets commands. A PCA9685 driver creates several repeatable servo-control signals. The five servos turn those signals into mechanical rotations. The OLED displays a face and status. A MAX98357A audio amplifier turns digital audio into a signal strong enough for the small speaker.

**Why this project needs it:** This divides debugging into layers. If Wi-Fi works but the arms do not move, you inspect the controller and servo power rather than assuming the whole robot has failed.

**Equation or system relationship:** `Command → ESP32 → I²C → PCA9685 → servo → mechanical motion`

**Example:** A POST /anim?name=ring request is received by firmware, which selects an animation and commands servo, LED, and sound actions.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/main-control-board.md

## 02 · Voltage, current, and power — Why do we need a 5 V / at least 2 A supply?

**Definition:** Voltage (V) is electric potential difference. Current (A) is the rate at which charge flows. Electrical power (watts) is how quickly energy is delivered. Current draw is determined by the loads, not forcibly pushed by a correctly regulated power supply.

**Why this project needs it:** A servo motor can momentarily draw much more current when it starts or stalls. Multiple servos plus audio can trip protective circuits or make the controller restart.

**Equation or system relationship:** `P = V × I   (W = V × A)`

**Example:** A nominal 5 V, 2 A supply is rated for 5 × 2 = 10 W. This is a capability, not a claim the robot always consumes 10 W. The board has a protected servo rail with an approximately 2 A eFuse limit.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/power.md

## 03 · Separate logic and motor power rails — Why not power servos from the ESP32 3.3 V pin?

**Definition:** The ESP32 logic uses 3.3 V circuitry. The SG90 motors need a separate nominal 5 V supply. A power rail is a common conductor that distributes a given voltage. The main PCB routes USB-C 5 V to protective circuits for servo and audio power and uses the ESP32’s regulator for 3.3 V logic.

**Why this project needs it:** The ESP32 regulator cannot safely supply the starting and stall currents of several motors. Incorrect routing can cause brownouts and damage.

**Equation or system relationship:** `I_total(t) = I_logic(t) + Σ I_servo,i(t) + I_audio(t)`

**Example:** When five servos begin moving, short current peaks may occur together; a healthy 5 V source does not guarantee the protected rail will never limit current.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/power.md

## 04 · Servo position and PWM — What does “move to 90°” mean?

**Definition:** A hobby servo contains a motor, gearing, sensing, and a small internal feedback controller. It interprets a periodic pulse signal as a desired shaft position. The firmware maps desired logical angles into timing values. The signal is a command; the installed part’s exact physical position also depends on shaft spline placement.

**Why this project needs it:** Centering before attaching Neck, BellyJoint, and the arms produces a known starting pose and reduces collisions.

**Equation or system relationship:** `duty cycle (%) = pulse width ÷ period × 100`

**Example:** For a purely illustrative 1.5 ms pulse in a 20 ms period, duty cycle = 7.5%. This is not a guarantee of the project’s actual calibration or servo angle limits.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/3d/assembly.md#2a-bench-window-centering

## 05 · Rotational degrees of freedom — What do the five motors move?

**Definition:** A rotational degree of freedom is one independently controlled joint angle. This robot has five addressed servo joints: head pitch (tilt), neck yaw (turn), left hand, right hand, and body/torso. The robot remains seated on its desk.

**Why this project needs it:** The channels must map to the correct physical joints or commands will move the wrong hardware. “Robot left” is defined from its own viewpoint.

**Equation or system relationship:** `q = [head_pitch, neck_yaw, left_hand, right_hand, torso]`

**Example:** PCA9685 channels 0–4 correspond to that ordering, which is different from the ESP32 GPIO numbering.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/pinout.md

## 06 · Force, lever arm, and servo torque — Why can a small printed arm overload a motor?

**Definition:** Torque is the turning effect of force about a joint. Gravity applies force downward to the mass of an arm. The farther its center of mass lies horizontally from the joint, the larger the torque the motor must resist. A short desk arm may be light, but friction and acceleration also matter.

**Why this project needs it:** Torque explains why joints move differently depending on orientation and why a stalled motor creates heat and current spikes.

**Equation or system relationship:** `τ = r × F; for gravity magnitude: τ = m g r⊥`

**Example:** Illustrative only: a 0.05 kg print with 0.04 m perpendicular lever arm gives 0.05 × 9.81 × 0.04 ≈ 0.0196 N·m. Do NOT use this number as a measured servo requirement.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/robot-movement.md

## 07 · I²C: two shared control wires — How can one ESP32 talk to the OLED and servo driver?

**Definition:** I²C is a digital bus with a serial data line (SDA) and serial clock line (SCL). Multiple compatible devices share the two lines but have different bus addresses. On the documented Tiny Engineer pinout, GPIO0 carries SDA and GPIO1 carries SCL.

**Why this project needs it:** A broken SDA/SCL connection can disable the servo controller or display even when 5 V motor power exists.

**Equation or system relationship:** `ESP32 SDA(GPIO0), SCL(GPIO1) → PCA9685(0x40) + OLED(0x3C)`

**Example:** A boot LED code of one red flash indicates the firmware could not find the PCA9685 at 0x40; check wiring or board assembly rather than changing the servo order.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/testing.md

## 08 · I²S and speaker output — Why is the speaker wiring different?

**Definition:** I²S carries synchronized digital audio. The ESP32 sends clock, frame timing, and data to an audio amplifier (MAX98357A), which drives the speaker. The pair SPK+/SPK− is an amplifier output, not the same as a simple signal wire and ground.

**Why this project needs it:** Tying SPK− to ground or connecting both speaker methods can damage the output stage or make audio unreliable.

**Equation or system relationship:** `I²S digital samples → amplifier → differential speaker output`

**Example:** If servos move during “ring” but audio is silent, check speaker connector/polarity and the flashed audio assets separately.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/main-control-board.md

## 09 · Dimensional tolerance and 3D printing — Why does a good CAD model sometimes print with bad fit?

**Definition:** Manufacturing has dimensional errors. CAD describes nominal geometry, while filament shrinkage, extrusion width, and print orientation change actual dimensions. A tolerance specifies acceptable deviation. Screw pilots and servo pockets are different interfaces and need independent tests.

**Why this project needs it:** Printing ServoSizingTester and ScrewSizingTest first catches mismatches before wasting filament on the whole enclosure.

**Equation or system relationship:** `clearance = opening dimension − part dimension`

**Example:** If a measured opening is 23.7 mm and the servo body is 23.9 mm, clearance is −0.2 mm (interference). Do not force the servo into brittle plastic.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/3d_models/README.md

## 10 · PCB, BOM, CPL, and PCBA — Why are three files needed to order a board?

**Definition:** A printed circuit board (PCB) is the manufactured structure of copper traces and drilled holes. Gerber files describe copper, solder mask and outlines. A bill of materials (BOM) lists components and identities. A component placement list (CPL) gives pick-and-place coordinates and rotations. PCBA means assembly of components onto the board.

**Why this project needs it:** The correct parts in the wrong orientation can make a visually neat but nonfunctional board.

**Equation or system relationship:** `Manufacturing correctness = matching board revision + BOM + placement + inspection`

**Example:** The two-sided PCBA option includes the ESP32 female headers; top-side-only assembly leaves hand soldering of those sockets.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/order-main-control-board.md

## 11 · Firmware, flash memory, and setup access point — Why flash before final mechanical assembly?

**Definition:** Firmware is the software stored in the microcontroller’s nonvolatile flash. It initializes I²C, OLED, audio, motors, and networking. An access point (AP) is a Wi-Fi network created by the robot during setup so it can receive initial configuration.

**Why this project needs it:** A flashed and bench-tested control system allows servo centering before delicate parts are mounted, and avoids opening the desk later for basic debugging.

**Equation or system relationship:** `Flash → boot → setup AP → center → mechanically assemble → calibrate`

**Example:** The setup AP commonly has a TinyEngineer-XXXX name. The configuration page is http://192.168.4.1/config while connected to that AP.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/getting-started.md

## 12 · IP addresses and REST requests — What does curl /health actually test?

**Definition:** An IP address identifies a network device. A hostname like tiny-engineer.local can resolve to that address via local mDNS. HTTP is a request/response protocol. A GET asks for information; a POST asks the firmware to perform an action. A REST API exposes named paths for these actions.

**Why this project needs it:** Separating connectivity from hardware movement avoids confusing an mDNS error with a broken robot.

**Equation or system relationship:** `GET /health → status; POST /anim?name=ring → animation command`

**Example:** If tiny-engineer.local does not resolve, use the IP shown on the OLED before reflashing firmware.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/getting-started.md

## 13 · Testing by subsystem — How can a beginner prove something really works?

**Definition:** A smoke test is a quick check for major faults. A subsystem test verifies one part in isolation. An integration test checks parts operating together. End-to-end verification checks the complete robot from host command to physical response.

**Why this project needs it:** The dashboard requires explicit evidence so a blocked upstream step cannot be hidden by future completion checkmarks.

**Equation or system relationship:** `Test order: power → firmware → OLED → audio → each servo → multi-servo → network → agent`

**Example:** A successful /health means the HTTP server is reachable; it does not prove the speaker, servo torque, or lack of cable pinches.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/hardware/testing.md

## 14 · Engineering decisions and reproducibility — Why record failed tests and version numbers?

**Definition:** A repeatable experiment records configuration, inputs, procedures, observations, and a clear pass/fail decision. Reproducibility means a later session can recreate the result from the recorded evidence. Progress is a claim about what was tested, not about how many pages were read.

**Why this project needs it:** A baseline version separates the working build from changes that may introduce regressions.

**Equation or system relationship:** `Confidence increases with independent evidence, not the number of unchecked assumptions`

**Example:** Record the exact printed servo preset, PCB revision, firmware release, physical test result, and an observation if the OLED is blank.

**Upstream:** https://github.com/jamro/tiny-engineer/blob/main/docs/getting-started.md
