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


class RgbFadeAnimation:
    """
    Animation that fades all the LEDs of a strip simultaneously between Red, Green,
    and Blue.
    
    
    
    :param led_start_index:    The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs,
                               and 8-399 control an attached LED strip.
    :type led_start_index: int
    :param led_end_index:    The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
    :type led_end_index: int
    :param slot:    The slot of this animation, within [0, 7]. Each slot on the
                    CANdle can store and run one animation.
    :type slot: int
    :param brightness:    The brightness of the animation, as a scalar from 0.0 to
                          1.0.
    :type brightness: float
    :param frame_rate:    The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the
                          LEDs, adjusting the brightness of the LEDs by 1%.
    :type frame_rate: hertz
    """

    def __init__(self, led_start_index: int, led_end_index: int, slot: int = 0, brightness: float = 1.0, frame_rate: hertz = 100):
        self._name = "RgbFadeAnimation"
        """The name of this control request."""
        self.update_freq_hz: hertz = 20
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
        self.slot = slot
        """
        The slot of this animation, within [0, 7]. Each slot on the CANdle can store and
        run one animation.
        """
        self.brightness = brightness
        """
        The brightness of the animation, as a scalar from 0.0 to 1.0.
        """
        self.frame_rate = frame_rate
        """
        The frame rate of the animation, from [2, 1000] Hz. This determines the speed of
        the animation.
        
        A frame is defined as a transition in the state of the LEDs, adjusting the
        brightness of the LEDs by 1%.
        
        - Units: Hz
        
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
        ss.append("Control: RgbFadeAnimation")
        ss.append("    led_start_index: " + str(self.led_start_index))
        ss.append("    led_end_index: " + str(self.led_end_index))
        ss.append("    slot: " + str(self.slot))
        ss.append("    brightness: " + str(self.brightness))
        ss.append("    frame_rate: " + str(self.frame_rate) + " Hz")
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
        return StatusCode(Native.instance().c_ctre_phoenix6_RequestControlRgbFadeAnimation(ctypes.c_char_p(bytes(network, 'utf-8')), device_hash, self.update_freq_hz, self.led_start_index, self.led_end_index, self.slot, self.brightness, self.frame_rate))

    
    def with_led_start_index(self, new_led_start_index: int) -> 'RgbFadeAnimation':
        """
        Modifies this Control Request's led_start_index parameter and returns itself for
        method-chaining and easier to use request API.
    
        The index of the first LED this animation controls (inclusive). Indices 0-7
        control the onboard LEDs, and 8-399 control an attached LED strip.
    
        :param new_led_start_index: Parameter to modify
        :type new_led_start_index: int
        :returns: Itself
        :rtype: RgbFadeAnimation
        """
        self.led_start_index = new_led_start_index
        return self
    
    def with_led_end_index(self, new_led_end_index: int) -> 'RgbFadeAnimation':
        """
        Modifies this Control Request's led_end_index parameter and returns itself for
        method-chaining and easier to use request API.
    
        The index of the last LED this animation controls (inclusive). Indices 0-7
        control the onboard LEDs, and 8-399 control an attached LED strip.
    
        :param new_led_end_index: Parameter to modify
        :type new_led_end_index: int
        :returns: Itself
        :rtype: RgbFadeAnimation
        """
        self.led_end_index = new_led_end_index
        return self
    
    def with_slot(self, new_slot: int) -> 'RgbFadeAnimation':
        """
        Modifies this Control Request's slot parameter and returns itself for
        method-chaining and easier to use request API.
    
        The slot of this animation, within [0, 7]. Each slot on the CANdle can store and
        run one animation.
    
        :param new_slot: Parameter to modify
        :type new_slot: int
        :returns: Itself
        :rtype: RgbFadeAnimation
        """
        self.slot = new_slot
        return self
    
    def with_brightness(self, new_brightness: float) -> 'RgbFadeAnimation':
        """
        Modifies this Control Request's brightness parameter and returns itself for
        method-chaining and easier to use request API.
    
        The brightness of the animation, as a scalar from 0.0 to 1.0.
    
        :param new_brightness: Parameter to modify
        :type new_brightness: float
        :returns: Itself
        :rtype: RgbFadeAnimation
        """
        self.brightness = new_brightness
        return self
    
    def with_frame_rate(self, new_frame_rate: hertz) -> 'RgbFadeAnimation':
        """
        Modifies this Control Request's frame_rate parameter and returns itself for
        method-chaining and easier to use request API.
    
        The frame rate of the animation, from [2, 1000] Hz. This determines the speed of
        the animation.
        
        A frame is defined as a transition in the state of the LEDs, adjusting the
        brightness of the LEDs by 1%.
        
        - Units: Hz
        
    
        :param new_frame_rate: Parameter to modify
        :type new_frame_rate: hertz
        :returns: Itself
        :rtype: RgbFadeAnimation
        """
        self.frame_rate = new_frame_rate
        return self

    def with_update_freq_hz(self, new_update_freq_hz: hertz) -> 'RgbFadeAnimation':
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
        :rtype: RgbFadeAnimation
        """
        self.update_freq_hz = new_update_freq_hz
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
        control_info["slot"] = self.slot
        control_info["brightness"] = self.brightness
        control_info["frame_rate"] = self.frame_rate
        return control_info
