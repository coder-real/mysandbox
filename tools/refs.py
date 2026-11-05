"""References and the appendix listing."""

REFERENCES = [
    "Analog Devices. (2015). DS3231 extremely accurate I²C-integrated RTC/TCXO/crystal: Data sheet. "
    "Analog Devices, Inc. https://www.analog.com/media/en/technical-documentation/data-sheets/ds3231.pdf",

    "Bluetooth SIG. (2023). Bluetooth Core Specification, Version 5.4. Bluetooth Special Interest Group. "
    "https://www.bluetooth.com/specifications/specs/core-specification-5-4/",

    "cagcoach. (2024). iPIXEL LED matrix Bluetooth protocol documentation [Source code documentation]. "
    "GitHub. https://github.com/cagcoach/ha-ipixel-color",

    "Espressif Systems. (2023). ESP32 technical reference manual (Version 5.1). Espressif Systems. "
    "https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf",

    "Futagami, T. (2024). Passive infrared sensing for presence detection in indoor environments. Journal of "
    "Sensor Technology, 12(3), 145–158.",

    "Hercog, D., Lerher, T., Truntič, M., & Težak, O. (2023). Design and implementation of ESP32-based IoT "
    "devices. Sensors, 23(15), 6739. https://doi.org/10.3390/s23156739",

    "Ifeagwu, E. N. (2025). Design and implementation of a Wi-Fi enabled digital notice board using the ESP32 "
    "microcontroller. International Journal of Engineering Research and Technology, 14(4), 112–119.",

    "Krebs, S., & Herter, T. (2024). Ultra-wideband positioning system based on ESP32 and DWM3000 modules. "
    "arXiv preprint.",

    "Margapuri, V. (2020). Smart motion detection system using PIR sensors. arXiv preprint.",

    "Mashrur, R. (2025). Motion operated LED lighting using Arduino and a passive infrared sensor. "
    "International Journal of Advanced Research in Science, Communication and Technology, 11(3), 249–257.",

    "Ogunseye, T. T., Egbeyale, G. B., Bello, A. K., & Ajani, S. A. (2021). Design and construction of a "
    "microcontroller-based electronic moving message display. arXiv preprint.",

    "Ranasinghe, J., & Herath, D. (2023). IoT-based automatic counter for detecting student flow using PIR and "
    "ultrasonic sensors. ResearchGate publication. https://www.researchgate.net/publication/368750968",

    "Sanap, V. C., Nikam, S., Sail, V., Thorat, S., & Vidhate, A. (2025). Design and implementation of real "
    "time clock using RTC DS3231 and Arduino Uno. International Journal for Research in Applied Science and "
    "Engineering Technology, 13(2), 1545–1551. https://doi.org/10.22214/ijraset.2025.67162",

    "Sarkar, S., Jana, A., Maity, S., Maiti, C., & Bera, C. K. (2023). IoT-based performance display system "
    "using ESP32: Design and development. Journal of Physics: Conference Series, 2576(1), 012002. "
    "https://doi.org/10.1088/1742-6596/2576/1/012002",

    "Sulartopo, S., Wiraditama, W., Candra, D., & Nugraha, A. P. (2023). Motion detection security system "
    "based on ESP32 and PIR sensor. Jurnal Teknologi Informasi dan Komunikasi, 14(2), 395–401. "
    "https://doi.org/10.51903/jtikp.v14i2.779",

    "Triwahyuni, N., & Beta, S. (2022). Running text information system design internet-based for small "
    "outlets. JAICT: Journal of Applied Information and Communication Technologies, 7(2), 97–101. "
    "https://doi.org/10.32497/jaict.v7i2.3270",

    "Vales, V. B., Bolaño, T. D., Fernández, O. C., García-Naya, J. A., & Escudero, C. J. (2024). Fine time "
    "measurement for the Internet of Things: A practical approach using ESP32. arXiv preprint.",

    "yyewolf. (2025). go-ipxl: A Go library for controlling iPixel Color LED displays over Bluetooth Low "
    "Energy [Source code]. GitHub. https://github.com/yyewolf/go-ipxl",

    "Zaghlool Mahmood, R. (2022). High accurate automatic school bell controller based on ESP32 Wi-Fi. "
    "Technium Romanian Journal of Applied Sciences and Technology, 4(10), 126–144. "
    "https://doi.org/10.47577/technium.v4i10.7929",
]

APPENDIX_INTRO = [
    "The program listed below is the firmware of the completed unit, as uploaded to the ESP32. It is written in "
    "C++ for the Arduino IDE with the ESP32 Arduino core, and it is reproduced in full so that the behaviour "
    "described in Chapters Three and Four can be checked against the code that produced it.",
    "The sketch includes two auxiliary files that belong to the same project but are not listed here, because "
    "they contain large constant tables rather than program logic. The first, eee_assets.h, holds the "
    "compressed dashboard page served at the root address, the character font from which the display glyphs "
    "are built, and the sample departmental timetable that is installed if no timetable file is found. The "
    "second, idle_clock.h, holds the packet that draws the stationary clock on the panel. Both files must "
    "accompany the sketch when it is compiled.",
    "The listing is given one statement per paragraph, with the indentation of the original.",
]
