import board
import busio

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.scanners.keypad import MatrixScanner, KeysScanner

from kmk.modules.layers import Layers
from kmk.modules.holdtap import HoldTap
from kmk.modules.encoder import EncoderHandler
from kmk.extensions.media_keys import MediaKeys

# OLED
from kmk.extensions.display import Display, TextEntry
from kmk.extensions.display.ssd1306 import SSD1306


# ----------------------------
# Keyboard (Your Pins)
# ----------------------------
class PrateekMacroPad(KMKKeyboard):
    def __init__(self):
        super().__init__()

        # Matrix:
        # ROW0 → D0, ROW1 → D1, ROW2 → D2
        # COL0 → D6, COL1 → D7, COL2 → D8
        self.matrix = [
            MatrixScanner(
                column_pins=(board.D6, board.D7, board.D8),
                row_pins=(board.D0, board.D1, board.D2),
                columns_to_anodes=DiodeOrientation.ROW2COL,
                # If keys behave "wrong", switch to:
                # columns_to_anodes=DiodeOrientation.COL2ROW,
            ),

            # Encoder switch: one side GND, other D3
            KeysScanner(
                pins=[board.D3],
                value_when_pressed=False,  # pressed = LOW
            ),
        ]


keyboard = PrateekMacroPad()


# ----------------------------
# Modules / Extensions
# ----------------------------
keyboard.extensions.append(MediaKeys())

layers = Layers()
keyboard.modules.append(layers)

holdtap = HoldTap()
holdtap.tap_time = 230  # tweak if you want (ms)
keyboard.modules.append(holdtap)

encoder = EncoderHandler()
keyboard.modules.append(encoder)


# ----------------------------
# OLED Setup (SDA=D4, SCL=D5)
# ----------------------------
# Your wiring: SDA → D4, SCL → D5
i2c = busio.I2C(board.D5, board.D4)  # (SCL, SDA)
oled_driver = SSD1306(i2c=i2c)

display = Display(
    display=oled_driver,
    width=128,
    height=32,
    brightness=0.6,
    dim_time=25,
    dim_target=0.06,
    off_time=600,
)

display.entries = [
    TextEntry(text="PRATEEK MACRO", x=0, y=0),

    TextEntry(text="CODING",   x=0, y=16, layer=0),
    TextEntry(text="EDITING",  x=0, y=16, layer=1),
    TextEntry(text="MEDIA",    x=0, y=16, layer=2),
    TextEntry(text="NUMPAD",   x=0, y=16, layer=3),

    # Layer-select overlay (hold MODE key)
    TextEntry(text="MODE: 1-4", x=0, y=16, layer=4),
]
keyboard.extensions.append(display)


# ----------------------------
# Encoder Setup (A=D9, B=D10)
# ----------------------------
encoder.pins = ((board.D9, board.D10),)

# Encoder actions per layer:
# ((CCW, CW),)
encoder.map = [
    ((KC.VOLD, KC.VOLU),),     # Layer 0 Coding: volume
    ((KC.PGDN, KC.PGUP),),     # Layer 1 Editing: page down/up
    ((KC.MPRV, KC.MNXT),),     # Layer 2 Media: prev/next
    ((KC.LEFT, KC.RGHT),),     # Layer 3 Numpad: left/right (super handy)
    ((KC.VOLD, KC.VOLU),),     # Layer 4 Mode: keep simple
]

# Encoder press key (10th key in keymap because KeysScanner adds it)
ENC_PRESS = KC.MPLY  # press knob = play/pause (change if you want)


# ----------------------------
# Super-useful shortcuts (cross-platform-ish)
# ----------------------------
COPY = KC.LCTL(KC.C)
PASTE = KC.LCTL(KC.V)
CUT = KC.LCTL(KC.X)
UNDO = KC.LCTL(KC.Z)
REDO = KC.LCTL(KC.Y)
SAVE = KC.LCTL(KC.S)
FIND = KC.LCTL(KC.F)
NEW_TAB = KC.LCTL(KC.T)
CLOSE_TAB = KC.LCTL(KC.W)
SCREENSHOT = KC.LGUI(KC.LSFT(KC.S))  # Windows/Chromebook style (works on many)


# ----------------------------
# MODE key behavior like demo:
# Hold MODE -> Layer 4 (mode-select)
# In mode-select, pressing keys 1-4 jumps to layers 0-3
# Tap MODE -> Enter (useful)
# ----------------------------
MODE = KC.HT(KC.ENT, KC.MO(4), prefer_hold=True, tap_interrupted=False, tap_time=230)


# ----------------------------
# Keymap (3x3 = 9 keys) + encoder press
# Order is:
# Row0: K1 K2 K3
# Row1: K4 K5 K6
# Row2: K7 K8 K9
# Then encoder press appended at end.
# ----------------------------

keyboard.keymap = [
    # ----------------------------
    # Layer 0: CODING (daily useful)
    # ----------------------------
    [
        KC.ESC,     NEW_TAB,     CLOSE_TAB,
        SAVE,       FIND,        UNDO,
        COPY,       PASTE,       MODE,
        ENC_PRESS,
    ],

    # ----------------------------
    # Layer 1: EDITING / PRODUCTIVITY
    # ----------------------------
    [
        KC.TAB,     KC.BSPC,     KC.DEL,
        CUT,        COPY,        PASTE,
        UNDO,       REDO,        MODE,
        ENC_PRESS,
    ],

    # ----------------------------
    # Layer 2: MEDIA
    # ----------------------------
    [
        KC.MUTE,    KC.VOLD,     KC.VOLU,
        KC.MPRV,    KC.MPLY,     KC.MNXT,
        KC.BRDOWN,  KC.BRUP,     MODE,
        ENC_PRESS,
    ],

    # ----------------------------
    # Layer 3: NUMPAD / NAV
    # ----------------------------
    [
        KC.N7,      KC.N8,       KC.N9,
        KC.N4,      KC.N5,       KC.N6,
        KC.N1,      KC.N2,       MODE,
        ENC_PRESS,
    ],

    # ----------------------------
    # Layer 4: MODE SELECT (hold MODE key)
    # Press 1/2/3/4 to jump to layers 0/1/2/3
    # ----------------------------
    [
        KC.TO(0),   KC.TO(1),    KC.TO(2),
        KC.TO(3),   SCREENSHOT,  KC.NO,
        KC.NO,      KC.NO,       KC.TRNS,
        KC.MUTE,
    ],
]


if __name__ == "__main__":
    keyboard.go()