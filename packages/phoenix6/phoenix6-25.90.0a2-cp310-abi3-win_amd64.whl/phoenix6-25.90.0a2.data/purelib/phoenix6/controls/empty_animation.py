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


class EmptyAnimation:
    """
    An empty animation, clearing any animation in the specified slot.
    
    
    
    :param slot:    The slot of this animation, within [0, 7]. Each slot on the
                    CANdle can store and run one animation.
    :type slot: int
    """

    def __init__(self, slot: int):
        self._name = "EmptyAnimation"
        """The name of this control request."""
        self.update_freq_hz: hertz = 0
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
        
        self.slot = slot
        """
        The slot of this animation, within [0, 7]. Each slot on the CANdle can store and
        run one animation.
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
        ss.append("Control: EmptyAnimation")
        ss.append("    slot: " + str(self.slot))
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
        return StatusCode(Native.instance().c_ctre_phoenix6_RequestControlEmptyAnimation(ctypes.c_char_p(bytes(network, 'utf-8')), device_hash, self.update_freq_hz, self.slot))

    
    def with_slot(self, new_slot: int) -> 'EmptyAnimation':
        """
        Modifies this Control Request's slot parameter and returns itself for
        method-chaining and easier to use request API.
    
        The slot of this animation, within [0, 7]. Each slot on the CANdle can store and
        run one animation.
    
        :param new_slot: Parameter to modify
        :type new_slot: int
        :returns: Itself
        :rtype: EmptyAnimation
        """
        self.slot = new_slot
        return self

    def with_update_freq_hz(self, new_update_freq_hz: hertz) -> 'EmptyAnimation':
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
        :rtype: EmptyAnimation
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
        control_info["slot"] = self.slot
        return control_info
