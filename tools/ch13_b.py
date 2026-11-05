"""Chapter three: circuit analysis and design for the BLE-driven display."""


def chapter3(r):
    r.h1("CIRCUIT ANALYSIS AND DESIGN")

    r.h2("Introduction")
    r.p("This chapter presents the electrical analysis and the design of each subsystem of the "
        "motion-activated LED departmental schedule display. Two questions are answered for every part: how "
        "were its values determined, and why was it chosen over its alternatives? The system comprises the "
        "ESP32 microcontroller as the controller, an iPixel 64 × 20 Bluetooth Low Energy LED matrix as the "
        "display, an HC-SR501 PIR sensor, a DS3231 real-time clock, a 4 × 4 matrix keypad, a passive buzzer, "
        "and one power arrangement: a 5 V adapter with a lithium-ion charge and discharge module and a cell, "
        "from which the controller and the panel are fed by separate branches of the same rail.")

    r.h2("ESP32 Microcontroller as the Controller")
    r.p("The ESP32 was selected on four counts: its dual-core 240 MHz processor, its combined Wi-Fi and "
        "Bluetooth Low Energy radio, its flash memory, which is large enough to hold the web page, the "
        "dashboard assets and a complete departmental timetable, and its cost. A single-core Arduino Mega 2560 "
        "was rejected because it has neither a radio nor enough program memory for the page, and an Arduino "
        "Uno with a separate Bluetooth module was rejected because a second processor would have to be "
        "interfaced and powered. The ESP32 operates at 3.3 V logic, with an absolute maximum of 3.6 V on any "
        "pin, and 12 mA of continuous current per pin.")
    r.p("The choice of radio matters more than the choice of processor. The panel is a Bluetooth peripheral, so "
        "the controller must be a Bluetooth client; the administration page must be served over Wi-Fi, so the "
        "controller must be an access point. The ESP32 is one of very few inexpensive devices that can be both "
        "at once, and the firmware of this project uses the qualification that comes with that: the radio "
        "time-shares between the two protocols.")

    r.h2("GPIO Pin Allocation")
    r.p("The pin assignment was decided by five constraints: the fixed functions of the I²C bus and of the "
        "strapping pins, the need for internal pull-ups on the keypad rows, the exclusion of the input-only "
        "pins GPIO34 to GPIO39, the desire to keep the pins used by the USB serial port free for the Serial "
        "Monitor, and the requirement that no pin be shared between two peripherals. The complete allocation "
        "is given in Table 3.1.")
    r.p("Three points in the table deserve comment. GPIO21 and GPIO22 are the hardware I²C pins and are used "
        "for the clock because a silicon implementation of the bus is more tolerant of bus capacitance than a "
        "software one. GPIO12, GPIO13, GPIO14 and GPIO15 are strapping pins whose level is read at reset; of "
        "these, GPIO12 selects the flash voltage and must not be pulled up at start-up, which is why it drives "
        "a keypad row that idles high through the internal pull-up only after the boot has completed, and "
        "GPIO15 is used for the buzzer because the buzzer is driven only after the system is running. GPIO34 "
        "to GPIO39 were not used at all, because they are input-only and have no internal pull-up, so a keypad "
        "scanned in the usual way cannot use them.")

    r.table("GPIO Pin Allocation of the ESP32 Controller", [
        ["GPIO", "Direction", "Connected to", "Function", "Design note"],
        ["GPIO27", "Input", "HC-SR501 OUT", "Motion detection", "Interrupt on a rising edge"],
        ["GPIO21", "I²C SDA", "DS3231 SDA", "Clock data line", "4.7 kΩ pull-up on the module"],
        ["GPIO22", "I²C SCL", "DS3231 SCL", "Clock line", "4.7 kΩ pull-up on the module"],
        ["GPIO13", "Input, pull-up", "Keypad row 1", "Row read during scan", "Bidirectional pin"],
        ["GPIO12", "Input, pull-up", "Keypad row 2", "Row read during scan", "Strapping pin, read at reset"],
        ["GPIO14", "Input, pull-up", "Keypad row 3", "Row read during scan", "Bidirectional pin"],
        ["GPIO33", "Input, pull-up", "Keypad row 4", "Row read during scan", "No special function"],
        ["GPIO32", "Output", "Keypad column 1", "Column driven low", "High impedance when not scanned"],
        ["GPIO26", "Output", "Keypad column 2", "Column driven low", "High impedance when not scanned"],
        ["GPIO25", "Output", "Keypad column 3", "Column driven low", "High impedance when not scanned"],
        ["GPIO19", "Output", "Keypad column 4", "Column driven low", "High impedance when not scanned"],
        ["GPIO15", "Output", "Passive buzzer", "Key acknowledgement", "tone(15, 1000, 70)"],
        ["5V / VIN", "Power", "5 V rail", "Controller supply", "5 V, 2 A from the module"],
        ["3V3", "Power", "DS3231 VCC", "Clock supply", "On-board regulator output"],
        ["GND", "Ground", "Module, sensor, buzzer", "Common reference", "Star point at the module"],
    ], [1200, 1250, 1500, 1700, 2200], font=17)
    r.p("No pin is assigned to the display, and that is the central architectural feature of this design. The "
        "panel is reached over the 2.4 GHz radio, so the ten GPIO lines that a wired matrix would have needed "
        "are free for the keypad and for future expansion, and no level shifting or series resistance is "
        "required on any signal leaving the controller.")

    r.h2("The iPixel LED Matrix as the Display")
    r.p("The display is an iPixel LED matrix of 64 columns and 20 rows, that is 1 280 pixels, built on a "
        "flexible printed circuit and carrying an on-board controller with its own flash memory, a Bluetooth "
        "Low Energy transceiver and a USB-C socket for power. Its active area measures about "
        "12.6 × 3.1 inches (320 × 80 mm), and its supply is quoted by the vendors of the family as 5 V at "
        "2 A at full load, that is 10 W, a figure that corresponds to about 12 mW for each of the 1 280 RGB "
        "pixels when the whole field is lit.")
    r.p("It was chosen over the three alternatives that a project of this kind might use. A HUB75 matrix "
        "requires thirteen conductors, a level shifter and a refresh routine that monopolises the processor, "
        "and its power consumption at this size is of the same order. A chain of WS2812B modules requires a "
        "timing-critical data stream, a frame buffer of 3 072 bytes per frame, and a serpentine pixel map that "
        "must be re-derived whenever the number or the arrangement of the modules changes. A character LCD or "
        "an OLED display requires none of that but is unreadable across a corridor. The iPixel panel combines "
        "the legibility of the matrix with the interface of the character display: the host sends text, and "
        "the panel does the rest.")
    r.p("The price of that convenience is control. The typeface, the letter spacing, the character set, the "
        "colour mapping and the speed of the scroll belong to the controller of the panel, and the firmware "
        "can only choose among the options that the protocol exposes: the text, the colour, the speed, the "
        "brightness and the power state. The design accepts that limitation in exchange for the removal of an "
        "entire subsystem from the firmware, and the consequences are recorded in Section 4.5.3.")

    r.table("Specification of the iPixel Bluetooth Low Energy LED Matrix", [
        ["Parameter", "Value"],
        ["Matrix size", "64 columns × 20 rows = 1 280 pixels"],
        ["Pixel type", "Addressable RGB LED, 1 280 devices"],
        ["Colour", "24-bit RGB; this project uses a single green"],
        ["Controller", "On-board, with font, frame buffer and flash memory"],
        ["Message slots", "9 stored messages"],
        ["Radio", "Bluetooth Low Energy, GATT server"],
        ["Service and characteristics", "0x00FA service; 0xFA02 write; 0xFA03 notify"],
        ["Advertised name", "LED_BLE_ followed by the device identifier"],
        ["Power", "5 V DC through the USB-C socket; up to 2 A (10 W) at full brightness"],
        ["Active area", "about 320 mm × 80 mm (12.6 in × 3.1 in)"],
        ["Mounting", "Flexible substrate with eyelets at the ends"],
    ], [2600, 6100])

    r.h2("Bluetooth Low Energy Link Between the Controller and the Panel")
    r.p("The link is a standard BLE connection in which the panel is the GATT server and the ESP32 is the "
        "client. At start-up the ESP32 initialises its Bluetooth stack, scans for a device whose advertised "
        "name begins with LED_BLE_, connects to the address recorded in the firmware, negotiates a Maximum "
        "Transmission Unit of 512 bytes, enumerates the services and keeps a handle on the characteristic at "
        "0xFA02. Every command is then a write to that characteristic, and every acknowledgement is a "
        "notification on 0xFA03.")
    r.p("Three parameters of the link had to be chosen. The first is the connection interval, which the client "
        "requests: a short interval delivers a message sooner but holds the radio more often, and the firmware "
        "uses the default of the ESP32 stack, which is 30 ms to 50 ms depending on the negotiation. The second "
        "is the MTU, which is requested as 512; the panel grants 512 in practice, so a single write carries 509 "
        "bytes of payload, which is why a message of 1 000 bytes needs only two or three writes rather than "
        "fifty. The third is the pause between writes, set to 8 ms in the firmware, which gives the controller "
        "of the panel time to consume one write before the next arrives; without it the panel drops bytes and "
        "the message appears truncated.")
    r.p("The throughput that results can be estimated. A message of 60 characters occupies 9 tiles of 8 columns "
        "each, that is 180 bytes of payload plus the 15-byte envelope, or about 195 bytes, which fits into a "
        "single write and is transferred in one connection interval plus the processing pause. A message of "
        "280 characters, the limit imposed by the firmware, occupies 490 tiles, 9 800 bytes of payload, and is "
        "sent as three segments of 4 096 bytes; at 509 bytes per write and 8 ms per write, each segment takes "
        "about 70 ms, so the whole message is in the panel within a quarter of a second. That is fast enough "
        "that the student at the keypad does not notice the transfer, and it is the figure against which the "
        "response time measured in Section 4.4.5 is compared.")
    r.table("Design Values of the Bluetooth Low Energy Link", [
        ["Parameter", "Value", "Reason"],
        ["Role of the ESP32", "GATT client", "The panel is the server and owns the data"],
        ["Addressing", "Fixed MAC address in the firmware", "One panel per unit; no scan at run time"],
        ["MTU requested", "512 bytes", "509 bytes of payload per write"],
        ["Fragment pause", "8 ms between writes", "Gives the panel controller time to consume"],
        ["Segment size", "4 096 bytes, 180 ms pause", "Separates the message into recoverable parts"],
        ["Maximum message", "280 characters", "Set by the memory of the panel controller"],
        ["Reconnection", "Retry with back-off", "A lost link must not stop the display"],
        ["Power state", "Panel powered on at connection", "Brightness 80 of 100"],
    ], [1900, 2400, 4400], font=17)
    r.figure("fig3_2_bleframe", "Framing of the Message Written to the Panel", 6.3,
             "The envelope and payload of a single message. The 15-byte envelope carries the length, the "
             "command, the payload length, a CRC32, the slot and the display parameters; the payload is a run "
             "of 20-byte records, one for every eight columns of the rendered text.")
    r.p("Two failure modes of the link were considered at the design stage. The first is the loss of the "
        "connection, which happens if the panel is switched off, if it is taken out of range, or if the ESP32 "
        "restarts. The firmware detects this from the state of the client and reconnects with an increasing "
        "delay; because the panel keeps the last message in its own flash memory, the display does not go "
        "blank while the link is down, which is the practical advantage of a panel with a controller of its "
        "own. The second is contention with Wi-Fi, since both protocols share one radio in the ESP32. The "
        "firmware therefore serves web requests between messages rather than during one, so an upload never "
        "interrupts a transmission and a transmission never delays a page for longer than the few hundred "
        "milliseconds that a message takes.")

    r.h2("PIR Motion Sensor Interface")
    r.p("The HC-SR501 is supplied from the 5 V rail, which gives its comparator the full headroom for which it "
        "was designed, and its output is taken to GPIO27. The output of the module is a 3.3 V logic signal, so "
        "no level shifter is required even though the module itself runs from 5 V. Table 3.4 gives the "
        "connection.")
    r.table("HC-SR501 to ESP32 Connection", [
        ["HC-SR501 pin", "ESP32 pin", "Function"],
        ["VCC", "5 V rail", "Supply; full comparator headroom"],
        ["GND", "GND", "Common ground"],
        ["OUT", "GPIO27", "Presence signal, active high"],
    ], [2200, 2200, 4300])
    r.p("The sensitivity potentiometer is set to about mid-scale, which corresponds to a detection range of "
        "four to five metres and which covers the width of the corridor while rejecting movement in the "
        "adjacent room. The hold-time potentiometer is set to its minimum of about three seconds, because the "
        "firmware manages the session itself and the hardware delay need only confirm that an event has "
        "occurred. The output is read through an interrupt on the rising edge; the routine sets a flag and "
        "does nothing else, and the main loop decides what to do with the flag on its next pass, so that a "
        "detection arriving during a BLE transmission is not lost and cannot interrupt it.")

    r.h2("DS3231 Real-Time Clock Interface")
    r.p("The clock is connected to the hardware I²C bus and is powered from the 3V3 pin of the ESP32 so that "
        "its logic levels match those of the controller and no level shifting is needed. Table 3.5 gives the "
        "connection. The module carries 4.7 kΩ pull-up resistors on both lines, which were checked against the "
        "requirements of the bus rather than assumed.")
    r.table("DS3231 to ESP32 Connection", [
        ["DS3231 pin", "ESP32 pin", "Function"],
        ["VCC", "3V3", "Supply, 1 mA active"],
        ["GND", "GND", "Common ground"],
        ["SDA", "GPIO21", "I²C data, 4.7 kΩ pull-up on the module"],
        ["SCL", "GPIO22", "I²C clock, 4.7 kΩ pull-up on the module"],
    ], [2200, 2200, 4300])

    r.h3("Verification of the I²C Pull-up Resistors")
    r.p("Two conditions fix the value of an I²C pull-up. The resistor must be small enough that the bus rises "
        "to a valid high level within the time allowed at the chosen rate, which sets a maximum value, and "
        "large enough that the current it sinks when a device pulls the line low does not exceed the 3 mA that "
        "the specification guarantees, which sets a minimum value. For the standard 100 kHz mode, a supply of "
        "3.3 V and an estimated bus capacitance of 100 pF, the rise time of 1 000 ns gives a maximum resistance "
        "of about 10 kΩ, and the 3 mA limit gives a minimum of about 1.1 kΩ. The 4.7 kΩ fitted on the module "
        "lies inside that window with room on both sides, so no additional resistor is needed and the bus will "
        "work at 100 kHz over the short length of hook-up wire used here.")

    r.h2("4 × 4 Matrix Keypad Interface")
    r.p("The keypad is scanned by driving one column low at a time and reading the four rows, which are held "
        "high by the internal pull-up resistors of the ESP32. When a key is pressed it connects its row to its "
        "column, so the row of the pressed key reads low while that column is driven. Only one column is "
        "driven at a time and the others are left as high-impedance inputs rather than driven high, so that "
        "two keys pressed together cannot short an output to ground. The internal pull-up of an ESP32 GPIO is "
        "nominally 45 kΩ, so the current that flows when a key closes is about 3.3 V divided by 45 kΩ, that is "
        "0.073 mA, which is far below the 12 mA rating of the pin and needs no external resistor.")
    r.table("Keypad to ESP32 Pin Mapping", [
        ["Keypad pin", "ESP32 GPIO", "Direction", "Function"],
        ["Row 1 (R1)", "GPIO13", "Input, pull-up", "Read row 1 while a column is driven"],
        ["Row 2 (R2)", "GPIO12", "Input, pull-up", "Read row 2 while a column is driven"],
        ["Row 3 (R3)", "GPIO14", "Input, pull-up", "Read row 3 while a column is driven"],
        ["Row 4 (R4)", "GPIO33", "Input, pull-up", "Read row 4 while a column is driven"],
        ["Column 1 (C1)", "GPIO32", "Output", "Drive low to scan column 1"],
        ["Column 2 (C2)", "GPIO26", "Output", "Drive low to scan column 2"],
        ["Column 3 (C3)", "GPIO25", "Output", "Drive low to scan column 3"],
        ["Column 4 (C4)", "GPIO19", "Output", "Drive low to scan column 4"],
    ], [1900, 1700, 1700, 3400])
    r.p("A scan runs on every pass of the main loop. A key is accepted only after it has been stable for 75 ms, "
        "and the keypad is then disarmed until every key has been released for 80 ms. This two-sided timing "
        "rejects the contact bounce of a membrane keypad, which lasts ten to twenty milliseconds, and prevents "
        "one press from registering twice. A scan that finds two keys closed at once returns an invalid code "
        "and the press is ignored, which is why the routine distinguishes a single key from a multiple press.")

    r.h2("Buzzer Interface")
    r.p("The buzzer is a passive piezo sounder, which contains no oscillator and therefore sounds at whatever "
        "frequency is applied to it. It is driven directly from GPIO15 through the tone() function, which uses "
        "a hardware timer to produce a square wave, in the call tone(15, 1000, 70) that sounds a 1 kHz note "
        "for 70 ms at each accepted key press. A sounder of this size draws about 10 mA while it sounds, which "
        "is inside the 12 mA continuous rating of the pin, and because the note lasts 70 ms and is repeated "
        "only when a key is accepted, the average current is a small fraction of even that. No transistor "
        "stage is required. A freewheeling diode would be required only if the load were inductive, which a "
        "piezo sounder is not.")

    r.h2("Power Supply Design")
    r.p("The system runs from a single 5 V rail. A 5 V, 4 A USB adapter feeds a 2-in-1 lithium-ion charge and "
        "discharge module and a 4 000 mAh cell; the 5 V output of that module then feeds two branches. The "
        "first branch supplies the controller, the PIR sensor, the clock and the buzzer, either directly or "
        "through the 3V3 regulator of the ESP32 board. The second branch goes to the USB-C input of the iPixel "
        "panel, so that the panel is powered from the same project supply as everything else and needs no "
        "mains adapter or charger of its own. The rail is common; what the design keeps separate is the "
        "conductor that carries data, because the panel is reached only over the Bluetooth link.")

    r.h3("Current Demand of the Two Loads")
    r.p("The demand of the controller side is the sum of the ESP32 at about 250 mA with its radio active, the "
        "PIR sensor at under 1 mA, the DS3231 at 1 mA and the buzzer at 10 mA when sounding:")
    r.eq("I_ctrl = 0.25 A + 0.001 A + 0.001 A + 0.01 A  =  0.26 A")
    r.p("The demand of the panel is of a different order. The family of panels to which this one belongs is "
        "specified by its vendors as a 5 V load of up to 2 A, that is 10 W, and the figure is consistent with "
        "1 280 RGB "
        "LEDs at a brightness of about 80 per cent: if a lit pixel draws of the order of 1 mA at that "
        "brightness, a field in which a third of the pixels are lit draws about 0.34 A, a field in which all "
        "are lit at full white draws about 1.0 A, and the controller and the radio add a further 50 mA. The "
        "worst case is therefore about 1.5 A, and the 2 A figure quoted by the vendors leaves a margin of "
        "about 30 per cent for the inrush at switch-on and for the ageing of the supply.")
    r.p("The two figures together set the rating of the single supply. A panel load of up to 2 A, which is "
        "the vendor rating of the family and is above the 1.5 A estimated here for a lit field, added to a "
        "0.26 A controller load gives 2.26 A in the worst case, and the current of a scrolling message is "
        "pulsed rather than steady, which adds a further allowance. A 5 V, 2 A adapter would therefore sit almost "
        "exactly at its limit with no margin, and the dips that a pulsed load produces on a saturated rail "
        "would appear as disturbance on the BLE link that the ESP32 is trying to hold. The supply is "
        "consequently rated at 4 A: two and a quarter amperes of load, plus the charging current of the cell, "
        "plus a margin for inrush and ageing, all inside one adapter instead of two.")

    r.h3("Choice of the Shared Supply")
    r.p("The rail is produced by a 5 V, 4 A USB adapter feeding a 2-in-1 lithium-ion charge and "
        "discharge module. The module charges the cell under a constant-current, constant-voltage profile, "
        "supplies the load from the adapter while the mains is present, transfers the load to the cell through "
        "a boost converter when the adapter is removed, and protects the cell against over-charge, "
        "over-discharge and short circuit. Because the transfer is electronic there is no relay, and therefore "
        "no interval during which the ESP32 is unpowered, which means that a mains failure does not reset the "
        "controller or break the BLE connection.")
    r.p("The power drawn from the adapter is the product of the rail voltage and the controller current:")
    r.eq("P_ctrl = 5 V × 0.26 A = 1.3 W")
    r.p("The controller side alone would be satisfied by the smallest adapter on the market, since 1.3 W is "
        "well under a tenth of a 4 A rating. The rating is set by the panel and by the cell, not by the "
        "controller. A 4 000 mAh cell charged at 1 A takes about four hours to fill from empty, and that "
        "charging current is drawn from the same adapter while both loads are supplied, so the adapter carries "
        "about 2.26 A of load plus up to 1 A of charging current, or 3.26 A, during a charge of a flat cell "
        "with the panel at full brightness. That is the worst case the 4 A rating is chosen against, and it "
        "leaves roughly 20 per cent of headroom.")

    r.h3("Choice of the Panel Supply")
    r.p("The panel is fed from the same 5 V rail through the USB-C socket at its left-hand end, by a branch "
        "taken from the output of the 2-in-1 module. Its own controller performs any regulation that its LEDs "
        "require, so a 5 V source of adequate current is the whole of the requirement, and the 4 A adapter "
        "already provides it. The panel draws about 1.5 A in the worst case, so the branch carries that "
        "current with the adapter's remaining capacity as margin; no separate charger, power bank or mains "
        "adapter is used for the display.")
    r.p("The branch to the panel is taken from the output of the 2-in-1 module and not from the 3V3 or the 5V "
        "pin of the ESP32 board, and this deserves to be stated plainly because the temptation exists. The 5V "
        "pin of a NodeMCU-32S is connected to the input of an AMS1117-3.3 regulator and to the USB connector, "
        "not to a path capable of 2 A; the polyfuse and the diode of the board would overheat long before the "
        "panel reached its working current, and the resulting voltage drop would reset the controller. The "
        "panel therefore takes its 5 V from the project rail at the module, in parallel with the controller "
        "branch, and its only connection to the controller is radio.")

    r.h3("Energy Store and Backup Time")
    r.p("The backup time of the controller side follows from the energy stored in the cell. With a capacity C "
        "in ampere-hours, a nominal cell voltage of 3.7 V and an assumed efficiency of 0.85 for the boost "
        "stage of the module, the energy available at the 5 V rail and the current drawn from the cell are:")
    r.eq("E = C × V_cell × η = 4 Ah × 3.7 V × 0.85 = 12.6 Wh")
    r.eq("I_cell = P_ctrl / (V_cell × η) = 1.3 W / (3.7 V × 0.85) = 0.41 A")
    r.p("The cell is therefore discharged at about 0.41 A, which is a fifth of its 2 A continuous rating and "
        "which the module passes without significant heating. Dividing the capacity by that current gives the "
        "backup time of the controller:")
    r.eq("t_ctrl = 4 Ah / 0.41 A = 9.8 h")
    r.p("The same cell therefore carries the whole display and not merely the controller, because the panel "
        "is fed from the same rail through the same module. The load on the rail is the sum of the two "
        "branches, and the current taken from the cell follows from the same efficiency:")
    r.eq("I_cell = (5 V × I_rail) / (3.7 V × 0.85) = 1.59 × I_rail")
    r.p("With the panel lit but stationary, the rail carries about 0.26 A for the controller branch and "
        "about 0.6 A for the panel, that is 0.86 A, and the cell delivers about 1.4 A. With a message "
        "scrolling and the panel at its worst-case 1.5 A the rail carries about 1.76 A and the cell about "
        "2.8 A. The backup time is the capacity divided by each of those currents:")
    r.eq("t_idle = 4 Ah / 1.4 A = 2.9 h          t_scroll = 4 Ah / 2.8 A = 1.4 h")
    r.p("These are design estimates and the measured figures are given in Section 4.4.2. The important "
        "consequence is that an administrator who arrives after an interruption of an hour still finds the "
        "access point running, the clock correct and the panel lit, and can upload a fresh timetable; an "
        "outage longer than that is covered by the timetable held in flash memory, which is not lost when "
        "the cell is exhausted.")

    r.h3("Table of Power Requirements")
    r.p("Table 3.7 collects the requirements. It shows the single rail and the two branches taken from it, and "
        "it gives the design values against which the measurements of Chapter Four are compared.")

    r.table("Summary of Power Requirements", [
        ["Load", "Rail", "Typical current", "Peak current", "Fed from"],
        ["ESP32, radio active", "5 V in, 3.3 V core", "250 mA", "350 mA", "First branch of the rail"],
        ["HC-SR501 PIR sensor", "5 V", "0.5 mA", "1 mA", "First branch of the rail"],
        ["DS3231 real-time clock", "3.3 V", "1 mA", "1.5 mA", "3V3 pin of the ESP32"],
        ["4 × 4 keypad", "3.3 V", "0.1 mA", "0.1 mA", "GPIO pull-ups"],
        ["Passive buzzer", "5 V", "10 mA when sounding", "20 mA", "First branch of the rail"],
        ["Controller branch total", "5 V", "about 0.26 A", "about 0.37 A", "First branch of the same rail"],
        ["iPixel panel, part lit", "5 V", "about 0.6 A", "1.5 A", "Second branch of the same rail"],
        ["iPixel panel, full white", "5 V", "about 1.0 A", "1.5 A", "Second branch of the same rail"],
        ["Total on the rail", "5 V", "about 0.86 A", "about 1.76 A", "5 V, 4 A adapter and module"],
    ], [2100, 1500, 1700, 1400, 2000], font=16)

    r.h2("Circuit Diagram")
    r.p("Figure 3.2 is the circuit diagram of the complete system. It is drawn to make the two boundaries of "
        "the design explicit. The upper block is the panel, which has no signal conductor to anything else: its "
        "only connection to the controller is the Bluetooth link drawn as a double-headed arrow, and its 5 V "
        "reaches it as a second branch of the project rail, shown in green. The centre block is the controller, "
        "with the PIR sensor, the clock, the keypad and the buzzer attached to the pins listed in Table 3.1. "
        "The lower block is the power arrangement shared by both loads: the adapter, the 2-in-1 module and the "
        "cell, with branch 1 of the 5 V rail leaving the module to the 5V pin of the ESP32 and the 3V3 pin of "
        "the board feeding the clock. All ground returns meet at one point at the module, which is what keeps "
        "the pulsed current of the panel out of the reference used by the keypad and the I²C bus.")
    r.figure("fig3_1_circuit", "Circuit Diagram of the Motion-Activated LED Schedule Display", 6.8,
             "The complete circuit. The panel is reached only by radio; the controller's 5 V rail feeds the "
             "ESP32, the PIR sensor and the buzzer, and the 3V3 pin of the board feeds the clock.")

    r.h2("Software Design of the Controller")
    r.p("The firmware is written in C++ in the Arduino environment and organised as a state machine rather "
        "than as a sequence of delays, so that the web server, the keypad, the clock, the PIR sensor and the "
        "BLE link are all serviced on every pass of the loop. The states are CONNECT, IDLE, GREETING, WELCOME, "
        "LEVEL, TIMETABLE, REENTRY, GOODBYE, WEEKEND and COOLDOWN. FreeRTOS tasks are used for the two "
        "activities that must not be starved: one task owns the file system and answers timetable lookups, and "
        "one task keeps the clock and the network time in step, each guarding its resource with a mutex.")
    r.p("The message that is sent to the panel is not a template. For each lookup the firmware reads the "
        "courses of the selected level and day, sorts them by starting time, and concatenates the course code, "
        "the time interval and the venue into one string separated by vertical bars, which the panel renders "
        "as a continuous scroll. The string is then converted to upper case, because the font of the panel has "
        "no lower case, and is checked against the 280-character limit before it is sent, so that a long day is "
        "reported to the administrator rather than silently truncated on the panel.")

    r.h2("System Block Diagram")
    r.p("Figure 3.3 shows the same system as a block diagram, which is the clearer view of the information "
        "flow. The ESP32 sits at the centre, with four inputs on its left: presence from the PIR sensor, the "
        "level from the keypad, and the time and day from the clock, the fourth being the timetable that "
        "arrives over Wi-Fi from the browser. On its right are the two outputs that are not the display: the "
        "flash memory in which the timetable is stored, and the buzzer. Above it, reached only by the BLE link, "
        "is the panel. Below it is the power arrangement, and the note on the diagram records the fact that the "
        "panel is not fed from it.")
    r.figure("fig3_3_block", "Block Diagram of the Motion-Activated LED Schedule Display", 6.6,
             "Information flow of the system. The display is the only block reached by radio, and it is the "
             "only block with a supply of its own.")

    r.h2("System Flowchart")
    r.p("Figure 3.4 is the operational flowchart. On power-on the ESP32 initialises the serial monitor, the "
        "file system, the I²C bus and the clock, the keypad, the buzzer and the PIR interrupt, then starts the "
        "Wi-Fi access point and the web server, and finally initialises its Bluetooth stack, connects to the "
        "panel and discovers the two characteristics it needs. If the connection fails the firmware waits and "
        "retries with a widening interval, and the panel continues to show whatever it held before. Once the "
        "link is up the system enters the IDLE state, in which a stationary HH:MM clock is sent to the panel "
        "and refreshed only when the minute changes.")
    r.p("A session begins on a rising edge from the PIR sensor or on a wake command from the web page. The "
        "firmware greets the reader according to the hour, using GOOD MORNING from 05:00 to 11:59, GOOD "
        "AFTERNOON from 12:00 to 16:59 and GOOD EVENING at all other times, or WELCOME if the clock has not "
        "been set; the greeting is followed by the welcome message and by the level prompt. A level entered on "
        "the keypad is confirmed with #, whereupon the classes of that level for the current day are read from "
        "the timetable file and streamed to the panel. A fifteen-second re-entry window follows, during which "
        "* returns the system to a fresh entry; otherwise the closing message is sent and the system waits ten "
        "seconds before it will start another session. An entry that is not completed within forty-five "
        "seconds produces the NO ENTRY message. On a Saturday or a Sunday the level prompt is skipped and the "
        "weekend message is shown instead.")
    r.figure("fig3_4_flowchart", "Operational Flowchart of the System", 4.9,
             "The state machine of the controller, from power-on through the idle clock to a session and back. "
             "The web server is serviced on every pass of the loop, so an upload is applied between messages.")

    r.table("State Table of the Controller", [
        ["State", "Panel shows", "Keypad", "Buzzer", "Next state"],
        ["CONNECT", "Last stored message", "Ignored", "Silent", "IDLE when the BLE link is up"],
        ["IDLE", "Stationary HH:MM clock", "Ignored", "Silent", "GREETING on a PIR edge or a wake command"],
        ["GREETING", "GOOD MORNING / AFTERNOON / EVENING", "Only *", "Beep on acceptance", "WELCOME after 6 s"],
        ["WELCOME", "WELCOME TO ELECTRICAL, then the level prompt", "Only *", "Beep", "LEVEL after the message"],
        ["LEVEL", "ENTER LEVEL 100-500 THEN PRESS #", "Digits, # and *", "Beep on an accepted key", "TIMETABLE on #, GOODBYE after 45 s"],
        ["TIMETABLE", "Classes of the level and day", "Only *", "Beep", "REENTRY after the message"],
        ["REENTRY", "PRESS * TO RE-ENTER LEVEL", "* only", "Beep", "GOODBYE after 15 s"],
        ["GOODBYE", "Closing message", "Ignored", "Silent", "COOLDOWN after the message"],
        ["WEEKEND", "NO LECTURES TODAY", "Ignored", "Silent", "COOLDOWN after the message"],
        ["COOLDOWN", "Stationary clock", "Ignored", "Silent", "IDLE when the restart gate has passed"],
    ], [1200, 2350, 1250, 1500, 1900], font=15)

    r.h2("Summary of the Design")
    r.p("This chapter has presented the analysis behind every part of the system. The ESP32 was chosen because "
        "it can be a Bluetooth client and a Wi-Fi access point at the same time, and its pins were allocated "
        "around the fixed functions of the I²C bus, the strapping pins and the input-only pins. The display is "
        "a 64 × 20 iPixel panel with its own controller, reached over a BLE link whose MTU, fragment pause and "
        "message limit were chosen so that a full day of classes is transferred in a fraction of a second. The "
        "panel carries its own controller and its own flash memory, shares the 5 V rail of the project, and "
        "is connected to the rest of the system for data by radio alone. The clock, the sensor, the keypad and the buzzer "
        "were shown to interface to the controller without level shifting or external resistors, and the "
        "controller side was shown to draw about 0.26 A at 5 V, which a 4 000 mAh cell supports for "
        "approximately nine hours through the boost stage of the module. Chapter Four reports the construction "
        "of the unit, the tests performed on it and the agreement between these calculations and the "
        "measurements.")
