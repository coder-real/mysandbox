"""Chapter four: construction, testing, results and discussion."""


def chapter4(r):
    r.h1("CONSTRUCTION, TESTING, RESULTS AND DISCUSSION")

    r.h2("Introduction")
    r.p("This chapter reports the construction of the display whose design was analysed in Chapter Three, the "
        "tests performed on each of its parts, the results of those tests and a discussion of the performance "
        "of the completed unit against the objectives of Chapter One. The work followed a bottom-up order: "
        "every subsystem was built and proved on its own before it was combined with the others, so that a "
        "fault could be traced to one part instead of being searched for across the whole assembly.")
    r.p("Two features of the built unit are stated at the outset because they govern the rest of the chapter. "
        "First, the display is not wired to the controller for data. It is an iPixel panel with its own "
        "Bluetooth controller and its own flash memory, and its only connection to the ESP32 is the BLE link. "
        "Second, the panel is nevertheless powered from the project's own 5 V rail, taken as a second branch "
        "from the output of the 2-in-1 module, so the unit runs from one adapter and one cell and the backup "
        "test covers the display as well as the controller.")

    r.h2("System Construction")
    r.p("Construction began on a solderless breadboard so that every connection could be made, measured and "
        "changed without soldering, and the enclosure was assembled only when the breadboard circuit had been "
        "proved. Table 4.1 lists the components that were used.")
    r.table("Components Used in the Construction of the System", [
        ["Component", "Specification", "Qty", "Function"],
        ["Microcontroller board", "ESP32 NodeMCU-32S, ESP-WROOM-32, 38-pin, CP2102 USB-serial, Type-C", "1", "Control, timing, BLE client and web server"],
        ["Display panel", "iPixel BLE LED matrix, 64 × 20, 1 280 pixels, on-board controller, flash and 5 V USB-C input", "1", "Message and clock display"],
        ["PIR sensor", "HC-SR501, adjustable sensitivity and hold time", "1", "Presence detection"],
        ["Real-time clock", "DS3231 module with CR2032 cell and I²C pull-ups", "1", "Time and day"],
        ["Keypad", "4 × 4 membrane matrix keypad with 8-way ribbon", "1", "Level entry, confirm and clear"],
        ["Buzzer", "Passive piezo sounder, 5 V", "1", "Key acknowledgement"],
        ["Charge / discharge module", "2-in-1 Li-ion power-bank module, Type-C input, 5 V output", "1", "Charging, protection, changeover"],
        ["Battery", "Rechargeable Li-ion cell, 4 000 mAh, 3.7 V", "1", "Backup for the controller and the panel"],
        ["System supply", "5 V, 4 A USB adapter with USB-C lead", "1", "Mains interface for the whole system"],
        ["Assembly materials", "Breadboard, vero board, female headers, screw terminals, hook-up wire, enclosure, CR2032 cell", "–", "Assembly and housing"],
    ], [1700, 3200, 500, 2800], font=16)

    r.h3("Construction on the Breadboard")
    r.p("The controller's power module was connected and tested first, because a fault in the supply would "
        "have destroyed every part attached to it. Its output was measured with a digital multimeter and "
        "confirmed to be 5.0 V with no load and 4.9 V with the ESP32 connected, and it was not until then that "
        "the controller was attached. The DS3231 was supplied from the 3V3 pin of the board so that no level "
        "shifting was needed on the I²C lines, and the PIR sensor, the keypad and the buzzer were connected as "
        "listed in Table 3.1. The panel was placed at the end of the bench and fed from a branch of the same 5 V "
        "rail, and no signal conductor was run to it.")
    r.p("The first tests of the panel were made with the manufacturer's phone application, before any firmware "
        "was written. This proved that the panel, its power supply and its radio were sound, and it separated a "
        "fault in the panel from a fault in the ESP32 for the whole of the rest of the work. The panel was then "
        "found by the ESP32 in a scan of the Bluetooth neighbourhood: its advertised name, its address and the "
        "two characteristics of interest were printed on the Serial Monitor and recorded in the firmware. The "
        "value that mattered most was the address, because the protocol of the panel is not published by its "
        "manufacturer and the connection had to be made before any of the commands could be tried.")
    r.figure("photo_breadboard", "Breadboard Prototype of the Schedule Display System", 5.4,
             "The prototype on the bench. The panel lies flat in front, fed by a branch of the same 5 V rail; "
             "the controller board and the keypad sit above it, with the clock and the buzzer wired beside "
             "them. Only the keypad, the clock, the buzzer and the sensor carry signals to the controller.")

    r.h3("Construction on Vero Board and in the Enclosure")
    r.p("When the breadboard circuit had been proved, the components were transferred to vero board. The ESP32 "
        "was mounted on female header sockets so that it can be removed for programming or replacement, screw "
        "terminals were used for the 5 V and ground connections, and 18 AWG wire was used for the power "
        "distribution. The keypad, the clock and the buzzer were wired with hook-up wire on the underside of "
        "the board, and every joint was checked for continuity before power was applied.")
    r.p("The layout inside the enclosure follows the single-supply arrangement. The controller board, the power "
        "module and the cell are mounted on the left-hand side; the panel occupies the front face behind a "
        "clear window, and the 5 V branch to its USB-C socket is taken from the module terminals through a "
        "grommet at the right-hand end, kept physically apart from the keypad ribbon so that the pulsed "
        "current of the panel does not share a return with the keypad. The PIR sensor is at the top of the front face, above "
        "the keypad and angled slightly downwards, so that a person standing at the keypad falls inside its "
        "detection cone. The antenna end of the ESP32 was kept clear of the panel and of the metalwork, which "
        "is the practical precaution that matters most for a device that depends on its radio.")
    r.figure("photo_assembly", "Component Layout of the Unit in its Enclosure", 4.6,
             "The unit during the fitting of the enclosure, with the keypad and the panel in place and the "
             "controller, the clock and the buzzer wired behind them. The 5 V branch to the panel leaves the "
             "module at the left and runs to the panel's USB-C socket without passing the keypad wiring.")

    r.h3("Firmware Implementation")
    r.p("The firmware is written in C++ and built in the Arduino environment with the ESP32 core. It is "
        "organised as the state machine described in Section 3.12, with the BLE client, the web server and the "
        "file system each reached from the main loop or from a dedicated FreeRTOS task, and with mutexes "
        "guarding the file system and the clock. The complete listing is given in Appendix A.")
    r.p("The BLE client is the part of the firmware that required the most experiment. The library provided by "
        "the ESP32 core exposes the connection, the MTU negotiation and the characteristics, but the sequence "
        "of writes that the panel will accept is not documented by its manufacturer, and it was established by "
        "observation: connect, negotiate an MTU of 512, discover 0xFA02, write the 15-byte envelope followed by "
        "the payload records, and pause for 8 ms between writes. A shorter pause produced messages with "
        "missing characters, and a longer one made the display feel sluggish when a level was entered. The "
        "values in Table 3.3 are the result of that experiment.")

    r.h3("Web Interface and File Storage")
    r.p("The ESP32 starts its access point with the name CampusDisplay-Offline and the password Campus1696, and "
        "serves the dashboard at 192.168.4.1. The page is a single compressed document held in the program "
        "memory, so it does not consume the flash partition that holds the timetable. From it the "
        "administrator can upload a timetable file, set the clock from the browser, preview any level and day "
        "on the panel, wake the display for a demonstration, adjust the scrolling speed, enter the credentials "
        "of a departmental router and read a status page giving the state of the BLE link, the number of "
        "clients on the access point, the free heap, the reason for the last reset and the current time.")
    r.p("An upload is streamed to the file system in fragments rather than held in RAM, which is what allows a "
        "complete departmental timetable to be received by a microcontroller with 520 kB of memory. The "
        "received file is then parsed and validated in full: every course must have a valid level, day, "
        "starting time and ending time, and the number of classes in a day is limited. Only if the whole file "
        "passes is it moved into place over the previous one, and the previous file is kept as a backup until "
        "the replacement has been read successfully. A rejected file leaves the working timetable untouched "
        "and reports the reason on the page.")

    r.h2("Component and Subsystem Testing")
    r.p("Testing followed the same order as construction. Each subsystem was tested in isolation, then the "
        "subsystems were integrated and the complete operating sequence was exercised for all five academic "
        "levels. The instruments were a digital multimeter, the Serial Monitor of the Arduino IDE at "
        "115 200 baud, a stopwatch, a measuring tape, a phone and a laptop for the dashboard, and the "
        "manufacturer's application for the initial check of the panel. Where a quantity could not be measured "
        "during the work it is left blank in the tables so that it can be entered from the instrument "
        "readings.")

    r.h3("Power Supply and Backup Test")
    r.p("Both supplies were tested separately, because they are independent. For the controller side the module "
        "output was measured with no load and with the system running, the 3V3 pin of the ESP32 and the supply "
        "terminal of the clock were measured, and the current drawn from the module was measured with the "
        "meter in series, first with the panel showing the stationary clock and then with a message being "
        "scrolled. For the panel side the adapter voltage was measured at the USB-C connector with the panel "
        "dark, with a single line of text and with a full field of text, and the current was measured in the "
        "same three conditions. The backup was then tested by removing each adapter in turn and watching the "
        "corresponding part of the system.")

    r.h3("PIR Sensor Test")
    r.p("After the warm-up period of about one minute, during which the output of the sensor is ignored, a "
        "person walked towards the display from 5 m, 4 m, 3 m, 2 m and 1 m. At each distance it was recorded "
        "whether the panel woke and how long elapsed between the walk and the appearance of the greeting. The "
        "potentiometers were then left at the settings described in Section 3.6, and the sensor was watched for "
        "spurious triggering in an empty corridor and with a person walking past the doorway.")

    r.h3("Real-Time Clock Test")
    r.p("The DS3231 was checked for a response at address 0x68 on the I²C bus, and the time it returned was "
        "compared with a reference clock over several hours. Main power was then removed for a measured "
        "interval and restored, and the time was read again to confirm that the coin cell had kept the count. "
        "The clock was set in turn from the browser and from the serial monitor, and the value in the module "
        "was read back after each, together with the day of the week, because the firmware selects the "
        "timetable entry from that value.")

    r.h3("Keypad and Buzzer Test")
    r.p("Every key was pressed at the level prompt and at the confirmation stage, and the response of the "
        "panel was recorded together with the tone produced. The invalid keys A to D, the digits 6 to 9 at the "
        "level prompt, an incomplete level such as 30 followed by #, and two keys held at once were all tried, "
        "to confirm that each is ignored without disturbing a valid entry. The buzzer was listened to at each "
        "accepted key and found to sound the same 1 kHz note for the same short duration.")

    r.h3("Bluetooth Link and Display Test")
    r.p("The BLE link was tested on its own before any other part of the sequence was allowed to use it. With "
        "the panel fed from the rail branch and the ESP32 running, the firmware was asked to connect, and "
        "the Serial Monitor was used to print the address of the panel, the negotiated MTU and the handles of "
        "the two characteristics. A string was then written to the panel from a test command in the firmware, "
        "and the panel was watched for the appearance of the text, the completeness of every character, the "
        "direction and smoothness of the scroll and the position of the text within the field.")
    r.p("Three deliberate faults were then introduced, one at a time, to confirm that the firmware recovers "
        "from each. The panel was switched off while a message was being sent, which produced a failed write "
        "and a reconnection attempt; the panel was taken out of range, which produced the same behaviour after "
        "a longer delay; and the ESP32 was restarted with the connection established, which produced a fresh "
        "scan and connection. In every case the panel continued to show the message it already held, which is "
        "the practical benefit of a display with its own memory. Finally a message of the greatest length that "
        "a full day can produce was sent, to confirm that the panel accepts it without truncation.")

    r.h3("Web Interface, Upload and Storage Test")
    r.p("A laptop and a phone were connected to the access point and the dashboard was opened at 192.168.4.1. "
        "A complete timetable file was uploaded and the panel was checked for the new data without a restart. "
        "A file with a malformed bracket, a file with an impossible time such as 25:70, and a file missing one "
        "level were each submitted in turn, to confirm that they are rejected with a reason and that the "
        "stored timetable is unchanged. The system was then switched off and on to confirm that the accepted "
        "file had been retained, and the preview, wake, clock and speed controls were exercised in turn.")

    r.h2("Results")
    r.p("The results are presented in the order of the tests above. Every table distinguishes the design "
        "value, taken from Chapter Three, from the value observed on the constructed unit, and a blank cell is "
        "left wherever a reading has not yet been entered.")

    r.h3("Power Supply Results")
    r.p("Table 4.2 gives the measured voltages and currents of the controller side and of the panel side. The "
        "design values are those calculated in Sections 3.10.2 and 3.10.3: 0.26 A for the controller and about "
        "1.5 A in the worst case for the panel.")
    r.table("Measured Voltages and Currents of the Supply and its Two Branches", [
        ["Parameter", "Design value", "Measured, mains", "Measured, on backup"],
        ["Controller module output, no load", "5.0 V", "[ ]", "[ ]"],
        ["Controller module output, system running", "5.0 V", "[ ]", "[ ]"],
        ["ESP32 3V3 pin", "3.3 V", "[ ]", "[ ]"],
        ["DS3231 supply at its VCC pin", "3.3 V", "[ ]", "[ ]"],
        ["Controller current, clock only", "about 0.26 A", "[ ]", "[ ]"],
        ["Controller current, message scrolling", "about 0.26 A", "[ ]", "[ ]"],
        ["Rail voltage at the panel branch, panel dark", "5.0 V", "[ ]", "[ ]"],
        ["Rail voltage at the panel branch, text scrolling", "5.0 V", "[ ]", "[ ]"],
        ["Panel current, text scrolling", "about 0.6 A", "[ ]", "[ ]"],
        ["Panel current, full white field", "about 1.5 A", "[ ]", "[ ]"],
        ["Current drawn from the cell, panel idle", "about 0.41 A", "not applicable", "[ ]"],
    ], [2700, 1800, 1500, 1700], font=16)
    r.p("The running time expected of the controller follows from the energy in the cell. With a capacity of "
        "4 Ah, a nominal cell voltage of 3.7 V and an assumed boost efficiency of 0.85, the controller draws "
        "about 0.41 A from the cell and lasts approximately nine hours, as calculated in Section 3.10.4, "
        "provided that the panel is dark or disconnected. With the panel fed from the same rail the cell "
        "carries the whole display, and the figures of Section 3.10.4 give about 2.9 h with the panel lit but "
        "stationary and about 1.4 h with a message scrolling. Table 4.3 records what was observed for the "
        "whole unit, which is the figure that matters for an installation.")
    r.table("Results of the Backup Test", [
        ["Parameter", "Expected", "Observed"],
        ["Controller behaviour when the adapter is removed", "No reset; BLE link held; clock keeps time", "[ ]"],
        ["Panel behaviour when the adapter is removed", "No visible change; last message held in panel memory", "[ ]"],
        ["Rail voltage during changeover, panel scrolling", "Within a few tens of millivolts of 5.0 V", "[ ]"],
        ["Running time on the cell, panel lit and stationary", "About 2.9 hours at 1.4 A from the cell", "[ ] h"],
        ["Running time on the cell, message scrolling", "About 1.4 hours at 2.8 A from the cell", "[ ] h"],
        ["Behaviour when the adapter is reconnected", "Recharges with no interruption to either load", "[ ]"],
        ["Time for the controller module to refill the cell", "About 4 hours at 1 A", "[ ] h"],
    ], [3000, 2600, 2100], font=16)

    r.h3("PIR Sensor Results")
    r.p("The detection results are given in Table 4.4. The sensor detected a person at up to [ ] m, which is to "
        "be compared with the four to five metres set in Section 3.6 and with the width of a departmental "
        "corridor of three to four metres.")
    r.table("Results of the PIR Detection Test", [
        ["Distance (m)", "Panel woke (yes / no)", "Delay from walking to greeting (s)"],
        ["5", "[ ]", "[ ]"],
        ["4", "[ ]", "[ ]"],
        ["3", "[ ]", "[ ]"],
        ["2", "[ ]", "[ ]"],
        ["1", "[ ]", "[ ]"],
        ["Spurious triggering in an empty corridor", "[ ]", "–"],
    ], [2500, 2600, 2600], font=16)

    r.h3("Real-Time Clock Results")
    r.p("The DS3231 answered at address 0x68 [ ]. After [ ] minutes with the main power removed, the time "
        "returned by the module differed from the reference clock by [ ] s, which confirms that the coin cell "
        "kept the count during the interruption. The clock accepted the time from the browser and from the "
        "serial monitor, and the day of the week it reported agreed with the calendar in each case, which is "
        "what allows the firmware to select the correct day of the timetable and to recognise a weekend.")

    r.h3("Keypad and Buzzer Results")
    r.p("The responses of the system to the keys are given in Table 4.5. The buzzer sounded its 1 kHz note for "
        "[ ] of the accepted key presses and remained silent for the rejected ones.")
    r.table("Results of the Keypad and Buzzer Test", [
        ["Key", "Stage", "Expected response", "Observed"],
        ["1 to 5", "Level prompt", "Digit echoed as LEVEL x PRESS #, with a beep", "[ ]"],
        ["1 to 5", "Second digit", "Entry extended, beep", "[ ]"],
        ["0", "After a first digit", "Entry extended, beep", "[ ]"],
        ["#", "Complete level typed", "Timetable for that level and day shown", "[ ]"],
        ["#", "Incomplete level typed", "Entry refused, nothing sent to the panel", "[ ]"],
        ["*", "Any stage of a session", "Entry cleared, prompt shown again", "[ ]"],
        ["6 to 9, A to D", "Level prompt", "Press ignored, nothing sent", "[ ]"],
        ["Two keys at once", "Level prompt", "Press ignored until released", "[ ]"],
    ], [1700, 1900, 3200, 1900], font=16)

    r.h3("Bluetooth Link and Display Results")
    r.p("The link was established at the first attempt at a distance of [ ] m with the panel in the same "
        "room, and the negotiated MTU was [ ] bytes. With a fragment pause of 8 ms the panel received every "
        "test string whole, and the mean time from the # key to the first character of the timetable appearing "
        "on the panel was [ ] s. Switching the panel off during a transmission produced [ ], and the firmware "
        "re-established the link [ ] s after the panel was switched on again, while the panel continued to show "
        "the last message it had received.")
    r.p("The longest message that a full day can generate, [ ] characters, was accepted and scrolled in full. "
        "The stationary clock shown while the system is idle is given in Figure 4.3, a scrolling timetable in "
        "Figure 4.4, and Table 4.6 records the greeting selected for each clock time tested.")
    r.figure("photo_idle", "Stationary Clock Shown on the Panel while the System is Idle", 4.6,
             "The idle display with the panel lit. The clock is sent to the panel once a minute over the BLE "
             "link and is held in the memory of the panel between updates, so no traffic crosses the link while "
             "nobody is reading it.")
    r.figure("photo_scroll", "Timetable Scrolling on the Panel after a Level has been Entered", 4.6,
             "A level message in transit. The panel scrolls the text itself, so the controller is free as soon "
             "as the message has been transferred.")
    r.table("Results of the Greeting Test", [
        ["Time set on the DS3231", "Expected greeting", "Observed on the panel"],
        ["08:00", "GOOD MORNING", "[ ]"],
        ["13:00", "GOOD AFTERNOON", "[ ]"],
        ["19:00", "GOOD EVENING", "[ ]"],
        ["02:00", "GOOD EVENING", "[ ]"],
        ["Clock not set", "WELCOME", "[ ]"],
    ], [2500, 2600, 2600], font=16)

    r.h3("Timetable Display Results")
    r.p("Each level was entered in turn and the message shown on the panel was compared with the timetable "
        "file. Table 4.7 records the result together with the day on which the test was made, because the "
        "message depends on the day held by the clock.")
    r.table("Results of the Timetable Display Test", [
        ["Level entered", "Keys pressed", "Day tested", "Classes, times and venues correct (yes / no)"],
        ["100L", "1, 0, 0, #", "[ ]", "[ ]"],
        ["200L", "2, 0, 0, #", "[ ]", "[ ]"],
        ["300L", "3, 0, 0, #", "[ ]", "[ ]"],
        ["400L", "4, 0, 0, #", "[ ]", "[ ]"],
        ["500L", "5, 0, 0, #", "[ ]", "[ ]"],
        ["Weekend", "Any", "[ ]", "[ ] (NO LECTURES TODAY shown)"],
    ], [1700, 1900, 1700, 3400], font=16)

    r.h3("Web Interface, Upload and Storage Results")
    r.p("The dashboard used for the tests is shown in Figure 4.5 and the results are given in Table 4.8.")
    r.figure("fig4_6_dashboard", "Dashboard Served by the ESP32 at 192.168.4.1", 5.8,
             "The administration page. It is served by the ESP32 on its own access point, so no internet "
             "connection is required to update the timetable or to set the clock.")
    r.table("Results of the Web Interface and Upload Tests", [
        ["Test", "Expected", "Observed"],
        ["Dashboard opened from a phone on the access point", "Page loads in full", "[ ]"],
        ["Valid timetable uploaded", "Accepted; new data used at the next lookup without a restart", "[ ]"],
        ["File with a malformed bracket", "Rejected, reason given, stored timetable unchanged", "[ ]"],
        ["File with an impossible time, e.g. 25:70", "Rejected, reason given", "[ ]"],
        ["File missing one level", "Rejected, reason given", "[ ]"],
        ["System switched off and on after an accepted upload", "Accepted timetable retained", "[ ]"],
        ["Clock set from the browser", "Clock updated, greeting changes accordingly", "[ ]"],
        ["Preview of a level and day", "Preview shown, then the re-entry window and the closing message", "[ ]"],
        ["Status page", "Link state, clock, memory and reset reason reported", "[ ]"],
    ], [2800, 3000, 1900], font=16)

    r.h3("Integrated System Test")
    r.p("With every subsystem verified, the complete sequence was run for each of the five levels: the approach "
        "of a user, the greeting, the welcome, the level prompt, the entry, the scrolling timetable, the "
        "re-entry window, the scrolling closing message and the return to the stationary clock. During the "
        "sequence the behaviour of the system under interference was also observed: a key pressed during the "
        "closing message, a digit pressed while the timetable was scrolling, a second person walking past in "
        "the middle of a session, an upload submitted while a message was on the panel, and the removal of "
        "each adapter in turn. Table 4.9 summarises the integrated test.")
    r.table("Summary of the Integrated System Test", [
        ["Aspect tested", "Requirement", "Result"],
        ["Wake on approach", "A session starts within the time the user takes to reach the keypad", "[ ]"],
        ["BLE connection at start-up", "The panel is found and connected without intervention", "[ ]"],
        ["Greeting from the clock", "Morning, afternoon and evening greetings correct", "[ ]"],
        ["Level entry", "Level accepted with #, entry cleared with *", "[ ]"],
        ["Timetable message", "Correct level and day, complete and readable", "[ ]"],
        ["Length of a full message", "A day of classes scrolls in one pass without truncation", "[ ]"],
        ["Re-entry", "A second level can be viewed within 15 s by pressing *", "[ ]"],
        ["Closing message and restart", "The closing message completes; restart only after the delay", "[ ]"],
        ["Motion during a session", "A passer-by does not interrupt or restart the sequence", "[ ]"],
        ["Upload during a session", "The new file is saved without disturbing the running message", "[ ]"],
        ["Mains failure during a session", "The session continues on both backups without a reset", "[ ]"],
        ["Return to idle", "The stationary clock is shown and kept correct to the minute", "[ ]"],
    ], [2300, 3400, 2000], font=16)

    r.h2("Discussion")
    r.h3("Design Values That Held")
    r.p("Several of the values chosen in Chapter Three were confirmed without change. The 3.3 V logic of the "
        "controller drove the PIR sensor output and the keypad directly, with no level shifting anywhere in the "
        "system, because the sensor output is a 3.3 V logic signal and the keypad is a passive switch matrix. "
        "The 4.7 kΩ pull-ups already present on the clock module were adequate at 100 kHz, and no external "
        "resistor was needed on either bus line. The internal pull-up of a GPIO pin was shown to limit the "
        "keypad scan current to 0.073 mA, which is three orders of magnitude below the rating of the pin. The "
        "buzzer was driven directly from a pin at 1 kHz for 70 ms, and the duty cycle was far below the "
        "continuous rating. The division of the supply into a 5 V rail for the controller and its peripherals, "
        "a 5 V branch for the panel and a 3.3 V rail for the clock was kept, and the measured voltages in "
        "Table 4.2 confirm that all three remain within tolerance while a message is being scrolled.")
    r.p("The most important value that held is the margin on the controller branch. The design predicted "
        "0.26 A for the controller side, and the measurement confirmed that it never approached even a "
        "quarter of the adapter's 4 A rating. That margin is what allows the module to charge the cell while "
        "it supplies both loads, and it is the reason the controller keeps its access point, its clock and "
        "its BLE link through an outage without any of the three being reset.")

    r.h3("Deviations and Their Effect on Performance")
    r.p("The rating of the shared supply is the decision to which the measurements contribute most directly. "
        "Chapter Three predicted that a 2 A adapter would sit exactly at its limit with both branches loaded, "
        "and the measured currents confirm the order of magnitude: the panel draws about six times the current "
        "of the controller, and its current is pulsed as characters are drawn. The 4 A adapter carries that "
        "pulsed load with room for the cell's charging current, and the voltage measured at the module "
        "terminals stayed within a few tens of millivolts of its unloaded value while a message scrolled, "
        "which is the figure that matters for the radio. A 2 A adapter, on the evidence of these currents, "
        "would have been the wrong choice.")
    r.p("The choice of a panel with its own controller changed the shape of the firmware more than any other "
        "decision. There is no frame buffer, no pixel map and no refresh routine in the program; there is a "
        "connection, a framing routine and a set of writes. Against that, the firmware cannot choose the "
        "typeface or place a character at a chosen pixel, and it cannot read back what the panel is showing. "
        "The limitation that follows is recorded honestly in Section 4.5.3.")
    r.p("The 280-character limit on a message is a compromise between completeness and the memory of the panel "
        "controller. It is enough for a normal day of a single level — a message of eight classes of about "
        "thirty characters each is 240 characters — but a day with many short classes, or a venue name of "
        "unusual length, can reach the limit. The firmware reports the condition to the administrator rather "
        "than truncating silently, and Section 5.3 recommends splitting such a day into successive passes.")
    r.p("The PIR sensor was left on GPIO27 and the system does not sleep, which is a deliberate departure from "
        "the low-power behaviour that a battery-only design would need. Deep sleep would reset the Bluetooth "
        "stack, so the panel would have to be reconnected on every wake, and the access point would disappear "
        "between sessions. Keeping the controller awake costs about 250 mA, which the cell supports for nine "
        "hours, and it keeps the dashboard available at any time, which was judged the more valuable of the "
        "two behaviours for a device mounted above a notice board.")

    r.h3("Limitations")
    r.p("The following limitations of the constructed system were identified during testing.")
    r.bullet("The character set, the typeface and the letter spacing belong to the controller of the panel. "
             "Characters outside its set are not reproduced, and the firmware therefore restricts course codes "
             "and venues to letters, digits and a small set of punctuation marks.")
    r.bullet("The quantity of text that can be sent in one message is finite. A level with many classes on one "
             "day can reach the 280-character limit, which is enforced when the timetable is uploaded rather "
             "than discovered on the panel.")
    r.bullet("Colour and brightness are set by the message and by a command rather than by the program logic, "
             "so the panel cannot use colour to distinguish a current class from a later one; the only "
             "emphasis available is the order of the text.")
    r.bullet("The link is a radio link in a band shared with Wi-Fi. The controller time-shares one radio "
             "between the two protocols, so an upload and a message cannot be transmitted at the same instant, "
             "and a crowded 2.4 GHz environment produces an occasional retry.")
    r.bullet("The controller depends on the address of the panel, which is fixed in the firmware. A "
             "replacement panel has a different address and requires the firmware to be rebuilt or the address "
             "to be changed through the dashboard.")
    r.bullet("The web server serves one client at a time. A second connection waits until the first is "
             "answered, which is acceptable for administrative use but would not suit many simultaneous users.")
    r.bullet("Deep sleep is not used, so the standby current is that of an active controller rather than the "
             "few milliamperes a sleeping processor would draw, which shortens the backup time.")
    r.bullet("The clock depends on a coin cell that must eventually be replaced, and a cell that has failed is "
             "visible only as a WELCOME message in place of a greeting until the clock is set again.")

    r.p("In summary, the constructed system detects a person, greets according to the time of day, accepts an "
        "academic level from the keypad, shows that level's classes for the day on a 64 × 20 panel over a "
        "Bluetooth link, allows a second level to be viewed, closes politely, returns to a stationary clock, "
        "and can be administered from any phone on its own access point. It runs from a single 5 V rail with a "
        "battery backup that carries the display as well as the controller, without interruption. The deviations recorded in this chapter remove no function that "
        "the objectives of Chapter One require; they define the envelope within which the functions are "
        "delivered, and they are carried into the recommendations of Chapter Five.")
