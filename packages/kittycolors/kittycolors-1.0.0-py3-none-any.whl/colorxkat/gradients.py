from .utils import ColorUtils

class Gradients:
    Presets = {
        "rainbow": [(255, 0, 0), (255, 165, 0), (255, 255, 0),
                    (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)],
        "sunset": [(255, 94, 98), (255, 195, 113), (255, 247, 174)],
        "mint": [(152, 255, 152), (0, 255, 127), (46, 139, 87)],
        "fire": [(255, 0, 0), (255, 140, 0), (255, 255, 0)],
        "ocean": [(0, 128, 255), (0, 255, 255), (0, 128, 128)],
        "midnight": [(25, 25, 112), (0, 0, 128), (75, 0, 130)],
        "pinkpurple": [(255, 105, 180), (147, 112, 219)],
        "purpleblue": [(147, 112, 219), (0, 0, 255)],
        "greyorange": [(128, 128, 128), (255, 165, 0)],
        "limegreen": [(50, 205, 50), (0, 255, 127)],
        "bluecyan": [(0, 0, 255), (0, 255, 255)],
        "greentoorange": [(0, 255, 0), (255, 165, 0)],
        "blacktowhite": [(0, 0, 0), (255, 255, 255)],
        "redblue": [(255, 0, 0), (0, 0, 255)],
        "yellowgreen": [(255, 255, 0), (0, 128, 0)],
        "pinkcyan": [(255, 105, 180), (0, 255, 255)],
        "orangeblue": [(255, 165, 0), (0, 0, 255)],
        "whitepurple": [(255, 255, 255), (128, 0, 128)],
    }

    @staticmethod
    def Apply(text: str, gradientName: str, center: bool = False) -> str:
        colors = Gradients.Presets.get(gradientName.lower())
        if not colors:
            return text
        output = ""
        steps = len(text)
        for i, char in enumerate(text):
            r, g, b = ColorUtils.InterpolateRgb(colors, i / max(steps - 1, 1))
            ansiCode = ColorUtils.RgbToAnsi(r, g, b)
            output += f"{ansiCode}{char}"
        output += "\033[0m"
        return ColorUtils.CenterText(output) if center else output
