from .utils import IS_WINDOWS, IS_CMD, ColorUtils

class Colors:
    Black       = (0, 0, 0)
    White       = (255, 255, 255)
    Gray        = (128, 128, 128)
    LightGray   = (200, 200, 200)
    DarkGray    = (64, 64, 64)

    Red         = (255, 0, 0)
    DarkRed     = (139, 0, 0)
    Orange      = (255, 165, 0)
    DarkOrange  = (255, 140, 0)
    Yellow      = (255, 255, 0)
    Gold        = (255, 215, 0)

    Green       = (0, 255, 0)
    DarkGreen   = (0, 100, 0)
    Lime        = (50, 205, 50)
    Mint        = (152, 255, 152)

    Blue        = (0, 0, 255)
    LightBlue   = (173, 216, 230)
    Cyan        = (0, 255, 255)
    DarkBlue    = (0, 0, 139)

    Purple      = (128, 0, 128)
    Indigo      = (75, 0, 130)
    Violet      = (148, 0, 211)
    Pink        = (255, 105, 180)
    HotPink     = (255, 20, 147)

    @staticmethod
    def Colorize(text: str, rgb: tuple) -> str:
        r, g, b = rgb
        ansiCode = ColorUtils.RgbToAnsi(r, g, b)
        resetCode = "\033[0m"
        return f"{ansiCode}{text}{resetCode}"
