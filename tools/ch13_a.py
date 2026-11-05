"""Chapters one to three of the corrected report: re-architected around a BLE iPixel panel."""


def chapter1(r):
    r.h1("INTRODUCTION")

    r.h2("Background of the Study")
    r.p("The effective dissemination of lecture schedules, course details and venue information is essential "
        "to the smooth academic progress of students in any higher education institution. In university "
        "departments across Nigeria, including those in Benue State, the traditional method of publishing "
        "lecture timetables has remained largely unchanged for decades: a printed sheet of paper is pinned to "
        "a departmental notice board at the beginning of each semester and is expected to serve for the whole "
        "term. That method suffers from poor visibility, rapid deterioration in a humid climate, and the "
        "difficulty of making a correction once the sheet has been printed and posted.")
    r.p("Modern embedded systems now make a better arrangement affordable. The ESP32 microcontroller combines "
        "a dual-core processor, ample flash memory and a 2.4 GHz radio that can act as either a Wi-Fi station "
        "or a Bluetooth Low Energy (BLE) peer, and it costs less than a printed banner. A passive infrared "
        "(PIR) sensor can start a display only when somebody is present, and a DS3231 real-time clock keeps "
        "the correct time and day without any network connection. On the display side, the class of LED "
        "matrix panels sold with an on-board Bluetooth controller (the iPixel family) has removed the "
        "difficult part of the problem: the panel stores the message, generates the characters and performs "
        "the scrolling itself, so the host has only to send a short string of text over a wireless link.")
    r.p("This project brings those parts together. A 64 × 20 iPixel BLE matrix is used as the display, and the "
        "ESP32 addresses it as a Bluetooth Low Energy client. The same ESP32 publishes a Wi-Fi access point "
        "of its own, on which a departmental administrator can open a web page and upload a new timetable "
        "without touching the unit and without any internet connection. A 4 × 4 keypad lets a student select "
        "an academic level, a passive buzzer acknowledges the entry, and a rechargeable lithium-ion supply "
        "keeps the controller alive during the mains interruptions that are routine in Makurdi. The result is "
        "a display that is legible across a corridor, aware of the time and day, filtered to the student's own "
        "level, and updateable from a phone.")
    r.p("The work proceeds in the conventional order. The technologies involved are reviewed first, then each "
        "subsystem is analysed electrically and its component values are justified, then the prototype is "
        "constructed and tested subsystem by subsystem, and finally the completed system is evaluated against "
        "the objectives set out below.")

    r.h2("Statement of the Problem")
    r.p("The Department of Electrical and Electronics Engineering, like most departments of Joseph Sarwuan "
        "Tarka University, Makurdi, communicates its lecture timetable on printed paper pinned to a notice "
        "board. The sheet is read by students of five academic levels, each of whom has to scan the whole "
        "departmental timetable to find the few classes that concern them. The paper fades and tears, a change "
        "of venue or time requires a reprint and a walk to the board, and the display is unreadable from the "
        "far end of the corridor. Electronic alternatives are rarely adopted because a screen that has no "
        "backup supply simply goes blank during the frequent outages in the region, and because a display that "
        "must be reprogrammed on the spot to change a timetable is no easier to administer than paper.")
    r.p("There is therefore a need for a departmental schedule display that is large and clearly visible, that "
        "shows the correct information for the current day and hour without intervention, that lets a student "
        "see only the classes of his or her own level, that can be updated remotely over a network the device "
        "creates itself, that wakes only when somebody is present to read it, and that continues to run while "
        "the mains supply is interrupted.")

    r.h2("Aim of the Study")
    r.p("The aim of this study is to design and construct a motion-activated, real-time interactive LED "
        "departmental schedule display in which an ESP32 microcontroller drives a 64 × 20 iPixel Bluetooth Low "
        "Energy LED matrix and also serves the web page from which the timetable is maintained.")

    r.h2("Objectives of the Study")
    r.p("The specific objectives of this study are:")
    r.p("To design a motion-activated LED departmental schedule display using an ESP32 microcontroller and a "
        "64 × 20 iPixel BLE LED matrix addressed over a Bluetooth Low Energy link, with PIR-based presence "
        "detection and a DS3231 real-time clock for automatic, time-correct display.", first_indent=False)
    r.p("To develop an interactive interface through which a student filters the timetable by academic level on "
        "a 4 × 4 keypad, and through which an administrator uploads a new timetable to a web page served by "
        "the ESP32 on its own Wi-Fi access point, sets the clock and inspects the state of the system.",
        first_indent=False)
    r.p("To ensure reliable and continuous operation through persistent storage of the timetable in ESP32 flash "
        "memory and a rechargeable lithium-ion backup supply that changes over automatically when the mains "
        "fails.", first_indent=False)

    r.h2("Significance of the Study")
    r.p("The project demonstrates that a schedule display of this class can be built from parts that are "
        "available in any Nigerian electronics market, and that the difficult parts of the problem — driving a "
        "large matrix, keeping time, and publishing a web page — are all handled by inexpensive modules. For "
        "the department, the display removes the printing and posting of timetables, allows a correction to be "
        "published from a phone in a minute, and keeps working during an outage. For students, it turns a "
        "single departmental timetable into five level-specific messages that can be read from several metres "
        "away. For the wider field, it is a documented example of a Bluetooth-controlled display driven by a "
        "microcontroller that also serves its own configuration interface, which is the arrangement most "
        "low-cost campus displays will use as the panels become cheaper.")

    r.h2("Scope of the Study")
    r.p("The system is built around an ESP32 NodeMCU-32S development board. The display is an iPixel LED matrix "
        "of 64 columns by 20 rows, that is 1 280 pixels, with an on-board Bluetooth Low Energy controller, an "
        "internal flash memory in which messages are stored, and a USB-C socket through which it is powered. "
        "The panel is addressed as a BLE peripheral: the ESP32 scans for it, connects as a client, discovers "
        "the write characteristic at 0xFA02 and the notify characteristic at 0xFA03, and streams the "
        "characters of the message to it. No signal conductor runs between the ESP32 and the panel. The panel is "
        "powered from the 5 V rail of the project itself, through a branch taken from the output of the "
        "lithium-ion module to its USB-C socket; it is not fed from the 5V or 3V3 pin of the ESP32 board, "
        "because it draws about 1.5 A when it is showing a message and no pin of the board can supply that.")
    r.p("A PIR sensor (HC-SR501) on GPIO27 detects a person and starts a session. A DS3231 real-time clock with "
        "a CR2032 backup cell keeps Nigerian local time, UTC+1, and communicates over I²C on GPIO21 and "
        "GPIO22. A student enters a level of 100L to 500L on a 4 × 4 matrix keypad, whose rows are GPIO13, "
        "GPIO12, GPIO14 and GPIO33 and whose columns are GPIO32, GPIO26, GPIO25 and GPIO19; the # key "
        "confirms an entry, the * key clears it, and a passive buzzer on GPIO15 acknowledges every accepted "
        "key. The timetable itself is a JSON file held in the LittleFS partition of the ESP32 and validated "
        "before it replaces the previous file. It is uploaded through a web page served by the ESP32 at "
        "192.168.4.1 on its own access point; the ESP32 may also be joined to a departmental router as a "
        "client, which supplies network time, but no function of the display depends on that router.")
    r.p("The controller is supplied from a 5 V USB adapter through a 2-in-1 lithium-ion charge and discharge "
        "module holding a 4 000 mAh cell, which changes the load over to the cell without a relay when the "
        "mains fails. The system holds the complete weekly timetable of five levels for one department, shows "
        "the classes of one level and one day as a single scrolling message of up to 280 characters, and is "
        "intended for indoor use in a corridor or above a departmental notice board.")


def chapter2(r):
    r.h1("LITERATURE REVIEW")

    r.h2("Theoretical Framework")
    r.p("The design of this display rests on four bodies of knowledge: short-range wireless communication in "
        "the form of Bluetooth Low Energy, matrix LED display modules that accept text rather than pixels, "
        "embedded web servers running on a microcontroller, and battery-backed power conversion. Each is "
        "reviewed below in the form in which it is used in this project, followed by the empirical studies "
        "from which the design decisions were taken.")

    r.h3("Bluetooth Low Energy and the GATT Profile")
    r.p("Bluetooth Low Energy is a short-range radio protocol operating in the 2.4 GHz industrial, scientific "
        "and medical band. Unlike the original Bluetooth, which holds a connection open with a fixed slot "
        "structure, BLE is built for intermittent transfer: a device advertises its presence on three "
        "dedicated channels, a client connects to it, and the two then exchange packets at a negotiated "
        "connection interval that may be as short as 7.5 ms and as long as four seconds. The data themselves "
        "are organised in the Generic Attribute Profile (GATT), in which a server exposes services, each "
        "service contains characteristics, and each characteristic carries a value that a client may read, "
        "write, or subscribe to by notification (Bluetooth SIG, 2023).")
    r.p("Three properties of BLE matter for a display of this kind. The first is that the protocol is "
        "asymmetric: the panel is the server, holding the characteristics, and the ESP32 is the client, so all "
        "commands travel as writes to a single characteristic and any acknowledgement arrives as a "
        "notification. The second is that the maximum length of a single write is fixed by the negotiated "
        "Maximum Transmission Unit (MTU); a default MTU of 23 bytes leaves 20 bytes of payload, whereas an MTU "
        "of 517 leaves 514, which is why a long message must be fragmented and why the MTU is negotiated at "
        "connection. The third is that BLE shares the 2.4 GHz band with Wi-Fi, so a device that runs both, as "
        "the ESP32 does here, must time-share a single radio between the two protocols and will show "
        "occasional latency when both are busy.")

    r.h3("iPixel Bluetooth Low Energy LED Matrix Panel")
    r.p("The display used in this project belongs to the family of flexible LED matrix panels sold under the "
        "iPixel Color application and its rebrands. The panel is a printed circuit board carrying 1 280 "
        "addressable RGB LEDs in 20 rows of 64, a controller that holds a font, a frame buffer and a small "
        "flash memory, and a Bluetooth Low Energy transceiver. It is not a pixel-addressable matrix in the "
        "sense of a HUB75 panel or a WS2812B chain: the host sends a character string, and the controller "
        "renders it, stores it in one of nine message slots and scrolls it across the field at a speed supplied "
        "with the message. The panel used here is the HRP-1696, the 64 × 20 member of the family: its active "
        "area is 12.59 × 3.15 inches (320 × 80 mm), it is built on a flexible substrate, and the protocol "
        "identifies its size class by a type byte in the device information, which for the 64 × 20 unit "
        "reports the 1 280-pixel field (cagcoach, 2024). It is supplied at 5 V through a USB-C socket and "
        "draws up to 2 A when the whole field is lit, which in this project is taken from the same 5 V rail "
        "that feeds the controller.")
    r.p("The protocol spoken by the panel has been documented by the community that reverse-engineered it. The "
        "service is 0x00FA; commands are written to characteristic 0xFA02 and acknowledgements and replies "
        "arrive on 0xFA03, which the client enables by writing 0x0100 to its client configuration descriptor. A "
        "message is framed as a 16-bit little-endian length, a 16-bit command, a 32-bit payload length, a "
        "32-bit CRC of the payload, a slot number and a group of display parameters, followed by the payload "
        "itself, which for text is a run of 20-byte records describing successive eight-column tiles of the "
        "rendered bitmap (yyewolf, 2025; cagcoach, 2024). Brightness is a five-byte command, power is another, "
        "and the device reports its panel size, firmware version and whether it also carries a Wi-Fi module "
        "when the appropriate query is sent.")
    r.p("Two consequences follow for this project. Because the controller owns the font, the character set and "
        "the scroll, the firmware cannot choose a typeface or place a character at an arbitrary pixel, and the "
        "colour of the text is set by the message rather than by the program. Because the whole message is "
        "uploaded before it is displayed, the length of a message is limited by the memory of the controller "
        "rather than by the patience of the reader, which is why the firmware of this project refuses a "
        "message longer than 280 characters.")
    r.figure("photo_panel", "iPixel 64 × 20 Bluetooth Low Energy LED Matrix Panel", 5.6,
             "The panel used in this project. The matrix is 64 columns by 20 rows, and the 5 V input is taken "
             "from the USB-C socket at the left-hand end by a branch of the project rail.")

    r.h3("ESP32 Microcontroller")
    r.p("The ESP32 is a system-on-chip designed by Espressif Systems around a dual-core Xtensa LX6 processor "
        "running at up to 240 MHz, with 520 kB of static RAM, a flash memory of 4 MB or more on the module, "
        "and a single 2.4 GHz radio that serves both Wi-Fi (802.11 b/g/n) and Bluetooth Low Energy. It "
        "provides 34 general-purpose input and output pins, of which some are reserved for flash memory, some "
        "are input-only, and a few determine the boot mode at reset. Its peripherals include two independent "
        "I²C controllers, several serial and SPI controllers, a CAN controller and a rich set of timers "
        "(Espressif Systems, 2023). The display of this project uses none of them, because the panel is "
        "addressed over the radio, and only the I²C controller and the GPIO pins are used by the rest of the "
        "system.")
    r.p("The dual-core architecture is directly useful here. One task can hold the BLE connection and stream "
        "the message to the panel, a second can run the web server and the file system, and the main loop can "
        "scan the keypad and watch the PIR sensor, without any one of them blocking the others for longer than "
        "a few milliseconds. The same radio serving both protocols is the principal constraint of the design, "
        "because a Wi-Fi upload and a BLE transmission cannot proceed at the same instant; the firmware "
        "therefore handles web requests between messages rather than during one.")
    r.table("Key Parameters of the ESP32 Module Used in the Design", [
        ["Parameter", "Value"],
        ["Processor", "Dual-core Xtensa LX6, up to 240 MHz"],
        ["Static RAM", "520 kB"],
        ["Flash memory", "4 MB on the module, shared by program and LittleFS"],
        ["Wi-Fi", "802.11 b/g/n, 2.4 GHz, access point and station"],
        ["Bluetooth", "Bluetooth 4.2 Low Energy, GATT client and server"],
        ["GPIO", "34 pins, 3.3 V logic, 12 mA continuous per pin"],
        ["I²C / serial / SPI controllers", "2 / 3 / 4"],
        ["Supply", "5 V at the VIN pin, 3.3 V regulated on board"],
        ["Active current", "about 250 mA with the radio transmitting, 0.15 mA in deep sleep"],
    ], [2600, 6100])
    r.figure("photo_esp32", "ESP32 NodeMCU-32S Development Board", 3.4,
             "The ESP32 development board used as the controller. The antenna end is kept clear of the power "
             "module and of the panel wiring so that the radio is not shadowed.")

    r.h3("Passive Infrared Motion Sensor (HC-SR501)")
    r.p("A passive infrared sensor detects the change in infrared radiation that occurs when a warm body moves "
        "across its field of view. The HC-SR501 module pairs a pyroelectric element with a Fresnel lens that "
        "divides the field into alternating zones, so that a person walking past produces a sequence of "
        "positive and negative transitions at the element. The module contains its own comparator, a "
        "monostable that holds the output high for a settable time of about three seconds to five minutes, and "
        "two potentiometers, one for sensitivity and one for the hold time. Its output is a 3.3 V logic signal "
        "that can be taken directly to a microcontroller pin (Mashrur, 2025).")
    r.p("The sensor is used here only to start a session, so its hold time is set to its minimum and the "
        "duration of the session is controlled by the firmware. Its sensitivity is set so that a person "
        "approaching the display is detected at about four metres, which is the width of the corridor in which "
        "the unit is intended to be mounted, while movement in the adjacent room is not.")
    r.figure("photo_pir", "HC-SR501 Passive Infrared Motion Sensor", 2.9,
             "The PIR module, showing the Fresnel dome, the two adjustment potentiometers and the three-pin "
             "header for supply, ground and output.")

    r.h3("DS3231 Real-Time Clock")
    r.p("The DS3231 is a temperature-compensated real-time clock. It contains a 32.768 kHz crystal, a "
        "temperature sensor and compensation circuitry that trims the oscillator, so that the time it keeps "
        "drifts by about two minutes a year at room temperature, far better than the few minutes a month of an "
        "uncompensated clock. It communicates over I²C at address 0x68, holds seconds, minutes, hours, day, "
        "date, month and year in binary-coded decimal, accounts for leap years up to 2100, and can raise an "
        "alarm at a programmed time. The module used here carries the chip, a CR2032 coin cell that keeps it "
        "running when the system is switched off, and 4.7 kΩ pull-up resistors on the two bus lines (Analog "
        "Devices, 2015).")
    r.p("The display depends on this device for two things: the greeting, which changes at noon and at five "
        "o'clock, and the day of the week, by which the timetable entry is selected and by which a weekend is "
        "recognised. Because the clock is read once a second and the module answers in well under a "
        "millisecond, the bus is not a bottleneck, and because the coin cell keeps the count during an outage "
        "the system comes back with the correct time even after the main battery has been exhausted.")
    r.figure("photo_rtc", "DS3231 Real-Time Clock Module", 3.4,
             "The DS3231 module. The coin cell holder is on the upper face and the six-pin header exposes the "
             "I²C lines, the square-wave output and the supply pins.")

    r.h3("4 × 4 Matrix Keypad")
    r.p("A matrix keypad arranges sixteen switches at the intersections of four rows and four columns, which "
        "reduces the number of conductors from seventeen to eight. The microcontroller drives one column low at "
        "a time, holds the rows high through internal pull-up resistors, and reads the rows; the row that goes "
        "low while a column is driven identifies the key. Only one column is driven at a time so that two keys "
        "pressed together cannot connect an output to ground, and the scan is filtered in time so that the "
        "contact bounce of a membrane keypad, which lasts ten to twenty milliseconds, is not read as several "
        "presses (Ifeagwu, 2025).")
    r.p("In this project the keypad carries the only input that the student provides: three digits of the "
        "academic level, confirmed with # and cleared with *. It is deliberately not used for administering the "
        "timetable, because a departmental timetable contains far more text than sixteen keys can conveniently "
        "enter; that is done on the web page described below.")
    r.figure("photo_keypad", "4 × 4 Matrix Membrane Keypad", 2.9,
             "The membrane keypad used for level entry, with the eight-way ribbon that connects it to the "
             "ESP32.")

    r.h3("Wi-Fi Access Point and Embedded Web Server")
    r.p("The ESP32 can act as a Wi-Fi access point in its own right: it beacons a network name, allocates "
        "addresses through its own DHCP server, and answers at 192.168.4.1 by default. A web server running on "
        "the microcontroller can therefore serve a page to any phone or laptop within range without a router, "
        "an internet connection or a cloud service. The same radio can also be joined to an existing network "
        "as a client, in which case the page becomes reachable from that network and the device can take its "
        "time from a network time server, while the access point continues to operate (Triwahyuni & Beta, "
        "2022).")
    r.p("This arrangement suits a departmental corridor, where the institutional network may be absent for "
        "days. The administrator walks up with a phone, joins the network that the display publishes, opens "
        "the page and uploads the new timetable file. The page is stored compressed in the program memory of "
        "the ESP32 and the upload is streamed to the file system in fragments, so that a complete departmental "
        "timetable can be received without holding it in RAM. The uploaded file is parsed and validated in "
        "full before it replaces the working copy, so that a mistake made in a text editor cannot destroy a "
        "timetable that is in use.")

    r.h3("Backup Power for the Two Loads")
    r.p("The system contains two loads that must survive an outage. The controller, the sensor, the keypad and "
        "the buzzer together draw about a quarter of an ampere at 5 V. The display panel draws roughly six "
        "times that, and although it is a self-contained unit with its own controller and flash memory, it is "
        "fed from the same rail as everything else. The design therefore uses one supply for the whole system: "
        "a 5 V, 4 A adapter with a 2-in-1 lithium-ion charge and discharge module and a 4 000 mAh cell, from "
        "whose output two branches are taken, one to the controller side and one to the USB-C socket of the "
        "panel.")
    r.p("Sharing the rail has three advantages. One adapter and one mains lead serve the whole display, which "
        "is what a unit mounted on a corridor wall requires. The cell then carries the display as well as the "
        "controller, so a message already on the panel and the timetable held in the controller both survive "
        "an outage together instead of one outliving the other. And the rail is loaded predictably, at about "
        "1.9 A in the worst case against a 4 A adapter, so the pulsed current of a scrolling message is drawn "
        "from a supply with real headroom rather than from one at its limit. The cost is that the backup time "
        "of the whole display is set by the heavier load, the panel, and is therefore shorter than the "
        "controller alone would give; the figures are calculated in Section 3.10.4 and measured in Section "
        "4.4.2.")

    r.h2("Conceptual Framework")
    r.p("The system is organised as an input–process–output arrangement of five subsystems coordinated by a "
        "state machine on the ESP32. The inputs are human presence from the PIR sensor, the time and day from "
        "the DS3231, the academic level from the keypad, and the timetable file uploaded over the access "
        "point. The process is the lookup of the classes of that level and day in the timetable file, their "
        "formatting into a single string of course code, time and venue, and the transmission of that string "
        "over the Bluetooth Low Energy link. The output is the scrolling message on the panel. The power "
        "subsystem underpins all of it, providing 5 V to the controller, the sensor and the buzzer, 3.3 V to "
        "the clock, and a separate 5 V supply to the panel.")
    r.p("Two boundaries in this framework deserve emphasis because they shape every other decision. The first "
        "is the boundary between the controller and the panel, which is a radio link and therefore carries no "
        "power and no ground: the ESP32 can say what the panel should show, but it cannot sense whether the "
        "panel is lit, and it must recover from a lost connection by itself. The second is the boundary "
        "between the panel and the departmental timetable, which is the panel controller's own font and "
        "scroll: the firmware decides the words and the order, but the typeface, the letter spacing and the "
        "speed of the scroll belong to the panel. The design is honest about both boundaries, and the "
        "limitations they impose are recorded in Chapter Four.")

    r.h2("Review of Related Empirical Studies")
    r.p("Hercog et al. (2023) examined the design of ESP32-based devices for the industrial internet of things "
        "and reported that the dual-core architecture allows communication and control tasks to run "
        "concurrently without measurable interference. Their measurements of task latency informed the "
        "division of work in this project between the BLE task, the web server and the main loop.")
    r.p("Ogunseye et al. (2021) constructed a microcontroller-driven moving-message display and showed that an "
        "LED matrix is an effective replacement for a printed notice board in an institution, but their unit "
        "required a physical connection to change the message. The absence of a wireless update route is the "
        "gap that the access point of this project fills.")
    r.p("Zaghlool Mahmood (2022) combined an ESP32 with a DS3231 to automate a school bell, and demonstrated "
        "that a compensated real-time clock is accurate enough to drive a schedule without a network. The "
        "present design borrows that arrangement, and adds the display of the schedule itself rather than only "
        "the signalling of its moments.")
    r.p("Sarkar et al. (2023) built an IoT performance display around the ESP32 and reported that the "
        "microcontroller can render a display and serve a network at the same time provided that the display "
        "work is delegated to a driver rather than performed pixel by pixel in the main loop. The iPixel panel "
        "used here takes that delegation to its limit, since the panel performs the rendering as well.")
    r.p("Ranasinghe and Herath (2023) and Sulartopo et al. (2023) both used PIR sensors with an ESP32 for "
        "presence detection, and both reported reliable detection at ranges of three to five metres with few "
        "false events when the sensor was mounted at head height and away from a window. The mounting "
        "arrangement and the sensitivity setting adopted in Chapter Three follow their experience.")
    r.p("Margapuri (2020) compared PIR detection with other low-cost presence methods and concluded that the "
        "passive infrared sensor remains the cheapest reliable option for indoor use, at the cost of "
        "insensitivity to a person who is stationary. That limitation is acceptable here because the display "
        "is read by somebody who has just walked up to it.")
    r.p("Mashrur (2025) demonstrated motion-operated LED lighting and quantified the energy saved by lighting "
        "only when a person is present. The same argument applies to the session structure of this project, in "
        "which the panel leaves its stationary clock and shows a timetable only after a detection.")
    r.p("Ifeagwu (2025) described a Wi-Fi-enabled digital notice board in which content is pushed from a "
        "browser to an ESP32, and emphasised that the absence of a separate server is what makes such a board "
        "affordable and maintainable. The access point and the embedded page of this project follow the same "
        "principle.")
    r.p("Triwahyuni and Beta (2022) reported a running-text information system for small businesses in which "
        "the text is edited over a local network and displayed on a scrolling panel. Their work is the closest "
        "published relative of the present design, and it differs in two respects that matter: their panel was "
        "wired to the controller, and their text was entered rather than looked up from a validated timetable.")
    r.p("Vales et al. (2024) and Krebs and Herter (2024) explored time synchronisation and ranging with the "
        "ESP32 radio, and their results are a reminder that the 2.4 GHz radio is a shared resource whose "
        "behaviour changes when two protocols are used at once. That observation shaped the decision to keep "
        "web traffic out of the middle of a BLE transmission.")
    r.p("Sanap et al. (2025) documented the interfacing of a DS3231 to a microcontroller in detail, including "
        "the pull-up requirement of the I²C bus and the handling of the coin cell, and their treatment is used "
        "in Section 3.7 below.")

    r.h2("Summary of Literature Review")
    r.p("The literature establishes four points. The ESP32 is a capable host for a display that must also serve "
        "a network, provided that the rendering is delegated. A compensated real-time clock makes a schedule "
        "display independent of the network. Passive infrared detection is a cheap and reliable way to start a "
        "display only when it is needed. And embedded web servers on the microcontroller have made the "
        "wireless update of a display's content an ordinary rather than an exotic feature.")
    r.p("The gap that remains is one of combination and of medium. The published campus displays either wire "
        "the panel to the controller, or drive a pixel-addressable matrix whose rendering the controller must "
        "perform itself, or update their content from a cloud service. None of the studies reviewed drives a "
        "commercially available Bluetooth LED matrix from an ESP32 that simultaneously publishes the page from "
        "which the timetable is maintained, and none validates the uploaded timetable before it is used. The "
        "present work addresses that combination, and documents the engineering consequences of putting the "
        "display behind a radio link rather than behind a wire.")
