"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

from typing import overload
from phoenix6.canbus import CANBus
from phoenix6.hardware.parent_device import ParentDevice, SupportsSendRequest
from phoenix6.spns.spn_value import SpnValue
from phoenix6.status_code import StatusCode
from phoenix6.status_signal import *
from phoenix6.units import *
from phoenix6.sim.device_type import DeviceType
from phoenix6.controls.modulate_v_bat_out import ModulateVBatOut
from phoenix6.controls.solid_color import SolidColor
from phoenix6.controls.empty_animation import EmptyAnimation
from phoenix6.controls.color_flow_animation import ColorFlowAnimation
from phoenix6.controls.fire_animation import FireAnimation
from phoenix6.controls.larson_animation import LarsonAnimation
from phoenix6.controls.rainbow_animation import RainbowAnimation
from phoenix6.controls.rgb_fade_animation import RgbFadeAnimation
from phoenix6.controls.single_fade_animation import SingleFadeAnimation
from phoenix6.controls.strobe_animation import StrobeAnimation
from phoenix6.controls.twinkle_animation import TwinkleAnimation
from phoenix6.controls.twinkle_off_animation import TwinkleOffAnimation
from phoenix6.configs.candle_configs import CANdleConfigurator
from phoenix6.sim.candle_sim_state import CANdleSimState

class CoreCANdle(ParentDevice):
    """
    Constructs a new CANdle object.

    :param device_id: ID of the device, as configured in Phoenix Tuner.
    :type device_id: int
    :param canbus: The CAN bus this device is on.
    :type canbus: CANBus, optional
    """

    def __init__(self, device_id: int, canbus: CANBus = CANBus()):
        super().__init__(device_id, "candle", canbus)
        self.configurator = CANdleConfigurator(self._device_identifier)

        Native.instance().c_ctre_phoenix6_platform_sim_create(DeviceType.P6_CANdleType.value, device_id)
        self.__sim_state = None


    @property
    def sim_state(self) -> CANdleSimState:
        """
        Get the simulation state for this device.

        This function reuses an allocated simulation state
        object, so it is safe to call this function multiple
        times in a robot loop.

        :returns: Simulation state
        :rtype: CANdleSimState
        """

        if self.__sim_state is None:
            self.__sim_state = CANdleSimState(self)
        return self.__sim_state


    def get_version_major(self, refresh: bool = True) -> StatusSignal[int]:
        """
        App Major Version number.
        
        - Minimum Value: 0
        - Maximum Value: 255
        - Default Value: 0
        - Units: 
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: VersionMajor Status Signal Object
        :rtype: StatusSignal[int]
        """
        return self._common_lookup(SpnValue.VERSION_MAJOR.value, None, "version_major", int, False, refresh)
    
    def get_version_minor(self, refresh: bool = True) -> StatusSignal[int]:
        """
        App Minor Version number.
        
        - Minimum Value: 0
        - Maximum Value: 255
        - Default Value: 0
        - Units: 
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: VersionMinor Status Signal Object
        :rtype: StatusSignal[int]
        """
        return self._common_lookup(SpnValue.VERSION_MINOR.value, None, "version_minor", int, False, refresh)
    
    def get_version_bugfix(self, refresh: bool = True) -> StatusSignal[int]:
        """
        App Bugfix Version number.
        
        - Minimum Value: 0
        - Maximum Value: 255
        - Default Value: 0
        - Units: 
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: VersionBugfix Status Signal Object
        :rtype: StatusSignal[int]
        """
        return self._common_lookup(SpnValue.VERSION_BUGFIX.value, None, "version_bugfix", int, False, refresh)
    
    def get_version_build(self, refresh: bool = True) -> StatusSignal[int]:
        """
        App Build Version number.
        
        - Minimum Value: 0
        - Maximum Value: 255
        - Default Value: 0
        - Units: 
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: VersionBuild Status Signal Object
        :rtype: StatusSignal[int]
        """
        return self._common_lookup(SpnValue.VERSION_BUILD.value, None, "version_build", int, False, refresh)
    
    def get_version(self, refresh: bool = True) -> StatusSignal[int]:
        """
        Full Version of firmware in device.  The format is a four byte value.
        
        - Minimum Value: 0
        - Maximum Value: 4294967295
        - Default Value: 0
        - Units: 
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Version Status Signal Object
        :rtype: StatusSignal[int]
        """
        return self._common_lookup(SpnValue.VERSION_FULL.value, None, "version", int, False, refresh)
    
    def get_fault_field(self, refresh: bool = True) -> StatusSignal[int]:
        """
        Integer representing all fault flags reported by the device.
        
        These are device specific and are not used directly in typical
        applications. Use the signal specific GetFault_*() methods instead.
        
        - Minimum Value: 0
        - Maximum Value: 4294967295
        - Default Value: 0
        - Units: 
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: FaultField Status Signal Object
        :rtype: StatusSignal[int]
        """
        return self._common_lookup(SpnValue.ALL_FAULTS.value, None, "fault_field", int, True, refresh)
    
    def get_sticky_fault_field(self, refresh: bool = True) -> StatusSignal[int]:
        """
        Integer representing all (persistent) sticky fault flags reported by
        the device.
        
        These are device specific and are not used directly in typical
        applications. Use the signal specific GetStickyFault_*() methods
        instead.
        
        - Minimum Value: 0
        - Maximum Value: 4294967295
        - Default Value: 0
        - Units: 
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFaultField Status Signal Object
        :rtype: StatusSignal[int]
        """
        return self._common_lookup(SpnValue.ALL_STICKY_FAULTS.value, None, "sticky_fault_field", int, True, refresh)
    
    def get_is_pro_licensed(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Whether the device is Phoenix Pro licensed.
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: IsProLicensed Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.VERSION_IS_PRO_LICENSED.value, None, "is_pro_licensed", bool, True, refresh)
    
    def get_supply_voltage(self, refresh: bool = True) -> StatusSignal[volt]:
        """
        Measured supply voltage to the CANdle.
        
        - Minimum Value: 0.0
        - Maximum Value: 32.767
        - Default Value: 0
        - Units: V
        
        Default Rates:
        - CAN 2.0: 10.0 Hz
        - CAN FD: 10.0 Hz (TimeSynced with Pro)
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: SupplyVoltage Status Signal Object
        :rtype: StatusSignal[volt]
        """
        return self._common_lookup(SpnValue.CANDLE_GENERAL_SUPPLY_VOLTAGE.value, None, "supply_voltage", volt, True, refresh)
    
    def get_five_v_rail_voltage(self, refresh: bool = True) -> StatusSignal[volt]:
        """
        The measured voltage of the 5V rail line.
        
        - Minimum Value: 0.0
        - Maximum Value: 10.23
        - Default Value: 0
        - Units: V
        
        Default Rates:
        - CAN 2.0: 10.0 Hz
        - CAN FD: 10.0 Hz (TimeSynced with Pro)
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: FiveVRailVoltage Status Signal Object
        :rtype: StatusSignal[volt]
        """
        return self._common_lookup(SpnValue.CANDLE_GENERAL_FIVE_V_RAIL_VOLTAGE.value, None, "five_v_rail_voltage", volt, True, refresh)
    
    def get_output_current(self, refresh: bool = True) -> StatusSignal[ampere]:
        """
        The measured output current. This includes both VBat and 5V output
        current.
        
        - Minimum Value: 0.0
        - Maximum Value: 10.23
        - Default Value: 0
        - Units: A
        
        Default Rates:
        - CAN 2.0: 10.0 Hz
        - CAN FD: 10.0 Hz (TimeSynced with Pro)
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: OutputCurrent Status Signal Object
        :rtype: StatusSignal[ampere]
        """
        return self._common_lookup(SpnValue.CANDLE_GENERAL_OUTPUT_CURRENT.value, None, "output_current", ampere, True, refresh)
    
    def get_device_temp(self, refresh: bool = True) -> StatusSignal[celsius]:
        """
        The temperature that the CANdle measures itself to be at.
        
        - Minimum Value: -128
        - Maximum Value: 127
        - Default Value: 0
        - Units: ℃
        
        Default Rates:
        - CAN 2.0: 10.0 Hz
        - CAN FD: 10.0 Hz (TimeSynced with Pro)
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: DeviceTemp Status Signal Object
        :rtype: StatusSignal[celsius]
        """
        return self._common_lookup(SpnValue.CANDLE_GENERAL_DEVICE_TEMP.value, None, "device_temp", celsius, True, refresh)
    
    def get_v_bat_modulation(self, refresh: bool = True) -> StatusSignal[float]:
        """
        The applied VBat modulation duty cycle.
        
        This signal will report 1.0 if the VBatOutputMode is configured to be
        always on, and 0.0 if configured to be always off. Otherwise, this
        will report the applied modulation from the last ModulateVBatOut
        request.
        
        - Minimum Value: 0.0
        - Maximum Value: 1.0
        - Default Value: 0
        - Units: frac
        
        Default Rates:
        - CAN 2.0: 10.0 Hz
        - CAN FD: 10.0 Hz (TimeSynced with Pro)
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: VBatModulation Status Signal Object
        :rtype: StatusSignal[float]
        """
        return self._common_lookup(SpnValue.CANDLE_GENERAL_V_BAT_MODULATION.value, None, "v_bat_modulation", float, True, refresh)
    
    def get_max_simultaneous_animation_count(self, refresh: bool = True) -> StatusSignal[int]:
        """
        The maximum number of simultaneous animations supported by the current
        version of CANdle firmware.
        
        Any control request using an animation slot greater than or equal to
        this signal will be ignored.
        
        - Minimum Value: 0
        - Maximum Value: 31
        - Default Value: 0
        - Units: 
        
        Default Rates:
        - CAN 2.0: 10.0 Hz
        - CAN FD: 10.0 Hz (TimeSynced with Pro)
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: MaxSimultaneousAnimationCount Status Signal Object
        :rtype: StatusSignal[int]
        """
        return self._common_lookup(SpnValue.CANDLE_GENERAL_MAX_SIMUL_ANIM_COUNT.value, None, "max_simultaneous_animation_count", int, True, refresh)
    
    def get_fault_hardware(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Hardware fault occurred
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_Hardware Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_HARDWARE.value, None, "fault_hardware", bool, True, refresh)
    
    def get_sticky_fault_hardware(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Hardware fault occurred
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_Hardware Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_HARDWARE.value, None, "sticky_fault_hardware", bool, True, refresh)
    
    def get_fault_undervoltage(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device supply voltage dropped to near brownout levels
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_Undervoltage Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_UNDERVOLTAGE.value, None, "fault_undervoltage", bool, True, refresh)
    
    def get_sticky_fault_undervoltage(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device supply voltage dropped to near brownout levels
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_Undervoltage Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_UNDERVOLTAGE.value, None, "sticky_fault_undervoltage", bool, True, refresh)
    
    def get_fault_boot_during_enable(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device boot while detecting the enable signal
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_BootDuringEnable Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_BOOT_DURING_ENABLE.value, None, "fault_boot_during_enable", bool, True, refresh)
    
    def get_sticky_fault_boot_during_enable(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device boot while detecting the enable signal
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_BootDuringEnable Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_BOOT_DURING_ENABLE.value, None, "sticky_fault_boot_during_enable", bool, True, refresh)
    
    def get_fault_unlicensed_feature_in_use(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        An unlicensed feature is in use, device may not behave as expected.
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_UnlicensedFeatureInUse Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_UNLICENSED_FEATURE_IN_USE.value, None, "fault_unlicensed_feature_in_use", bool, True, refresh)
    
    def get_sticky_fault_unlicensed_feature_in_use(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        An unlicensed feature is in use, device may not behave as expected.
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_UnlicensedFeatureInUse Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_UNLICENSED_FEATURE_IN_USE.value, None, "sticky_fault_unlicensed_feature_in_use", bool, True, refresh)
    
    def get_fault_overvoltage(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device supply voltage is too high (above 30 V).
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_Overvoltage Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_CANDLE_OVERVOLTAGE.value, None, "fault_overvoltage", bool, True, refresh)
    
    def get_sticky_fault_overvoltage(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device supply voltage is too high (above 30 V).
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_Overvoltage Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_CANDLE_OVERVOLTAGE.value, None, "sticky_fault_overvoltage", bool, True, refresh)
    
    def get_fault_5_v_too_high(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device 5V line is too high (above 6 V).
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_5VTooHigh Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_CANDLE_5_V_TOO_HIGH.value, None, "fault_5_v_too_high", bool, True, refresh)
    
    def get_sticky_fault_5_v_too_high(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device 5V line is too high (above 6 V).
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_5VTooHigh Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_CANDLE_5_V_TOO_HIGH.value, None, "sticky_fault_5_v_too_high", bool, True, refresh)
    
    def get_fault_5_v_too_low(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device 5V line is too low (below 4 V).
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_5VTooLow Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_CANDLE_5_V_TOO_LOW.value, None, "fault_5_v_too_low", bool, True, refresh)
    
    def get_sticky_fault_5_v_too_low(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device 5V line is too low (below 4 V).
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_5VTooLow Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_CANDLE_5_V_TOO_LOW.value, None, "sticky_fault_5_v_too_low", bool, True, refresh)
    
    def get_fault_thermal(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device temperature exceeded limit.
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_Thermal Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_CANDLE_THERMAL.value, None, "fault_thermal", bool, True, refresh)
    
    def get_sticky_fault_thermal(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        Device temperature exceeded limit.
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_Thermal Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_CANDLE_THERMAL.value, None, "sticky_fault_thermal", bool, True, refresh)
    
    def get_fault_software_fuse(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        CANdle output current exceeded the 6 A limit.
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_SoftwareFuse Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_CANDLE_SOFTWARE_FUSE.value, None, "fault_software_fuse", bool, True, refresh)
    
    def get_sticky_fault_software_fuse(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        CANdle output current exceeded the 6 A limit.
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_SoftwareFuse Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_CANDLE_SOFTWARE_FUSE.value, None, "sticky_fault_software_fuse", bool, True, refresh)
    
    def get_fault_short_circuit(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        CANdle has detected the output pin is shorted.
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: Fault_ShortCircuit Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.FAULT_CANDLE_SHORT_CIRCUIT.value, None, "fault_short_circuit", bool, True, refresh)
    
    def get_sticky_fault_short_circuit(self, refresh: bool = True) -> StatusSignal[bool]:
        """
        CANdle has detected the output pin is shorted.
        
        - Default Value: False
        
        Default Rates:
        - CAN: 4.0 Hz
        
        This refreshes and returns a cached StatusSignal object.
        
        :param refresh: Whether to refresh the StatusSignal before returning it; defaults to true
        :type refresh: bool
        :returns: StickyFault_ShortCircuit Status Signal Object
        :rtype: StatusSignal[bool]
        """
        return self._common_lookup(SpnValue.STICKY_FAULT_CANDLE_SHORT_CIRCUIT.value, None, "sticky_fault_short_circuit", bool, True, refresh)
    

    
    @overload
    def set_control(self, request: ModulateVBatOut) -> StatusCode:
        """
        Modulates the CANdle VBat output to the specified duty cycle. This can
        be used to control a single-color LED strip.
        
        Note that CANdleFeaturesConfigs.VBatOutputMode must be set to
        VBatOutputModeValue.Modulated.
        
        
        
        - ModulateVBatOut Parameters: 
            - output: Proportion of VBat to output in fractional units between 0.0 and
                      1.0.
    
        :param request: Control object to request of the device
        :type request: ModulateVBatOut
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: SolidColor) -> StatusCode:
        """
        Sets LEDs to a solid color.
        
        
        
        - SolidColor Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
            - color: The color to apply to the LEDs.
    
        :param request: Control object to request of the device
        :type request: SolidColor
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: EmptyAnimation) -> StatusCode:
        """
        An empty animation, clearing any animation in the specified slot.
        
        
        
        - EmptyAnimation Parameters: 
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
    
        :param request: Control object to request of the device
        :type request: EmptyAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: ColorFlowAnimation) -> StatusCode:
        """
        Animation that gradually lights the entire LED strip one LED at a
        time.
        
        
        
        - ColorFlowAnimation Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip
                               
                               If the start index is greater than the end index, the
                               direction will be reversed. The direction can also be
                               changed using the Direction parameter.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
                             
                             If the end index is less than the start index, the
                             direction will be reversed. The direction can also be
                             changed using the Direction parameter.
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
            - color: The color to use in the animation.
            - direction: The direction of the animation.
            - frame_rate: The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the LEDs,
                          turning one on or off.
    
        :param request: Control object to request of the device
        :type request: ColorFlowAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: FireAnimation) -> StatusCode:
        """
        Animation that looks similar to a flame flickering.
        
        
        
        - FireAnimation Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip
                               
                               If the start index is greater than the end index, the
                               direction will be reversed. The direction can also be
                               changed using the Direction parameter.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
                             
                             If the end index is less than the start index, the
                             direction will be reversed. The direction can also be
                             changed using the Direction parameter.
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
            - brightness: The brightness of the animation, as a scalar from 0.0 to 1.0.
            - direction: The direction of the animation.
            - sparking: The proportion of time in which sparks reignite the fire, as a
                        scalar from 0.0 to 1.0.
            - cooling: The rate at which the fire cools along the travel, as a scalar
                       from 0.0 to 1.0.
            - frame_rate: The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the LEDs,
                          advancing the animation of the fire.
    
        :param request: Control object to request of the device
        :type request: FireAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: LarsonAnimation) -> StatusCode:
        """
        Animation that bounces a pocket of light across the LED strip.
        
        
        
        - LarsonAnimation Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
            - color: The color to use in the animation.
            - size: The number of LEDs in the pocket of light, up to 15.
            - bounce_mode: The behavior of the pocket of light when it reaches the end
                           of the strip.
            - frame_rate: The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the LEDs,
                          advancing the pocket of light by one LED.
    
        :param request: Control object to request of the device
        :type request: LarsonAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: RainbowAnimation) -> StatusCode:
        """
        Animation that creates a rainbow throughout all the LEDs.
        
        
        
        - RainbowAnimation Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip
                               
                               If the start index is greater than the end index, the
                               direction will be reversed. The direction can also be
                               changed using the Direction parameter.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
                             
                             If the end index is less than the start index, the
                             direction will be reversed. The direction can also be
                             changed using the Direction parameter.
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
            - brightness: The brightness of the animation, as a scalar from 0.0 to 1.0.
            - direction: The direction of the animation.
            - frame_rate: The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the LEDs,
                          advancing the rainbow by about 3 degrees of hue (out of 360
                          degrees).
    
        :param request: Control object to request of the device
        :type request: RainbowAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: RgbFadeAnimation) -> StatusCode:
        """
        Animation that fades all the LEDs of a strip simultaneously between
        Red, Green, and Blue.
        
        
        
        - RgbFadeAnimation Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
            - brightness: The brightness of the animation, as a scalar from 0.0 to 1.0.
            - frame_rate: The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the LEDs,
                          adjusting the brightness of the LEDs by 1%.
    
        :param request: Control object to request of the device
        :type request: RgbFadeAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: SingleFadeAnimation) -> StatusCode:
        """
        Animation that fades into and out of a specified color.
        
        
        
        - SingleFadeAnimation Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
            - color: The color to use in the animation.
            - frame_rate: The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the LEDs,
                          adjusting the brightness of the LEDs by 1%.
    
        :param request: Control object to request of the device
        :type request: SingleFadeAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: StrobeAnimation) -> StatusCode:
        """
        Animation that strobes the LEDs a specified color.
        
        
        
        - StrobeAnimation Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
            - color: The color to use in the animation.
            - frame_rate: The frame rate of the animation, from [1, 500] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the LEDs,
                          turning all LEDs on or off.
    
        :param request: Control object to request of the device
        :type request: StrobeAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: TwinkleAnimation) -> StatusCode:
        """
        Animation that randomly turns LEDs on and off to a certain color.
        
        
        
        - TwinkleAnimation Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
            - color: The color to use in the animation.
            - max_leds_on_proportion: The max proportion of LEDs that can be on, in the
                                      range [0.1, 1.0].
            - frame_rate: The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the LEDs,
                          turning one on or off.
    
        :param request: Control object to request of the device
        :type request: TwinkleAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...
    
    @overload
    def set_control(self, request: TwinkleOffAnimation) -> StatusCode:
        """
        Animation that randomly turns on LEDs until it reaches the maximum
        count, and then turns them all off.
        
        
        
        - TwinkleOffAnimation Parameters: 
            - led_start_index: The index of the first LED this animation controls
                               (inclusive). Indices 0-7 control the onboard LEDs, and
                               8-399 control an attached LED strip.
            - led_end_index: The index of the last LED this animation controls
                             (inclusive). Indices 0-7 control the onboard LEDs, and
                             8-399 control an attached LED strip.
            - slot: The slot of this animation, within [0, 7]. Each slot on the CANdle
                    can store and run one animation.
            - color: The color to use in the animation.
            - max_leds_on_proportion: The max proportion of LEDs that can be on, in the
                                      range [0.1, 1.0].
            - frame_rate: The frame rate of the animation, from [2, 1000] Hz. This
                          determines the speed of the animation.
                          
                          A frame is defined as a transition in the state of the LEDs,
                          turning one LED on or all LEDs off.
    
        :param request: Control object to request of the device
        :type request: TwinkleOffAnimation
        :returns: Code response of the request
        :rtype: StatusCode
        """
        ...

    @overload
    def set_control(self, request: SupportsSendRequest) -> StatusCode:
        """
        Control device with generic control request object.

        If control request is not supported by device, this request
        will fail with StatusCode NotSupported

        :param request: Control object to request of the device
        :type request: SupportsSendRequest
        :returns: StatusCode of the request
        :rtype: StatusCode
        """
        ...

    def set_control(self, request: SupportsSendRequest) -> StatusCode:
        if isinstance(request, (ModulateVBatOut, SolidColor, EmptyAnimation, ColorFlowAnimation, FireAnimation, LarsonAnimation, RainbowAnimation, RgbFadeAnimation, SingleFadeAnimation, StrobeAnimation, TwinkleAnimation, TwinkleOffAnimation)):
            return self._set_control_private(request)
        return StatusCode.NOT_SUPPORTED

    
    def clear_sticky_faults(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear the sticky faults in the device.
        
        This typically has no impact on the device functionality.  Instead, it
        just clears telemetry faults that are accessible via API and Tuner
        Self-Test.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_faults(timeout_seconds)
    
    def clear_sticky_fault_hardware(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Hardware fault occurred
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_hardware(timeout_seconds)
    
    def clear_sticky_fault_undervoltage(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device supply voltage dropped to near brownout
        levels
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_undervoltage(timeout_seconds)
    
    def clear_sticky_fault_boot_during_enable(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device boot while detecting the enable signal
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_boot_during_enable(timeout_seconds)
    
    def clear_sticky_fault_unlicensed_feature_in_use(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: An unlicensed feature is in use, device may not
        behave as expected.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_unlicensed_feature_in_use(timeout_seconds)
    
    def clear_sticky_fault_overvoltage(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device supply voltage is too high (above 30 V).
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_overvoltage(timeout_seconds)
    
    def clear_sticky_fault_5_v_too_high(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device 5V line is too high (above 6 V).
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_5_v_too_high(timeout_seconds)
    
    def clear_sticky_fault_5_v_too_low(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device 5V line is too low (below 4 V).
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_5_v_too_low(timeout_seconds)
    
    def clear_sticky_fault_thermal(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device temperature exceeded limit.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_thermal(timeout_seconds)
    
    def clear_sticky_fault_software_fuse(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: CANdle output current exceeded the 6 A limit.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_software_fuse(timeout_seconds)
    
    def clear_sticky_fault_short_circuit(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: CANdle has detected the output pin is shorted.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        return self.configurator.clear_sticky_fault_short_circuit(timeout_seconds)

