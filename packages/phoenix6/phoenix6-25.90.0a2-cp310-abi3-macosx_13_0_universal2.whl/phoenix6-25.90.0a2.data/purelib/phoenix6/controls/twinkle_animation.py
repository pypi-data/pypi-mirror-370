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

class TwinkleAnimation:
    """
    Animation that randomly turns LEDs on and off to a certain color.
    
    
    
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
    :param color:    The color to use in the animation.
    :type color: RGBWColor
    :param max_leds_on_proportion:    The max proportion of LEDs that can be on, in
                                      the range [0.1, 1.0].
    :type max_leds_on_proportion: float
    :param frame_rate:    The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the
                          LEDs, turning one on or off.
    :type frame_rate: hertz
    """

    def __init__(self, led_start_index: int, led_end_index: int, slot: int = 0, color: RGBWColor = RGBWColor(), max_leds_on_proportion: float = 0.5, frame_rate: hertz = 100):
        self._name = "TwinkleAnimation"
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
        self.color = color
        """
        The color to use in the animation.
        """
        self.max_leds_on_proportion = max_leds_on_proportion
        """
        The max proportion of LEDs that can be on, in the range [0.1, 1.0].
        """
        self.frame_rate = frame_rate
        """
        The frame rate of the animation, from [2, 1000] Hz. This determines the speed of
        the animation.
        
        A frame is defined as a transition in the state of the LEDs, turning one on or
        off.
        
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
        ss.append("Control: TwinkleAnimation")
        ss.append("    led_start_index: " + str(self.led_start_index))
        ss.append("    led_end_index: " + str(self.led_end_index))
        ss.append("    slot: " + str(self.slot))
        ss.append("    color: " + str(self.color))
        ss.append("    max_leds_on_proportion: " + str(self.max_leds_on_proportion))
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
        return StatusCode(Native.instance().c_ctre_phoenix6_RequestControlTwinkleAnimation(ctypes.c_char_p(bytes(network, 'utf-8')), device_hash, self.update_freq_hz, self.led_start_index, self.led_end_index, self.slot, self.color.red, self.color.green, self.color.blue, self.color.white, self.max_leds_on_proportion, self.frame_rate))

    
    def with_led_start_index(self, new_led_start_index: int) -> 'TwinkleAnimation':
        """
        Modifies this Control Request's led_start_index parameter and returns itself for
        method-chaining and easier to use request API.
    
        The index of the first LED this animation controls (inclusive). Indices 0-7
        control the onboard LEDs, and 8-399 control an attached LED strip.
    
        :param new_led_start_index: Parameter to modify
        :type new_led_start_index: int
        :returns: Itself
        :rtype: TwinkleAnimation
        """
        self.led_start_index = new_led_start_index
        return self
    
    def with_led_end_index(self, new_led_end_index: int) -> 'TwinkleAnimation':
        """
        Modifies this Control Request's led_end_index parameter and returns itself for
        method-chaining and easier to use request API.
    
        The index of the last LED this animation controls (inclusive). Indices 0-7
        control the onboard LEDs, and 8-399 control an attached LED strip.
    
        :param new_led_end_index: Parameter to modify
        :type new_led_end_index: int
        :returns: Itself
        :rtype: TwinkleAnimation
        """
        self.led_end_index = new_led_end_index
        return self
    
    def with_slot(self, new_slot: int) -> 'TwinkleAnimation':
        """
        Modifies this Control Request's slot parameter and returns itself for
        method-chaining and easier to use request API.
    
        The slot of this animation, within [0, 7]. Each slot on the CANdle can store and
        run one animation.
    
        :param new_slot: Parameter to modify
        :type new_slot: int
        :returns: Itself
        :rtype: TwinkleAnimation
        """
        self.slot = new_slot
        return self
    
    def with_color(self, new_color: RGBWColor) -> 'TwinkleAnimation':
        """
        Modifies this Control Request's color parameter and returns itself for
        method-chaining and easier to use request API.
    
        The color to use in the animation.
    
        :param new_color: Parameter to modify
        :type new_color: RGBWColor
        :returns: Itself
        :rtype: TwinkleAnimation
        """
        self.color = new_color
        return self
    
    def with_max_leds_on_proportion(self, new_max_leds_on_proportion: float) -> 'TwinkleAnimation':
        """
        Modifies this Control Request's max_leds_on_proportion parameter and returns itself for
        method-chaining and easier to use request API.
    
        The max proportion of LEDs that can be on, in the range [0.1, 1.0].
    
        :param new_max_leds_on_proportion: Parameter to modify
        :type new_max_leds_on_proportion: float
        :returns: Itself
        :rtype: TwinkleAnimation
        """
        self.max_leds_on_proportion = new_max_leds_on_proportion
        return self
    
    def with_frame_rate(self, new_frame_rate: hertz) -> 'TwinkleAnimation':
        """
        Modifies this Control Request's frame_rate parameter and returns itself for
        method-chaining and easier to use request API.
    
        The frame rate of the animation, from [2, 1000] Hz. This determines the speed of
        the animation.
        
        A frame is defined as a transition in the state of the LEDs, turning one on or
        off.
        
        - Units: Hz
        
    
        :param new_frame_rate: Parameter to modify
        :type new_frame_rate: hertz
        :returns: Itself
        :rtype: TwinkleAnimation
        """
        self.frame_rate = new_frame_rate
        return self

    def with_update_freq_hz(self, new_update_freq_hz: hertz) -> 'TwinkleAnimation':
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
        :rtype: TwinkleAnimation
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
        control_info["color"] = self.color
        control_info["max_leds_on_proportion"] = self.max_leds_on_proportion
        control_info["frame_rate"] = self.frame_rate
        return control_info
