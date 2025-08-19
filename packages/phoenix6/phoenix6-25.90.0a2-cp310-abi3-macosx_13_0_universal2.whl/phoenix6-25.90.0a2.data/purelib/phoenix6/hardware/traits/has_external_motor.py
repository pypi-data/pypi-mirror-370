"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

from phoenix6.status_signal import *
from phoenix6.units import *
from phoenix6.signals.spn_enums import ExternalMotorTempStatusValue

class HasExternalMotor():
    """
    Contains all status signals for motor controllers that support external motors.
    """
    def get_external_motor_temp_status(self, refresh: bool = True) -> StatusSignal[ExternalMotorTempStatusValue]:
        """
        Status of the temperature sensor of the external motor.
        
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: ExternalMotorTempStatus Status Signal Object
        :rtype: StatusSignal[ExternalMotorTempStatusValue]
        """
        ...
    
    def get_external_motor_temp(self, refresh: bool = True) -> StatusSignal[celsius]:
        """
        Temperature of the external motor.
        
        - Minimum Value: 0.0
        - Maximum Value: 255.0
        - Default Value: 0
        - Units: ℃
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: ExternalMotorTemp Status Signal Object
        :rtype: StatusSignal[celsius]
        """
        ...
    
    def get_five_v_rail_voltage(self, refresh: bool = True) -> StatusSignal[volt]:
        """
        The measured voltage of the 5V rail available on the JST and dataport
        connectors.
        
        - Minimum Value: 0.0
        - Maximum Value: 40.95
        - Default Value: 0
        - Units: Volts
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: FiveVRailVoltage Status Signal Object
        :rtype: StatusSignal[volt]
        """
        ...
    
    def get_analog_voltage(self, refresh: bool = True) -> StatusSignal[volt]:
        """
        The voltage of the analog pin (pin 3) of the Talon FXS data port. The
        analog pin reads a nominal voltage of 0-5V.
        
        - Minimum Value: 0
        - Maximum Value: 6
        - Default Value: 0
        - Units: Volts
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: AnalogVoltage Status Signal Object
        :rtype: StatusSignal[volt]
        """
        ...
    
    def get_raw_quadrature_position(self, refresh: bool = True) -> StatusSignal[rotation]:
        """
        The raw position retrieved from the connected quadrature encoder. This
        is only affected by the QuadratureEdgesPerRotation config. In most
        situations, the user should instead configure the
        ExternalFeedbackSensorSource and use the regular position getter.
        
        This signal must have its update frequency configured before it will
        have data.
        
        - Minimum Value: -16384.0
        - Maximum Value: 16383.999755859375
        - Default Value: 0
        - Units: rotations
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: RawQuadraturePosition Status Signal Object
        :rtype: StatusSignal[rotation]
        """
        ...
    
    def get_raw_quadrature_velocity(self, refresh: bool = True) -> StatusSignal[rotations_per_second]:
        """
        The raw velocity retrieved from the connected quadrature encoder. This
        is only affected by the QuadratureEdgesPerRotation config. In most
        situations, the user should instead configure the
        ExternalFeedbackSensorSource and use the regular velocity getter.
        
        This signal must have its update frequency configured before it will
        have data.
        
        - Minimum Value: -512.0
        - Maximum Value: 511.998046875
        - Default Value: 0
        - Units: rotations per second
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: RawQuadratureVelocity Status Signal Object
        :rtype: StatusSignal[rotations_per_second]
        """
        ...
    
    def get_raw_pulse_width_position(self, refresh: bool = True) -> StatusSignal[rotation]:
        """
        The raw position retrieved from the connected pulse-width encoder.
        This is not affected by any config. In most situations, the user
        should instead configure the ExternalFeedbackSensorSource and use the
        regular position getter.
        
        This signal must have its update frequency configured before it will
        have data.
        
        - Minimum Value: -16384.0
        - Maximum Value: 16383.999755859375
        - Default Value: 0
        - Units: rotations
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: RawPulseWidthPosition Status Signal Object
        :rtype: StatusSignal[rotation]
        """
        ...
    
    def get_raw_pulse_width_velocity(self, refresh: bool = True) -> StatusSignal[rotations_per_second]:
        """
        The raw velocity retrieved from the connected pulse-width encoder.
        This is not affected by any config. In most situations, the user
        should instead configure the ExternalFeedbackSensorSource and use the
        regular velocity getter.
        
        This signal must have its update frequency configured before it will
        have data.
        
        - Minimum Value: -512.0
        - Maximum Value: 511.998046875
        - Default Value: 0
        - Units: rotations per second
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: RawPulseWidthVelocity Status Signal Object
        :rtype: StatusSignal[rotations_per_second]
        """
        ...
    
    def get_fault_bridge_short(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Bridge was disabled most likely due to a short in the motor leads.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_BridgeShort Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    def get_sticky_fault_bridge_short(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Bridge was disabled most likely due to a short in the motor leads.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_BridgeShort Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    def get_fault_hall_sensor_missing(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Hall sensor signals are invalid.  Check hall sensor and cabling.  This
        fault can be used to detect when hall cable is unplugged.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_HallSensorMissing Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    def get_sticky_fault_hall_sensor_missing(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Hall sensor signals are invalid.  Check hall sensor and cabling.  This
        fault can be used to detect when hall cable is unplugged.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_HallSensorMissing Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    def get_fault_drive_disabled_hall_sensor(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Hall sensor signals are invalid during motor drive, so motor was
        disabled.  Check hall sensor and cabling.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_DriveDisabledHallSensor Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    def get_sticky_fault_drive_disabled_hall_sensor(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Hall sensor signals are invalid during motor drive, so motor was
        disabled.  Check hall sensor and cabling.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_DriveDisabledHallSensor Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    def get_fault_motor_temp_sensor_missing(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Motor temperature signal appears to not be connected.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_MotorTempSensorMissing Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    def get_sticky_fault_motor_temp_sensor_missing(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Motor temperature signal appears to not be connected.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_MotorTempSensorMissing Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    def get_fault_motor_temp_sensor_too_hot(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Motor temperature signal indicates motor is too hot.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_MotorTempSensorTooHot Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    def get_sticky_fault_motor_temp_sensor_too_hot(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Motor temperature signal indicates motor is too hot.
        
        - Default Value: False
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_MotorTempSensorTooHot Status Signal Object
        :rtype: StatusSignal[bool]
        """
        ...
    
    

    
    def clear_sticky_fault_bridge_short(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Bridge was disabled most likely due to a short in
        the motor leads.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
        ...
    
    def clear_sticky_fault_hall_sensor_missing(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Hall sensor signals are invalid.  Check hall
        sensor and cabling.  This fault can be used to detect when hall cable
        is unplugged.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
        ...
    
    def clear_sticky_fault_drive_disabled_hall_sensor(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Hall sensor signals are invalid during motor
        drive, so motor was disabled.  Check hall sensor and cabling.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
        ...
    
    def clear_sticky_fault_motor_temp_sensor_missing(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Motor temperature signal appears to not be
        connected.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
        ...
    
    def clear_sticky_fault_motor_temp_sensor_too_hot(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Motor temperature signal indicates motor is too
        hot.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
        ...

