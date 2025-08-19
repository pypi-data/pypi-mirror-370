"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

from phoenix6.status_code import StatusCode
from phoenix6.phoenix_native import Native
import ctypes
from phoenix6.units import *
from phoenix6.sim.device_type import DeviceType
from phoenix6.signals.spn_enums import S1StateValue, S2StateValue
from phoenix6.sim.chassis_reference import ChassisReference

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from phoenix6.hardware.core.core_candi import CoreCANdi

class CANdiSimState:
    """
    Creates an object to control the state of a simulated CANdi.

    Note the recommended method of accessing simulation features is
    to use CANdi.sim_state.

    :param device: Device to which this simulation state is attached
    :type device: CoreCANdi
    :param pwm1_orientation: The orientation of the PWM1 sensor relative to the robot chassis.
    :type pwm1_orientation: ChassisReference
    :param pwm2_orientation: The orientation of the PWM2 sensor relative to the robot chassis.
    :type pwm2_orientation: ChassisReference
    :param quadrature_orientation: The orientation of the Quadrature sensor relative to the robot chassis.
    :type quadrature_orientation: ChassisReference
    :param quadrature_edges_per_rotation: The number of quadrature edges per sensor rotation for an external quadrature sensor attached to the CANdi.
    :type quadrature_edges_per_rotation: int
    """

    __device_type = DeviceType.P6_CANdiType

    def __init__(self, device: 'CoreCANdi',
                 pwm1_orientation = ChassisReference.CounterClockwise_Positive,
                 pwm2_orientation = ChassisReference.CounterClockwise_Positive,
                 quadrature_orientation = ChassisReference.CounterClockwise_Positive,
                 quadrature_edges_per_rotation = 4096):
        self._id = device.device_id

        self.pwm1_orientation = pwm1_orientation
        """
        The orientation of the PWM1 sensor relative
        to the robot chassis.
        
        This value should not be changed based on the CANdi PWM1 invert.
        Rather, this value should be changed when the mechanical linkage
        between the sensor and the robot changes.
        """
        
        self.pwm2_orientation = pwm2_orientation
        """
        The orientation of the PWM2 sensor relative
        to the robot chassis.
        
        This value should not be changed based on the CANdi PWM2 invert.
        Rather, this value should be changed when the mechanical linkage
        between the sensor and the robot changes.
        """
        
        self.quadrature_orientation = quadrature_orientation
        """
        The orientation of the Quadrature sensor relative
        to the robot chassis.
        <p>
        This value should not be changed based on the CANdi Quadrature invert.
        Rather, this value should be changed when the mechanical linkage
        between the sensor and the robot changes.
        """
        
        self.quadrature_edges_per_rotation = quadrature_edges_per_rotation
        """
        The number of quadrature edges per sensor rotation for an external
        quadrature sensor attached to the CANdi.
        """

    def set_supply_voltage(self, volts: volt) -> StatusCode:
        """
        Sets the simulated supply voltage of the CANdi.

        The minimum allowed supply voltage is 4 V - values below this
        will be promoted to 4 V.

        :param volts: The supply voltage in Volts
        :type volts: volt
        :returns: Status code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"SupplyVoltage"), volts)
        )

    def set_output_current(self, current: ampere) -> StatusCode:
        """
        Sets the simulated output current of the CANdi.

        :param current: The output current
        :type current: ampere
        :returns: Status Code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"RequestedOutputCurrent"), current)
        )

    def set_pwm1_rise_rise(self, time: second) -> StatusCode:
        """
        Sets the simulated PWM1 Rise to Rise timing of the CANdi.

        :param time: The time between two Rise events
        :type time: second
        :returns: Status Code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM1RiseRise"), time)
        )

    def set_pwm1_rise_fall(self, time: second) -> StatusCode:
        """
        Sets the simulated PWM1 Rise to Fall timing of the CANdi.

        :param time: The time between the Rise and Fall events in seconds
        :type time: second
        :returns: Status Code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM1RiseFall"), time)
        )

    def set_pwm1_connected(self, connected: bool) -> StatusCode:
        """

        Sets whether a PWM sensor is connected to the S1 pin.

        :param connected: True if sensor is connected
        :type connected: bool
        :returns: Status Code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM1Connected"), 1 if connected else 0)
        )

    def set_pwm1_position(self, position: rotation) -> StatusCode:
        """
        Sets the simulated pulse width position of the CANdi. This is the position
        of an external PWM encoder connected to the S1 pin.

        :param position: The new position
        :type position: rotation
        :returns: Status Code
        :rtype: StatusCode
        """
        if self.pwm1_orientation == ChassisReference.Clockwise_Positive:
            position = -position
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM1Position"), position)
        )

    def set_pwm1_velocity(self, velocity: rotations_per_second) -> StatusCode:
        """
        Sets the simulated pulse width velocity of the CANdi. This is the velocity
        of an external PWM encoder connected to the S1 pin.

        :param velocity: The new velocity
        :type velocity: rotations_per_second
        :returns: Status Code
        :rtype: StatusCode
        """
        if self.pwm1_orientation == ChassisReference.Clockwise_Positive:
            velocity = -velocity
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM1Velocity"), velocity)
        )

    def set_pwm2_rise_rise(self, time: second) -> StatusCode:
        """
        Sets the simulated PWM2 Rise to Rise timing of the CANdi.

        :param time: The time between two Rise events
        :type time: second
        :returns: Status Code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM2RiseRise"), time)
        )

    def set_pwm2_rise_fall(self, time: second) -> StatusCode:
        """
        Sets the simulated PWM2 Rise to Fall timing of the CANdi.

        :param time: The time between the Rise and Fall events in seconds
        :type time: second
        :returns: Status Code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM2RiseFall"), time)
        )

    def set_pwm2_connected(self, connected: bool) -> StatusCode:
        """
        Sets whether a PWM sensor is connected to the S2 pin.

        :param connected: True if sensor is connected
        :type connected: bool
        :returns: Status Code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM2Connected"), 1 if connected else 0)
        )

    def set_pwm2_position(self, position: rotation) -> StatusCode:
        """
        Sets the simulated pulse width position of the CANdi. This is the position
        of an external PWM encoder connected to the S2 pin.

        :param position: The new position
        :type position: rotation
        :returns: Status Code
        :rtype: StatusCode
        """
        if self.pwm2_orientation == ChassisReference.Clockwise_Positive:
            position = -position
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM2Position"), position)
        )

    def set_pwm2_velocity(self, velocity: rotations_per_second) -> StatusCode:
        """
        Sets the simulated pulse width velocity of the CANdi. This is the velocity
        of an external PWM encoder connected to the S2 pin.

        :param velocity: The new velocity
        :type velocity: rotations_per_second
        :returns: Status Code
        :rtype: StatusCode
        """
        if self.pwm2_orientation == ChassisReference.Clockwise_Positive:
            velocity = -velocity
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"PWM2Velocity"), velocity)
        )

    def set_raw_quadrature_position(self, position: rotation) -> StatusCode:
        """
        Sets the simulated raw quadrature position of the CANdi.

        Inputs to this function over time should be continuous, as user calls of
        CANdi.set_quadrature_position will be accounted for in the callee.

        The CANdi integrates this to calculate the true reported quadrature position.

        When using the WPI Sim GUI, you will notice a readonly position and settable rawPositionInput.
        The readonly signal is the emulated position which will match self-test in Tuner and the hardware API.
        Changes to rawPositionInput will be integrated into the emulated position.
        This way a simulator can modify the position without overriding hardware API calls for home-ing the sensor.

        :param position: The raw position
        :type position: rotation
        :returns: Status Code
        :rtype: StatusCode
        """
        if self.quadrature_orientation == ChassisReference.Clockwise_Positive:
            position = -position
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"RawQuadraturePosition"), position * self.quadrature_edges_per_rotation)
        )

    def set_quadrature_velocity(self, velocity: rotations_per_second) -> StatusCode:
        """
        Sets the simulated pulse width velocity of the CANdi.

        :param velocity: The new velocity
        :type velocity: rotations_per_second
        :returns: Status Code
        :rtype: StatusCode
        """
        if self.quadrature_orientation == ChassisReference.Clockwise_Positive:
            velocity = -velocity
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"QuadratureVelocity"), velocity * self.quadrature_edges_per_rotation)
        )

    def set_s1_state(self, state: S1StateValue) -> StatusCode:
        """
        Sets the state of the S1 pin

        :param state: The state to set the S1 pin to
        :type state: S1StateValue
        :returns: Status Code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"S1State"), state.value)
        )

    def set_s2_state(self, state: S2StateValue) -> StatusCode:
        """
        Sets the state of the S2 pin

        :param state: The state to St the S2 pin to
        :type state: S2StateValue
        :returns: Status Code
        :rtype: StatusCode
        """
        return StatusCode(
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(self.__device_type.value, self._id, ctypes.c_char_p(b"S2State"), state.value)
        )
