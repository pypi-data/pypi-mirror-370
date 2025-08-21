import os
import shutil

def EnableWindowsAnsiSupport():
    if os.name != 'nt':
        return

    import ctypes
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)  
    if handle == 0:
        return
    mode = ctypes.c_uint()
    if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        return
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
    kernel32.SetConsoleMode(handle, new_mode)


IS_WINDOWS = os.name == 'nt'
IS_CMD = False

if IS_WINDOWS:
    import platform
    WT = os.environ.get("WT_SESSION")
    PS = os.environ.get("PSModulePath")
    if WT or PS:
        IS_CMD = False 
    else:
        IS_CMD = True   


class ColorUtils:
    ANSI16Colors = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "brightBlack": 90,
        "brightRed": 91,
        "brightGreen": 92,
        "brightYellow": 93,
        "brightBlue": 94,
        "brightMagenta": 95,
        "brightCyan": 96,
        "brightWhite": 97,
    }

    @staticmethod
    def RgbToAnsiTruecolor(r, g, b):
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def RgbToAnsi16color(r, g, b):
        colorMap = {
            (0, 0, 0): 30,
            (128, 0, 0): 31,
            (0, 128, 0): 32,
            (128, 128, 0): 33,
            (0, 0, 128): 34,
            (128, 0, 128): 35,
            (0, 128, 128): 36,
            (192, 192, 192): 37,
            (128, 128, 128): 90,
            (255, 0, 0): 91,
            (0, 255, 0): 92,
            (255, 255, 0): 93,
            (0, 0, 255): 94,
            (255, 0, 255): 95,
            (0, 255, 255): 96,
            (255, 255, 255): 97,
        }

        def dist(c1, c2):
            return sum((a - b) ** 2 for a, b in zip(c1, c2))

        nearestColor = min(colorMap.keys(), key=lambda c: dist(c, (r, g, b)))
        code = colorMap[nearestColor]
        return f"\033[{code}m"

    @staticmethod
    def RgbToAnsi(r, g, b):
        if IS_WINDOWS and IS_CMD:
            return ColorUtils.RgbToAnsi16color(r, g, b)
        else:
            return ColorUtils.RgbToAnsiTruecolor(r, g, b)

    @staticmethod
    def InterpolateRgb(colors, t):
        total = len(colors) - 1
        i = int(t * total)
        t = (t * total) - i
        if i >= total:
            return colors[-1]
        r1, g1, b1 = colors[i]
        r2, g2, b2 = colors[i + 1]
        return (
            int(r1 + (r2 - r1) * t),
            int(g1 + (g2 - g1) * t),
            int(b1 + (b2 - b1) * t)
        )

    @staticmethod
    def CenterText(text: str, width: int = None) -> str:
        if width is None:
            try:
                width = shutil.get_terminal_size().columns
            except:
                width = 80
        return text.center(width)