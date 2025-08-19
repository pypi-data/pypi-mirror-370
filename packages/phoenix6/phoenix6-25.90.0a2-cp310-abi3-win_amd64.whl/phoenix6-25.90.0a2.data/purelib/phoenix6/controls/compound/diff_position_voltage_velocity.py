"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

import ctypes
from phoenix6.phoenix_native import Native
from phoenix6.status_code import StatusCode
from phoenix6.units import *
from phoenix6.controls.position_voltage import PositionVoltage
from phoenix6.controls.velocity_voltage import VelocityVoltage

class Diff_PositionVoltage_Velocity:
    """
    Requires Phoenix Pro and CANivore;
    Differential control with position average target and velocity difference target
    using voltage control.
    
    :param AverageRequest:    Average PositionVoltage request of the mechanism.
    :param DifferentialRequest:    Differential VelocityVoltage request of the
                                   mechanism.
    """

    def __init__(self, average_request: PositionVoltage, differential_request: VelocityVoltage):
        self._name = "Diff_PositionVoltage_Velocity"
        """The name of this control request."""
        self.update_freq_hz: hertz = 100
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
        
        self.average_request = average_request
        """
        Average PositionVoltage request of the mechanism.
        """
        self.differential_request = differential_request
        """
        Differential VelocityVoltage request of the mechanism.
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
        ss.append("Control: Diff_PositionVoltage_Velocity")
        ss.append("    average_request:")
        ss.append("        position: " + str(self.average_request.position) + " rotations")
        ss.append("        velocity: " + str(self.average_request.velocity) + " rotations per second")
        ss.append("        enable_foc: " + str(self.average_request.enable_foc))
        ss.append("        feed_forward: " + str(self.average_request.feed_forward) + " Volts")
        ss.append("        slot: " + str(self.average_request.slot))
        ss.append("        override_brake_dur_neutral: " + str(self.average_request.override_brake_dur_neutral))
        ss.append("        limit_forward_motion: " + str(self.average_request.limit_forward_motion))
        ss.append("        limit_reverse_motion: " + str(self.average_request.limit_reverse_motion))
        ss.append("        ignore_hardware_limits: " + str(self.average_request.ignore_hardware_limits))
        ss.append("        use_timesync: " + str(self.average_request.use_timesync))
        ss.append("    differential_request:")
        ss.append("        velocity: " + str(self.differential_request.velocity) + " rotations per second")
        ss.append("        acceleration: " + str(self.differential_request.acceleration) + " rotations per second²")
        ss.append("        enable_foc: " + str(self.differential_request.enable_foc))
        ss.append("        feed_forward: " + str(self.differential_request.feed_forward) + " Volts")
        ss.append("        slot: " + str(self.differential_request.slot))
        ss.append("        override_brake_dur_neutral: " + str(self.differential_request.override_brake_dur_neutral))
        ss.append("        limit_forward_motion: " + str(self.differential_request.limit_forward_motion))
        ss.append("        limit_reverse_motion: " + str(self.differential_request.limit_reverse_motion))
        ss.append("        ignore_hardware_limits: " + str(self.differential_request.ignore_hardware_limits))
        ss.append("        use_timesync: " + str(self.differential_request.use_timesync))
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
        return StatusCode(Native.instance().c_ctre_phoenix6_RequestControlDiff_PositionVoltage_Velocity(ctypes.c_char_p(bytes(network, 'utf-8')), device_hash, self.update_freq_hz, self.average_request.position, self.average_request.velocity, self.average_request.enable_foc, self.average_request.feed_forward, self.average_request.slot, self.average_request.override_brake_dur_neutral, self.average_request.limit_forward_motion, self.average_request.limit_reverse_motion, self.average_request.ignore_hardware_limits, self.average_request.use_timesync, self.differential_request.velocity, self.differential_request.acceleration, self.differential_request.enable_foc, self.differential_request.feed_forward, self.differential_request.slot, self.differential_request.override_brake_dur_neutral, self.differential_request.limit_forward_motion, self.differential_request.limit_reverse_motion, self.differential_request.ignore_hardware_limits, self.differential_request.use_timesync))

    
    def with_average_request(self, new_average_request: PositionVoltage) -> 'Diff_PositionVoltage_Velocity':
        """
        Modifies this Control Request's average_request parameter and returns itself for
        method-chaining and easier to use request API.
    
        Average PositionVoltage request of the mechanism.
    
        :param new_average_request: Parameter to modify
        :type new_average_request: PositionVoltage
        :returns: Itself
        :rtype: Diff_PositionVoltage_Velocity
        """
        self.average_request = new_average_request
        return self
    
    def with_differential_request(self, new_differential_request: VelocityVoltage) -> 'Diff_PositionVoltage_Velocity':
        """
        Modifies this Control Request's differential_request parameter and returns itself for
        method-chaining and easier to use request API.
    
        Differential VelocityVoltage request of the mechanism.
    
        :param new_differential_request: Parameter to modify
        :type new_differential_request: VelocityVoltage
        :returns: Itself
        :rtype: Diff_PositionVoltage_Velocity
        """
        self.differential_request = new_differential_request
        return self

    def with_update_freq_hz(self, new_update_freq_hz: hertz) -> 'Diff_PositionVoltage_Velocity':
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
        :rtype: Diff_PositionVoltage_Velocity
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
        control_info["average_request"] = self.average_request.control_info
        control_info["differential_request"] = self.differential_request.control_info
        return control_info
