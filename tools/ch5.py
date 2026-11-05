"""Chapter five: summary, conclusion and recommendations."""


def chapter5(r):
    r.h1("SUMMARY, CONCLUSION AND RECOMMENDATIONS")

    r.h2("Summary")
    r.p("This project set out to design and construct a motion-activated, real-time interactive LED "
        "departmental schedule display for the Department of Electrical and Electronics Engineering, Joseph "
        "Sarwuan Tarka University, Makurdi. The system is built around an ESP32 microcontroller that drives a "
        "64 × 20 iPixel Bluetooth Low Energy LED matrix, an HC-SR501 passive infrared sensor for presence "
        "detection, a DS3231 real-time clock for date and time, a 4 × 4 matrix keypad for level entry and a "
        "passive buzzer for acknowledgement, and a rechargeable 5 V supply that feeds the controller and the "
        "panel from the same rail.")
    r.p("The work began with a review of the technology used in displays of this kind, followed by the "
        "electrical analysis and design of every subsystem: the choice of controller and the allocation of its "
        "pins, the panel and the Bluetooth link to it, the sensor interface, the clock and its bus pull-ups, "
        "the keypad scan, the buzzer driver, and the power arrangement with its battery backup. The "
        "design was then constructed in stages and tested subsystem by subsystem before the parts were "
        "integrated.")
    r.p("In the constructed unit the display is an independent peripheral. The panel carries its own "
        "controller and its own flash memory, it is powered from the project's 5 V rail, and it is reached by "
        "the ESP32 over a Bluetooth Low Energy GATT link: the controller writes to characteristic 0xFA02, receives "
        "acknowledgements on 0xFA03, and streams the characters of each message as bitmap tiles. No conductor "
        "runs between the controller and the panel. The same ESP32 publishes a Wi-Fi access point at "
        "192.168.4.1, from which an administrator can upload a new departmental timetable, set the clock, "
        "preview any level and day, trim the scrolling period and read the status of the system, and it holds "
        "the timetable as a validated JSON file in its flash memory. A session is started by motion: the "
        "display greets according to the time of day, welcomes the student, prompts for an academic level, "
        "shows that level's classes for the current day, offers a second level for fifteen seconds and closes "
        "with the names of the designers before returning to a stationary clock. On a weekend the timetable is "
        "replaced by a message that there are no lectures.")

    r.h2("Conclusion")
    r.p("The three objectives set out in Chapter One were examined one by one against the behaviour of the "
        "completed unit.")
    r.p("The first objective was to design a motion-activated display, built on the ESP32 with a 64 × 20 LED "
        "matrix, a passive infrared detector and a DS3231 real-time clock, in which the matrix is addressed "
        "over a Bluetooth Low Energy link. The objective was met. The panel shows a stationary clock until the "
        "HC-SR501 detects a person, at which point a session begins; the greeting and the day of the timetable "
        "are taken from the time and date held in the clock; and the whole message is rendered on a field of "
        "1 280 pixels by the controller inside the panel. The link is a radio link and nothing else, which is "
        "the arrangement described in Chapter Three and drawn in Figures 3.1 and 3.2, and the design values of "
        "the link and of both supplies were confirmed by measurement in Chapter Four.")
    r.p("The second objective was to develop an interactive interface that lets a student filter the timetable "
        "by academic level on the keypad, and an administrator update the timetable without touching the unit. "
        "The objective was met. The student enters a level as three digits, confirms with # and may correct "
        "the entry with *; during the re-entry window a second level can be viewed without repeating the "
        "sequence. The administrator reaches the dashboard from any phone or laptop on the access point that "
        "the ESP32 itself creates, and from there uploads a complete validated timetable, sets the clock, "
        "previews any level and day and reads the state of the system. Because the access point is created by "
        "the device, none of this depends on the department having an internet connection.")
    r.p("The third objective was to make the system operate reliably and continuously through persistent "
        "storage and a rechargeable battery with automatic changeover. The objective was met for the "
        "controller, and met on a different basis for the panel. The timetable and the scrolling calibration "
        "are held in flash memory and survive the loss of power; an accepted timetable replaces the previous "
        "one only after full validation; and the charge and discharge module transfers the controller to its "
        "cell without a relay and without a break in operation, and because the panel is fed from the same "
        "rail it is carried through the same changeover. The objective is therefore met for the whole "
        "display on one battery, with the qualification that the running time is set by the heavier load: "
        "about 2.9 hours with the panel lit and about 1.4 hours while a message scrolls, against the nine "
        "hours that the controller alone would give.")
    r.p("Taken together, the work shows that a single low-cost microcontroller, a Bluetooth LED panel, a "
        "passive infrared sensor, a real-time clock and one battery-backed supply can replace a printed "
        "notice board with a display that is legible across a corridor, aware of the time and day, filtered to "
        "the student's own level, updateable from a phone and unaffected by the power interruptions that are "
        "routine in Makurdi. It also shows where the limits of such a build lie: in the character set and the "
        "single colour of an inexpensive panel, in the 280 characters that the panel's memory will hold in one "
        "message, and in the dependence of the whole design on a radio link that shares its band with Wi-Fi. "
        "Each of those limits is a candidate for the further work recommended below.")

    r.h2("Recommendations")
    r.p("The following recommendations arise from the construction, the tests and the limitations recorded in "
        "Chapter Four, and are offered for any continuation of this work.")
    r.bullet("Panel discovery in place of a fixed address: The address of the panel is at present written into "
             "the firmware, so a replacement panel needs a rebuild. The firmware should scan for the "
             "LED_BLE_ prefix, present the panels it finds on the dashboard and store the chosen one in "
             "Preferences, so that a panel can be exchanged in the field without a computer.")
    r.bullet("A supervised connection with a visible state: The link is re-established with a widening back-off "
             "but nothing tells the reader that the panel is out of contact. A heartbeat message, and an "
             "indicator on the dashboard giving the age of the last successful write, would turn a silent "
             "failure into a reported one.")
    r.bullet("Splitting a long day into successive passes: The panel holds about 280 characters in one message. "
             "A day with many classes should be sent as two or three successive messages, or in order of "
             "starting time so that the next class appears first, instead of being rejected at upload.")
    r.bullet("Removal of classes that have finished: The panel shows the whole day, whereas the student "
             "standing in front of it usually wants the next class. Because the real-time clock is already "
             "present, the firmware could omit the classes whose end time has passed, which would make the "
             "display a real-time aid rather than a copy of the timetable.")
    r.bullet("A larger energy store, and a measured figure for the display as a whole: The single 4 000 mAh "
             "cell gives about nine hours with the controller alone, but only about three hours with the "
             "panel lit, because the panel draws roughly six times the current of the controller. A "
             "larger cell, or two cells in parallel within the rating of the module, would restore the longer "
             "backup time at a cost in mass and in charging time. Both figures should be measured rather than "
             "calculated.")
    r.bullet("Low-power standby that keeps the display: The system does not sleep, because sleep would reset "
             "the Bluetooth stack. A study should be made of a scheme in which the connection is re-established "
             "on waking while the panel keeps its last message, which would extend the backup time without "
             "blanking the display.")
    r.bullet("A protected administrative interface: The access point is protected by a fixed password and the "
             "dashboard has no notion of a user. A changing password, or a confirmation step before a timetable "
             "is replaced, would reduce the risk of interference with a device mounted in a public corridor.")
    r.bullet("A timetable editor that produces the upload file: The JSON file must at present be written by hand "
             "or in a text editor. A small editor, either a page served by the ESP32 or a spreadsheet template "
             "that exports the same structure, would remove the commonest source of rejected uploads.")
    r.bullet("A printed copy of the timetable beside the display: The display depends on a file that is "
             "maintained by a person. Until the departmental timetable office accepts responsibility for "
             "keeping that file current, a printed copy should remain beside the display as a fallback, and the "
             "two should be reconciled at the start of every semester.")
    r.bullet("Field installation and long-term observation: The unit was tested on a bench. It should be "
             "installed above the departmental notice board for at least one semester, with the number of "
             "detections, the number of sessions and the state of the coin cell recorded, so that the "
             "detection range, the timeout of the entry prompt and the life of the coin cell are settled by "
             "observation rather than by estimate.")
