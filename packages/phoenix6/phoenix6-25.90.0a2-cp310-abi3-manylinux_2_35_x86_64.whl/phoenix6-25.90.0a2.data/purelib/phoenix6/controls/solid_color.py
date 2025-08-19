"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

from phoenix6.phoenix_native import Native
from phoenix6.status_code import StatusCode
from phoenix6.units import *
import ctypes

from phoenix6.signals.rgbw_color import *

class SolidColor:
    """
    Sets LEDs to a solid color.
    
    
    
    :param led_start_index:    The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs,
                               and 8-399 control an attached LED strip.
    :type led_start_index: int
    :param led_end_index:    The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
    :type led_end_index: int
    :param color:    The color to apply to the LEDs.
    :type color: RGBWColor
    """

    def __init__(self, led_start_index: int, led_end_index: int, color: RGBWColor = RGBWColor()):
        self._name = "SolidColor"
        """The name of this control request."""
        # This request is always 0 Hz. self.update_freq_hz: hertz = 0
        """
        The period at which this control will update at.
        This is designated in Hertz, with a minimum of 20 Hz
        (every 50 ms) and a maximum of 1000 Hz (every 1 ms).

        If this field is set to 0 Hz, the control request will
        be sent immediately as a one-shot frame. This may be useful
        for advanced applications that require outputs to be
        synchronized with data acquisition. In this case, we
        recommend not exceeding 50 ms between control calls.
        """
        
        self.led_start_index = led_start_index
        """
        The index of the first LED this animation controls (inclusive). Indices 0-7
        control the onboard LEDs, and 8-399 control an attached LED strip.
        """
        self.led_end_index = led_end_index
        """
        The index of the last LED this animation controls (inclusive). Indices 0-7
        control the onboard LEDs, and 8-399 control an attached LED strip.
        """
        self.color = color
        """
        The color to apply to the LEDs.
        """

    @property
    def name(self) -> str:
        """
        Gets the name of this control request.

        :returns: Name of the control request
        :rtype: str
        """
        return self._name

    def __str__(self) -> str:
        ss = []
        ss.append("Control: SolidColor")
        ss.append("    led_start_index: " + str(self.led_start_index))
        ss.append("    led_end_index: " + str(self.led_end_index))
        ss.append("    color: " + str(self.color))
        return "\n".join(ss)

    def _send_request(self, network: str, device_hash: int) -> StatusCode:
        """
        Sends this request out over CAN bus to the device for
        the device to apply.

        :param network: Network to send request over
        :type network: str
        :param device_hash: Device to send request to
        :type device_hash: int
        :returns: Status of the send operation
        :rtype: StatusCode
        """
        return StatusCode(Native.instance().c_ctre_phoenix6_RequestControlSolidColor(ctypes.c_char_p(bytes(network, 'utf-8')), device_hash, 0, self.led_start_index, self.led_end_index, self.color.red, self.color.green, self.color.blue, self.color.white))

    
    def with_led_start_index(self, new_led_start_index: int) -> 'SolidColor':
        """
        Modifies this Control Request's led_start_index parameter and returns itself for
        method-chaining and easier to use request API.
    
        The index of the first LED this animation controls (inclusive). Indices 0-7
        control the onboard LEDs, and 8-399 control an attached LED strip.
    
        :param new_led_start_index: Parameter to modify
        :type new_led_start_index: int
        :returns: Itself
        :rtype: SolidColor
        """
        self.led_start_index = new_led_start_index
        return self
    
    def with_led_end_index(self, new_led_end_index: int) -> 'SolidColor':
        """
        Modifies this Control Request's led_end_index parameter and returns itself for
        method-chaining and easier to use request API.
    
        The index of the last LED this animation controls (inclusive). Indices 0-7
        control the onboard LEDs, and 8-399 control an attached LED strip.
    
        :param new_led_end_index: Parameter to modify
        :type new_led_end_index: int
        :returns: Itself
        :rtype: SolidColor
        """
        self.led_end_index = new_led_end_index
        return self
    
    def with_color(self, new_color: RGBWColor) -> 'SolidColor':
        """
        Modifies this Control Request's color parameter and returns itself for
        method-chaining and easier to use request API.
    
        The color to apply to the LEDs.
    
        :param new_color: Parameter to modify
        :type new_color: RGBWColor
        :returns: Itself
        :rtype: SolidColor
        """
        self.color = new_color
        return self

    def with_update_freq_hz(self, new_update_freq_hz: hertz) -> 'SolidColor':
        """
        Sets the period at which this control will update at.
        This is designated in Hertz, with a minimum of 20 Hz
        (every 50 ms) and a maximum of 1000 Hz (every 1 ms).

        If this field is set to 0 Hz, the control request will
        be sent immediately as a one-shot frame. This may be useful
        for advanced applications that require outputs to be
        synchronized with data acquisition. In this case, we
        recommend not exceeding 50 ms between control calls.

        :param new_update_freq_hz: Parameter to modify
        :type new_update_freq_hz: hertz
        :returns: Itself
        :rtype: SolidColor
        """
        # This request is always 0 Hz. self.update_freq_hz = new_update_freq_hz
        return self

    @property
    def control_info(self) -> dict:
        """
        Gets information about this control request.

        :returns: Dictonary of control parameter names and corresponding applied values
        :rtype: dict
        """
        control_info = {}
        control_info["name"] = self._name
        control_info["led_start_index"] = self.led_start_index
        control_info["led_end_index"] = self.led_end_index
        control_info["color"] = self.color
        return control_info
