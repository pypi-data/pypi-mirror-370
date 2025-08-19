"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

from phoenix6.units import degree
from typing import overload
import math

try:
    from wpilib import Color, Color8Bit
    USE_WPILIB = True
except ImportError:
    USE_WPILIB = False

class RGBWColor:
    """
    Represents an RGBW color that can be applied to an LED.
    """

    @overload
    def __init__(self) -> None:
        """
        Creates a new RGBW color where all components are off.
        """
        ...

    @overload
    def __init__(self, red: int, green: int, blue: int, white: int = 0) -> None:
        """
        Creates a new RGBW color from the given 8-bit components.
        
        :param red: The red component of the color, within [0, 255].
        :type red: int
        :param green: The green component of the color, within [0, 255].
        :type green: int
        :param blue: The blue component of the color, within [0, 255].
        :type blue: int
        :param white: The white component of the color, within [0, 255].
                    Note that not all LED strips support the white component.
        :type white: int
        """
        ...

    if USE_WPILIB:
        @overload
        def __init__(self, color: Color | Color8Bit) -> None:
            """
            Creates a new RGBW color from a WPILib color.
            The white component will be left 0.
            
            :param color: The WPILib color
            :type color: Color | Color8Bit
            """
            ...

    def __init__(self, red: 'int | Color | Color8Bit | None' = None, green: int | None = None, blue: int | None = None, white: int = 0):
        if USE_WPILIB:
            color_param = red
            if isinstance(color_param, Color):
                color_param = Color8Bit(color_param)
            if isinstance(color_param, Color8Bit) and green is None and blue is None and white == 0:
                color_param: Color8Bit
                (red, green, blue, white) = (color_param.red, color_param.green, color_param.blue, 0)

        if isinstance(red, int) and isinstance(green, int) and isinstance(blue, int) and isinstance(white, int):
            pass
        elif red is None and green is None and blue is None and isinstance(white, int):
            (red, green, blue) = (0, 0, 0)
        else:
            raise TypeError(
                "RGBWColor.__init__(): incompatible constructor arguments. The following argument types are supported:"
                + "\n    1. phoenix6.signals.RGBWColor()"
                + "\n    2. phoenix6.signals.RGBWColor(red: int, green: int, blue: int, white: int = 0)"
                + (
                    "\n    3. phoenix6.signals.RGBWColor(color: wpilib.Color | wpilib.Color8Bit)"
                    if USE_WPILIB else ""
                )
                + "\n"
            )

        self.__red: int = red
        self.__green: int = green
        self.__blue: int = blue
        self.__white: int = white

    @property
    def red(self) -> int:
        """
        The red component of the color, within [0, 255].
        """
        return self.__red

    @property
    def green(self) -> int:
        """
        The green component of the color, within [0, 255].
        """
        return self.__green

    @property
    def blue(self) -> int:
        """
        The blue component of the color, within [0, 255].
        """
        return self.__blue

    @property
    def white(self) -> int:
        """
        The white component of the color, within [0, 255].
        Note that not all LED strips support the white component.
        """
        return self.__white

    @staticmethod
    def from_hex(hex_str: str) -> 'RGBWColor | None':
        """
        Creates a new RGBW color from the given hex string.

        :param hex_str: The color hex in the form "#RRGGBBWW" or "#RRGGBB".
        :type hex_str: str
        :returns: The color if the hex is valid, otherwise None
        :rtype: RGBWColor | None
        """
        # hex string is either 7 (RGB) or 9 (RGBW) characters and starts with '#'
        if (len(hex_str) != 7 and len(hex_str) != 9) or not hex_str.startswith('#'):
            return None

        # [r, g, b, w]
        colors = [0] * 4
        for i in range(1, len(hex_str), 2):
            try:
                color = int(hex_str[i : i+2], 16)
            except:
                return None
            colors[(i - 1) >> 1] = color

        return RGBWColor(*colors)

    @staticmethod
    def from_hsv(h: degree, s: float, v: float) -> 'RGBWColor':
        """
        Creates a new RGBW color from the given HSV color.

        :param h: The hue as an angle from [0, 360) deg, where 0 is red.
        :type h: degree
        :param s: The saturation as a scalar from [0, 1].
        :type s: float
        :param v: The value as a scalar from [0, 1].
        :type v: float
        :returns: The corresponding RGB color; the white component will be 0.
        :rtype: RGBWColor
        """
        # wrap h to [0, 360) and clamp s and v
        if not 0.0 <= h < 360.0:
            h -= math.floor(h / 360.0) * 360.0
        s = max(0.0, min(s, 1.0))
        v = max(0.0, min(v, 1.0))

        # range between highest and lowest RGB components
        chroma = s * v
        # 6 regions of hue
        hue_region = h / 60.0

        # the highest RGB component
        maxf = v
        # the lowest RGB component
        minf = maxf - chroma

        # offset from max/min for the middle RGB component
        Xoffset = chroma * (hue_region - int(hue_region))
        # the middle RGB component; even regions from min, odd from max
        Xf = maxf - Xoffset if (int(hue_region) & 1) else minf + Xoffset

        # all scalars within [0, 1], scale to [0, 255]
        max_val = round(maxf * 255)
        min_val = round(minf * 255)
        X_val = round(Xf * 255)

        match int(hue_region):
            case 1: return RGBWColor(X_val, max_val, min_val)
            case 2: return RGBWColor(min_val, max_val, X_val)
            case 3: return RGBWColor(min_val, X_val, max_val)
            case 4: return RGBWColor(X_val, min_val, max_val)
            case 5: return RGBWColor(max_val, min_val, X_val)
            case _: return RGBWColor(max_val, X_val, min_val)

    def __mul__(self, brightness: float) -> 'RGBWColor':
        """
        Scales down the components of this color
        by the given brightness.

        :param brightness: The scalar to apply from [0, 1].
        :type brightness: float
        :returns: New color scaled by the given brightness
        :rtype: RGBWColor
        """
        brightness = max(0.0, min(brightness, 1.0))
        return RGBWColor(
            round(self.red * brightness),
            round(self.green * brightness),
            round(self.blue * brightness),
            round(self.white * brightness),
        )

    def __str__(self) -> str:
        """
        Returns this RGBW color as a string.

        :returns: A string in the format "RGBW(Red, Green, Blue, White)"
        :rtype: str
        """
        return f"RGBW({self.red}, {self.green}, {self.blue}, {self.white})"

    def to_hex_str(self) -> str:
        """
        Returns this RGBW color as a hex string.

        :returns: A hex string in the format "#RRGGBBWW"
        :rtype: str
        """
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}{self.white:02X}"
