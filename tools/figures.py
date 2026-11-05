"""Generate the technical figures for the Bluetooth/iPixel report."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

OUT = os.path.dirname(os.path.abspath(__file__))
DPI = 200
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 8

INK = "#111111"
BLUE = "#1f4e79"
RED = "#a61b1b"
GREEN = "#1e6b3a"
GREY = "#5a5a5a"
FILL = "#eef2f7"
FILL2 = "#fdf3e7"
FILL3 = "#eaf4ec"


def new(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100 * h / w)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fill=FILL, edge=INK, fs=7.2, bold=False, lw=1.0, rad=0.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.35,rounding_size={rad}",
                                linewidth=lw, edgecolor=edge, facecolor=fill, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=INK, zorder=3, linespacing=1.45)
    return (x, y, w, h)


def arrow(ax, p1, p2, color=BLUE, style="-|>", lw=1.1, ls="-", rad=0.0, shrink=2):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=8, color=color,
                                 lw=lw, linestyle=ls, zorder=1,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=shrink, shrinkB=shrink))


def line(ax, pts, color=BLUE, lw=1.1, ls="-"):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, lw=lw, linestyle=ls, zorder=1, solid_capstyle="round")


def label(ax, x, y, t, fs=6.3, color=GREY, ha="center", va="center", rot=0, style="italic"):
    ax.text(x, y, t, fontsize=fs, color=color, ha=ha, va=va, rotation=rot,
            style=style, zorder=4)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", pad_inches=0.08,
                facecolor="white")
    plt.close(fig)
    print("wrote", path)


# ----------------------------------------------------------------------------- 3.1 block diagram
def block_diagram():
    fig, ax = new(11, 8.2)
    ax.set_xlim(-10, 100)
    ax.set_ylim(0, 74.5)

    # --- display
    box(ax, 30, 63, 40, 9.0,
        "iPixel BLE LED matrix\n64 x 20 pixels (1 280), on-board controller and flash\n"
        "USB-C 5 V input, fed from the project rail",
        fill=FILL3, edge=GREEN, fs=6.9)
    label(ax, 50, 73.3, "DISPLAY SUBSYSTEM", fs=6.8, color=GREEN)

    # --- controller
    box(ax, 30, 38, 40, 14.0,
        "ESP32  (NodeMCU-32S, ESP-WROOM-32)\n240 MHz dual core, 520 kB SRAM\n"
        "Wi-Fi 802.11 b/g/n  +  BLE 4.2 client\n"
        "state machine, timetable lookup, web server",
        fill=FILL, edge=BLUE, fs=6.9)
    label(ax, 50, 36.2, "PROCESSING AND CONTROL", fs=6.8, color=BLUE)

    # --- inputs
    box(ax, 2, 54, 23, 9, "HC-SR501\npassive infrared\npresence sensor", fill=FILL2, fs=6.7)
    box(ax, 2, 40.5, 23, 9, "4 x 4 matrix keypad\nacademic level entry\nconfirm and clear", fill=FILL2, fs=6.7)
    box(ax, 2, 27, 23, 9, "DS3231 RTC\nI2C address 0x68\nCR2032 backup", fill=FILL2, fs=6.7)

    # --- support and admin
    box(ax, 75, 54, 23, 9, "Phone or laptop\nbrowser, no internet\nAP 192.168.4.1", fill=FILL2, fs=6.7)
    box(ax, 75, 40.5, 23, 9, "LittleFS flash\n/eee_timetable.json\nvalidated upload", fill=FILL2, fs=6.7)
    box(ax, 75, 27, 23, 9, "Passive buzzer\nGPIO15\ntone 1 kHz, 70 ms", fill=FILL2, fs=6.7)

    # --- orthogonal connections
    def elbow(pts, color=BLUE):
        a = pts[0]
        for b in pts[1:-1]:
            line(ax, [a, b], color=color)
            a = b
        arrow(ax, a, pts[-1], color=color)

    elbow([(25, 58.5), (27.5, 58.5), (27.5, 50.0), (30, 50.0)])
    label(ax, 26.3, 54.2, "GPIO27", rot=90, fs=5.8)
    elbow([(25, 45.0), (30, 45.0)])
    label(ax, 27.5, 46.2, "8 GPIO", fs=5.8)
    elbow([(25, 31.5), (27.5, 31.5), (27.5, 42.0), (30, 42.0)])
    label(ax, 26.3, 36.6, "I2C", rot=90, fs=5.8)

    elbow([(75, 58.5), (72.5, 58.5), (72.5, 49.0), (70, 49.0)])
    label(ax, 73.7, 54.2, "Wi-Fi", rot=90, fs=5.8)
    elbow([(75, 45.0), (70, 45.0)])
    label(ax, 72.5, 46.2, "flash", fs=5.8)
    elbow([(64, 38), (64, 31.5), (75, 31.5)])
    label(ax, 63.2, 35.2, "GPIO15", rot=90, fs=5.8)

    # --- BLE link: the only path between ESP32 and panel
    arrow(ax, (50, 52), (50, 63), color=RED, lw=2.0, style="<|-|>")
    ax.text(51.6, 57.5, "Bluetooth Low Energy\n(BLE 4.2 GATT link)\n"
                        "write 0xFA02, notify 0xFA03\nadvertised as LED_BLE_xxxx",
            fontsize=6.2, color=RED, ha="left", va="center", fontweight="bold", linespacing=1.55)

    # --- power
    box(ax, 20, 7.0, 60, 13,
        "POWER SUBSYSTEM  (one rail for the whole system)\n"
        "5 V / 4 A USB adapter  ->  2-in-1 Li-ion charge / discharge module  ->  4 000 mAh cell\n"
        "two branches from the module output: control side (5 V, and 3V3 to the DS3231) and panel (5 V)",
        fill=FILL2, edge=GREY, fs=6.9)
    arrow(ax, (33, 20), (33, 38), color=GREY, lw=1.2, style="<|-|>")
    label(ax, 34.4, 29.0, "5 V and GND", ha="left", fs=6.1, style="normal", color=GREY)
    # second branch of the same rail up to the USB-C input of the panel
    elbow([(20, 16.5), (-5.0, 16.5), (-5.0, 67.5), (30, 67.5)], color=GREY)
    label(ax, -3.7, 43, "second 5 V branch of the same rail to the panel", rot=90, fs=5.9,
          color=GREY, style="normal")
    label(ax, 50, 4.4, "the panel and the controller share this rail; only data between them goes by radio",
          fs=6.1, color=GREY)

    save(fig, "fig3_1_block.png")


# ---------------------------------------------------------------------------- 3.2 circuit diagram
def circuit_diagram():
    fig, ax = new(11, 8.4)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 76.3)

    # ---------------- panel
    box(ax, 12, 64, 68, 10,
        "iPixel BLE LED matrix   64 x 20   (1 280 pixels; single colour, green, is used)\n"
        "on-board BLE controller and flash   |   GATT: write 0xFA02, notify 0xFA03\n"
        "USB-C 5 V input at the left end of the panel",
        fill=FILL3, edge=GREEN, fs=6.8)
    # 5 V branch from the project rail to the USB-C input of the panel
    ax.add_patch(Rectangle((82, 65.5), 16, 7, facecolor=FILL3, edgecolor=GREEN, lw=1.0, zorder=2,
                           linestyle=(0, (3, 2))))
    ax.text(90, 70.6, "5 V branch from", ha="center", fontsize=6.0, color=GREEN)
    ax.text(90, 67.6, "the module output", ha="center", fontsize=6.0, color=GREEN)
    arrow(ax, (82, 69), (80, 69), color=GREEN, lw=1.1, ls=(0, (3, 2)))

    # ---------------- ESP32
    ax.add_patch(Rectangle((33, 30), 34, 30, facecolor=FILL, edgecolor=BLUE, lw=1.4, zorder=2))
    ax.text(50, 56.6, "ESP32  NodeMCU-32S", ha="center", fontsize=8.2, fontweight="bold")
    ax.text(50, 54.4, "ESP-WROOM-32, 3.3 V logic", ha="center", fontsize=6.2, color=GREY)

    left_pins = [("GPIO27", 52.0), ("GPIO21", 46.0), ("GPIO22", 43.5),
                 ("GPIO13", 37.5), ("GPIO12", 35.2), ("GPIO14", 32.9)]
    for name, y in left_pins:
        ax.plot([30.5, 33], [y, y], color=INK, lw=0.9, zorder=3)
        ax.text(33.7, y, name, fontsize=5.9, va="center", color=INK)
    right_pins = [("GPIO15", 33.5), ("GPIO32", 44.0), ("GPIO26", 42.0),
                  ("GPIO25", 40.0), ("GPIO19", 38.0)]
    for name, y in right_pins:
        ax.plot([67, 69.5], [y, y], color=INK, lw=0.9, zorder=3)
        ax.text(66.3, y, name, fontsize=5.9, va="center", ha="right", color=INK)
    ax.plot([67, 69.5], [54.5, 54.5], color=BLUE, lw=1.2, zorder=3)
    ax.text(66.3, 54.5, "Wi-Fi", fontsize=5.9, va="center", ha="right", color=BLUE)

    for x, name in ((39, "5V"), (45, "GND"), (60, "3V3")):
        ax.plot([x, x], [30, 27.6], color=INK, lw=0.9, zorder=3)
        ax.text(x, 26.4, name, fontsize=5.9, ha="center", va="center", color=INK)

    # ---------------- radio link up to the panel
    arrow(ax, (24, 60.6), (24, 64), color=RED, lw=1.8, style="<|-|>")
    ax.text(29, 62.3, "BLE air interface, 2.4 GHz  -  text, brightness, power and clock commands",
            fontsize=6.1, color=RED, ha="left", va="center", fontweight="bold")

    # ---------------- left peripherals
    box(ax, 2, 47, 26, 9, "HC-SR501 PIR sensor\nVCC 5 V, OUT 3.3 V logic, GND", fill=FILL2, fs=6.4)
    line(ax, [(30.5, 52.0), (28, 52.0)], color=BLUE)

    box(ax, 2, 39, 26, 7.5, "DS3231 real-time clock\nSDA, SCL, VCC 3V3, GND", fill=FILL2, fs=6.4)
    line(ax, [(28, 45.0), (30.5, 45.0)], color=BLUE)
    line(ax, [(28, 42.6), (30.5, 42.6)], color=BLUE)

    box(ax, 2, 30, 26, 8, "4 x 4 matrix keypad\nrows R1-R4 to GPIO13, 12, 14, 33", fill=FILL2, fs=6.4)
    for y in (37.5, 35.2, 32.9):
        line(ax, [(28, y), (30.5, y)], color=BLUE)
    ax.text(2, 27.6, "row R4 and the four column lines C1-C4 are run to the right-hand\n"
                     "pins of the ESP32 as listed in Table 3.6.",
            fontsize=5.4, color=GREY, ha="left", va="top", style="italic", linespacing=1.5)

    # ---------------- right peripherals
    box(ax, 72, 50, 20, 8.5, "Phone or laptop browser\nAP 192.168.4.1, no internet", fill=FILL2, fs=6.4)
    line(ax, [(69.5, 54.5), (72, 54.5)], color=BLUE, ls=(0, (3, 2)))

    box(ax, 72, 30, 20, 7.5, "Passive buzzer\n+ to GPIO15, - to GND", fill=FILL2, fs=6.4)
    line(ax, [(69.5, 33.5), (72, 33.5)], color=BLUE)

    # keypad columns taken from the right-hand pins
    line(ax, [(70.6, 44.0), (70.6, 38.0)], color=BLUE, lw=1.0, ls=(0, (2, 1.6)))
    for y in (44.0, 42.0, 40.0, 38.0):
        line(ax, [(69.5, y), (70.6, y)], color=BLUE, lw=0.9)
    ax.text(71.4, 41.0, "keypad\nC1-C4", fontsize=5.2, color=BLUE, va="center", ha="left",
            style="italic", linespacing=1.4)

    # ---------------- power
    ax.add_patch(Rectangle((4, 6), 26, 10, facecolor=FILL2, edgecolor=GREY, lw=1.1, zorder=2))
    ax.text(17, 12.6, "5 V / 4 A USB adapter", ha="center", fontsize=7.0)
    ax.text(17, 9.0, "mains interface", ha="center", fontsize=6.0, color=GREY)

    ax.add_patch(Rectangle((38, 4.5), 34, 13, facecolor=FILL2, edgecolor=GREY, lw=1.1, zorder=2))
    ax.text(55, 14.4, "2-in-1 Li-ion charge / discharge module", ha="center", fontsize=7.0)
    ax.text(55, 11.0, "charger + boost converter + protection", ha="center", fontsize=6.0, color=GREY)
    ax.text(55, 7.6, "5 V output, 4 000 mAh Li-ion cell", ha="center", fontsize=6.0, color=GREY)
    line(ax, [(30, 11), (38, 11)], color=GREY, lw=1.2)
    ax.text(34, 12.2, "5 V in", fontsize=5.5, color=GREY, ha="center", style="italic")

    line(ax, [(39, 17.5), (39, 27.6)], color=GREY, lw=1.1)
    arrow(ax, (39, 27.6), (39, 30), color=GREY, lw=1.1)
    label(ax, 41.0, 19.6, "branch 1: 5 V to the ESP32, the PIR sensor and the buzzer", ha="left", fs=5.8,
          color=GREY, style="normal")

    # branch 2 of the same rail: module output -> USB-C socket of the panel
    line(ax, [(72, 4.5), (96.6, 4.5), (96.6, 69), (98, 69)], color=GREEN, lw=1.1)
    ax.plot([72], [4.5], marker="o", ms=2.6, color=GREEN, zorder=4)
    label(ax, 95.4, 36.0, "branch 2: 5 V to the panel USB-C (about 1.5 A peak)",
          rot=90, fs=5.8, color=GREEN, style="normal")

    # ground
    ax.plot([45, 45], [27.6, 24.4], color=INK, lw=1.0)
    ax.plot([43.2, 46.8], [24.4, 24.4], color=INK, lw=1.3)
    ax.plot([44.1, 45.9], [23.6, 23.6], color=INK, lw=1.3)
    ax.plot([44.6, 45.4], [22.8, 22.8], color=INK, lw=1.3)
    ax.text(47.2, 24.4, "common ground, star point at the module", fontsize=5.6, color=GREY,
            va="center", style="italic")
    ax.text(2, 15.0, "", fontsize=5)

    # 3V3 note
    ax.text(61.4, 26.0, "3V3 -> DS3231 VCC (1 mA)", fontsize=5.6, color=GREY,
            va="center", style="italic")

    ax.text(50, 0.9,
            "The ESP32 and the panel share no signal conductor: every message travels over the BLE link. Both loads take their 5 V\n"
            "from the same adapter and the same 2-in-1 module, as branch 1 and branch 2 of the one rail shown here.",
            ha="center", fontsize=6.0, color=GREY, style="italic", linespacing=1.5)

    save(fig, "fig3_2_circuit.png")


# --------------------------------------------------------------------------- 3.3 BLE frame
def ble_frame():
    fig, ax = new(11, 5.2)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 47)

    # segment 1: envelope
    def seg(x, y, w, h, text, fill, fs=6.0, edge=INK, lw=0.8):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge, lw=lw, zorder=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                color=INK, linespacing=1.3, zorder=3)

    y, h = 30, 9
    ax.text(0.5, 42.5, "(a)  GATT write to characteristic 0xFA02 - the envelope that opens a message",
            fontsize=7.4, fontweight="bold", color=INK, va="center")

    seg(4, y, 9, h, "length\n2 bytes LE", "#dfe7f1")
    seg(13, y, 9, h, "command\n2 bytes\n00 01", "#dfe7f1")
    seg(22, y, 12, h, "payload length\n4 bytes LE", "#dfe7f1")
    seg(34, y, 12, h, "CRC32\n4 bytes LE", "#dfe7f1")
    seg(46, y, 8, h, "slot\n1 byte 00", "#dfe7f1")
    seg(54, y, 14, h, "animation, speed,\nrainbow, RGB", "#dfe7f1")
    seg(68, y, 28, h, "character count,\nfont height, background", "#dfe7f1")

    ax.annotate("", xy=(4, y - 2.6), xytext=(54, y - 2.6),
                arrowprops=dict(arrowstyle="<|-|>", color=GREY, lw=1))
    ax.text(29, y - 5.4, "15-byte envelope (same for every message)", ha="center", fontsize=6.2, color=GREY)

    # segment 2: per-character records
    y2, h2 = 8, 9
    ax.text(0.5, 21.0, "(b)  the payload - one 20-byte record per 8-column tile of the rendered message",
            fontsize=7.4, fontweight="bold", color=INK, va="center")

    seg(4, y2, 13, h2, "tile meta\n6 bytes", "#e9f2ea")
    for i in range(5):
        seg(17 + i * 10, y2, 10, h2, f"bitmap\nbyte {i * 8}\n8 px", "#e9f2ea", fs=5.6)
    seg(67, y2, 13, h2, "...", "#e9f2ea")
    seg(80, y2, 16, h2, "next tile\n20 bytes", "#e9f2ea", fs=5.6)

    ax.text(50, 2.4,
            "Repeated over BLE: MTU negotiated at 512, so the message is cut into 509-byte writes, "
            "roughly 4 kB at a time, with a short pause between segments.",
            ha="center", fontsize=6.2, color=GREY, style="italic")

    save(fig, "fig3_3_bleframe.png")


# ---------------------------------------------------------------------------- 3.4 flowchart
def flowchart():
    fig, ax = new(9.4, 11.4)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 121)

    def term(x, y, w, h, t, fill="#dbe5f1"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=4",
                                    facecolor=fill, edgecolor=INK, lw=1.0, zorder=2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=6.8, zorder=3,
                linespacing=1.35)

    def proc(x, y, w, h, t, fill=FILL):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=INK, lw=1.0, zorder=2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=6.6, zorder=3,
                linespacing=1.35)

    def dec(x, y, w, h, t, fill="#fdf3e7"):
        ax.add_patch(plt.Polygon([[x + w / 2, y + h], [x + w, y + h / 2], [x + w / 2, y],
                                 [x, y + h / 2]], facecolor=fill, edgecolor=INK, lw=1.0, zorder=2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=6.4, zorder=3,
                linespacing=1.3)

    def down(x, y1, y2, t="", fs=5.9):
        arrow(ax, (x, y1), (x, y2), color=INK, lw=1.0, shrink=0)
        if t:
            ax.text(x + 1.3, (y1 + y2) / 2, t, fontsize=fs, color=GREY, ha="left", va="center")

    term(30, 114, 40, 6, "power on / reset", fill="#dbe5f1")
    proc(22, 103, 56, 8, "initialise serial monitor, LittleFS, I2C + DS3231, keypad, buzzer, PIR interrupt")
    proc(22, 92, 56, 8, "start Wi-Fi access point  +  web server at 192.168.4.1")
    proc(22, 81, 56, 8, "initialise BLE host, connect to LED_BLE_xxxx, discover 0xFA02 / 0xFA03")
    dec(30, 69, 40, 9, "BLE link\nestablished?")
    proc(8, 69.5, 16, 7, "retry after\nback-off", fill="#f7e7e7")
    proc(22, 57, 56, 8, "STATE IDLE: send stationary HH:MM clock, refresh when the minute changes")

    dec(30, 44, 40, 9, "PIR high, or wake\ncommand from the web page?")
    proc(22, 33, 56, 7, "STATE GREETING: GOOD MORNING / AFTERNOON / EVENING")
    proc(22, 24.5, 56, 7, "STATE WELCOME: WELCOME TO ELECTRICAL, then level prompt")
    proc(22, 16, 56, 7, "read level and day, look up classes in /eee_timetable.json")
    proc(22, 8.5, 56, 6.5, "STATE TIMETABLE: stream the message over BLE, panel scrolls it")
    proc(22, 1.2, 56, 6.0, "STATE REENTRY (15 s), GOODBYE, then COOLDOWN -> IDLE")

    down(50, 114, 111)
    down(50, 103, 100)
    down(50, 92, 89)
    down(50, 81, 78)
    arrow(ax, (30, 73.5), (25.5, 73.0), color=INK, lw=1.0)
    ax.text(26.4, 71.4, "no", fontsize=5.9, color=GREY)
    down(50, 69, 65, "yes")
    down(50, 57, 53)
    arrow(ax, (30, 48.5), (18.0, 51.0), color=INK, lw=1.0)
    ax.text(20.5, 46.6, "no", fontsize=5.9, color=GREY)
    line(ax, [(16.5, 51), (16.5, 61)], color=INK, lw=1.0)
    arrow(ax, (16.5, 61), (22, 61), color=INK, lw=1.0)
    ax.text(23.4, 50.4, "yes", fontsize=5.9, color=GREY)
    down(50, 44, 40)
    down(50, 33, 31.5)
    down(50, 24.5, 23)
    down(50, 16, 15)
    down(50, 8.5, 7.2)

    # web server note
    line(ax, [(78, 96), (84, 96)], color=BLUE, lw=1.0, ls=(0, (3, 2)))
    ax.text(84.6, 96, "served on\nevery pass\nof the loop", fontsize=5.8, color=BLUE, va="center")
    line(ax, [(78, 61), (84, 61)], color=BLUE, lw=1.0, ls=(0, (3, 2)))
    ax.text(84.6, 61, "upload / clock /\npreview handled\nbetween messages", fontsize=5.8,
            color=BLUE, va="center")

    save(fig, "fig3_4_flowchart.png")


if __name__ == "__main__":
    block_diagram()
    circuit_diagram()
    ble_frame()
    flowchart()
