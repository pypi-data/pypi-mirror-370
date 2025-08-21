from .colors import Colors
from .gradients import Gradients
from .utils import ColorUtils

from .utils import EnableWindowsAnsiSupport
try:
    EnableWindowsAnsiSupport()
except Exception as e:
    print(f"Re install pip lib | pip install .")

