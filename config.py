TERMINAL = "xfce4-terminal"

FOCUSED_BORDER_COLOR = "#ff0000"
UNFOCUSED_BORDER_COLOR = "#222222"
BORDER_WIDTH = 3

MIN_WIDTH = 100
MIN_HEIGHT = 60

MODKEY = 'X.Mod1Mask'

KEYBINDS = [
    {
        'mod': MODKEY,
        'key': 'F1',
        'action': 'raise',
    },
    {
        'mod': MODKEY + ' + X.ShiftMask',
        'key': 'Return',
        'action': 'spawn_terminal',
    },
    {
        'mod': MODKEY,
        'key': 'm',
        'action': 'maximize',
    },
    {
        'mod': MODKEY,
        'key': 'u',
        'action': 'unmaximize',
    },
    {
        'mod': MODKEY + ' + X.ShiftMask',
        'key': 'q',
        'action': 'close',
    },
]

