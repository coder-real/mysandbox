# New Images and Photographs Required

Document: `Approved Departmental Schedule display (Corrected).docx`
(BLE / iPixel rewrite, HRP-1696, 64 × 20 panel)

The rewritten report is complete in its text, tables and numbering. Thirteen
figures are already in place. The list below is what you still have to produce so
that every figure is a real one.

---

## A. Photographs that must be replaced or supplied (6)

| # | Figure | Caption printed in the report | Size on page | What to photograph |
|---|--------|-------------------------------|--------------|--------------------|
| 1 | 2.1 | iPixel 64 × 20 Bluetooth Low Energy LED Matrix Panel | 5.2 in wide | The panel itself, face on, laid flat and evenly lit, with a ruler or a sheet of A4 beside it to establish the 12.59 × 3.15 in size. **This is the one figure that must show 20 rows, not 16** — the current picture was cropped from `image1.png` and still reads as the 16-row unit. |
| 2 | 2.2 | ESP32 NodeMCU-32S Development Board | 3.0 in | The ESP32 board alone on a plain background, USB port towards the camera, pin labels legible. `image2.jpeg` is in place but is a working shot; a clean one is better. |
| 3 | 2.3 | HC-SR501 Passive Infrared Motion Sensor | 2.6 in | The PIR module alone, dome visible, the three pins (VCC, OUT, GND) readable. `image3.png` is in place. |
| 4 | 2.4 | DS3231 Real-Time Clock Module | 3.0 in | The RTC module alone with the CR2032 cell fitted and the six header pins visible. `image4.jpeg` is in place. |
| 5 | 2.5 | 4 × 4 Matrix Membrane Keypad | 2.6 in | The keypad face on, all sixteen legends readable. `image5.jpeg` is in place. |
| 6 | 4.4 | Timetable Scrolling on the Panel after a Level has been Entered | 4.6 in | **The only figure still a placeholder box.** A lit panel with a real level's timetable scrolling: photograph it in a dim room with the camera square to the panel so the text is sharp, at the moment a full line of text is visible. |

Photographs 1–5 exist but at "bench" quality: keep them if you have nothing
better, replace them if you can. Photograph 6 is missing.

## B. Drawings already generated — verify, do not redraw (4)

These are drawn to the built system and are in the document; check them against
your hardware before submission and tell me anything that disagrees.

| # | Figure | Caption | Check against |
|---|--------|---------|----------------|
| 7 | 3.1 | Framing of the Message Written to the Panel | the packet layout in `EEE_Campus.ino` (`uploadIdleClock`, 4 096-byte segments, 509-byte writes) |
| 8 | 3.2 | Circuit Diagram of the Motion-Activated LED Schedule Display | actual wiring: rows GPIO13/12/14/33, columns GPIO32/26/25/19, PIR GPIO27, buzzer GPIO15, I²C GPIO21/22, both branches of the 5 V rail as drawn, **no data wire to the panel** |
| 9 | 3.3 | Block Diagram of the Motion-Activated LED Schedule Display | that the only line from ESP32 to panel is the BLE arrow, and that the 5 V of the panel comes from a second branch of the same rail |
| 10 | 3.4 | Operational Flowchart of the System | the state machine in the firmware (IDLE → GREETING → WELCOME → SCROLL → COOLDOWN) |

## C. Screenshot you may want to re-take (1)

| # | Figure | Caption | Note |
|---|--------|---------|------|
| 11 | 4.5 | Dashboard Served by the ESP32 at 192.168.4.1 | Currently a **redrawn mock** of the web page, not a screenshot. If you can browse to 192.168.4.1 with the board running, capture the real page at about 1 350 × 1 000 px and this figure becomes genuine evidence rather than an illustration. |

## D. Photographs already in place and accepted (2)

| # | Figure | Caption | Source |
|---|--------|---------|--------|
| 12 | 4.1 | Breadboard Prototype of the Schedule Display System | `image104.jpeg` |
| 13 | 4.2 | Component Layout of the Unit in its Enclosure | `image105.jpeg` |

---

## Settled since the last draft

- **Panel size is 64 × 20 (1 280 px).** The `.ino` header (`HRP-1696 64x20`) settles it, and the whole
  report now reads 64 × 20, with the 12.6 × 3.1 in active area of `image1.png`. Figure 2.1's caption
  follows the same size, so the photograph you supply for it must show **20 rows**.
- **One 5 V rail.** The report now states that the panel is fed from the project's own supply, as a second
  branch from the output of the 2-in-1 module to the panel's USB-C socket, and that the only thing kept
  apart is the data path (BLE). The block diagram (3.3) and circuit diagram (3.2) were redrawn to show the
  two branches, and Table 3.7, Table 4.2 and Table 4.3 follow the same arrangement. Section 3.10 rates the
  adapter at 5 V / 4 A, because 2.26 A of load plus up to 1 A of charging current will not fit inside 2 A.

## Reading blanks

Sixty-eight `[ ]` fields in Chapter 4 are deliberate: they are the places where
measured values go (voltages, currents, distances, times, character counts). No
number was invented. Fill them from your test sheets, or send me the readings
and I will enter them.
