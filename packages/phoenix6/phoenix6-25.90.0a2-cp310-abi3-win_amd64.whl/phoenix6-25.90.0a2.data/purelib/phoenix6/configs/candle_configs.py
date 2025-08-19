"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

from phoenix6.configs.config_groups import *
from phoenix6.configs.parent_configurator import ParentConfigurator
from phoenix6.hardware.device_identifier import DeviceIdentifier
from phoenix6.status_code import StatusCode
from phoenix6.units import *


class CANdleConfiguration:
    """
    Class for CTR Electronics' CANdle® branded device, a device that controls LEDs
    over the CAN bus.

    This handles the configurations for CANdle
    """

    def __init__(self):

        self.future_proof_configs: bool = True
        """
        True if we should factory default newer unsupported configs,
        false to leave newer unsupported configs alone.

        This flag addresses a corner case where the device may have
        firmware with newer configs that didn't exist when this
        version of the API was built. If this occurs and this
        flag is true, unsupported new configs will be factory
        defaulted to avoid unexpected behavior.

        This is also the behavior in Phoenix 5, so this flag
        is defaulted to true to match.
        """

        
        self.custom_params: CustomParamsConfigs = CustomParamsConfigs()
        """
        Custom Params.
        
        Custom paramaters that have no real impact on controller.
        
        Parameter list:
        
        - CustomParamsConfigs.custom_param0
        - CustomParamsConfigs.custom_param1
        
        """
        
        
        self.led: LEDConfigs = LEDConfigs()
        """
        Configs related to CANdle LED control.
        
        All the configs related to controlling LEDs with the CANdle, including
        LED strip type and brightness.
        
        Parameter list:
        
        - LEDConfigs.strip_type
        - LEDConfigs.brightness_scalar
        - LEDConfigs.loss_of_signal_behavior
        
        """
        
        
        self.candle_features: CANdleFeaturesConfigs = CANdleFeaturesConfigs()
        """
        Configs related to general CANdle features.
        
        This includes configs such as disabling the 5V rail and the behavior
        of VBat output.
        
        Parameter list:
        
        - CANdleFeaturesConfigs.enable5_v_rail
        - CANdleFeaturesConfigs.v_bat_output_mode
        - CANdleFeaturesConfigs.status_led_when_active
        
        """
        
    
    def with_custom_params(self, new_custom_params: CustomParamsConfigs) -> 'CANdleConfiguration':
        """
        Modifies this configuration's custom_params parameter and returns itself for
        method-chaining and easier to use config API.
    
        Custom Params.
        
        Custom paramaters that have no real impact on controller.
        
        Parameter list:
        
        - CustomParamsConfigs.custom_param0
        - CustomParamsConfigs.custom_param1
        
    
        :param new_custom_params: Parameter to modify
        :type new_custom_params: CustomParamsConfigs
        :returns: Itself
        :rtype: CANdleConfiguration
        """
        self.custom_params = new_custom_params
        return self
    
    def with_led(self, new_led: LEDConfigs) -> 'CANdleConfiguration':
        """
        Modifies this configuration's led parameter and returns itself for
        method-chaining and easier to use config API.
    
        Configs related to CANdle LED control.
        
        All the configs related to controlling LEDs with the CANdle, including
        LED strip type and brightness.
        
        Parameter list:
        
        - LEDConfigs.strip_type
        - LEDConfigs.brightness_scalar
        - LEDConfigs.loss_of_signal_behavior
        
    
        :param new_led: Parameter to modify
        :type new_led: LEDConfigs
        :returns: Itself
        :rtype: CANdleConfiguration
        """
        self.led = new_led
        return self
    
    def with_candle_features(self, new_candle_features: CANdleFeaturesConfigs) -> 'CANdleConfiguration':
        """
        Modifies this configuration's candle_features parameter and returns itself for
        method-chaining and easier to use config API.
    
        Configs related to general CANdle features.
        
        This includes configs such as disabling the 5V rail and the behavior
        of VBat output.
        
        Parameter list:
        
        - CANdleFeaturesConfigs.enable5_v_rail
        - CANdleFeaturesConfigs.v_bat_output_mode
        - CANdleFeaturesConfigs.status_led_when_active
        
    
        :param new_candle_features: Parameter to modify
        :type new_candle_features: CANdleFeaturesConfigs
        :returns: Itself
        :rtype: CANdleConfiguration
        """
        self.candle_features = new_candle_features
        return self

    def __str__(self) -> str:
        """
        Provides the string representation
        of this object

        :returns: String representation of this object
        :rtype: str
        """
        ss = []
        ss.append("CANdleConfiguration")
        ss.append(str(self.custom_params))
        ss.append(str(self.led))
        ss.append(str(self.candle_features))
        return "\n".join(ss)


    def serialize(self) -> str:
        """
        Get the serialized form of this configuration

        :returns: Serialized form of this config group
        :rtype: str
        """
        ss = []
        ss.append(self.custom_params.serialize())
        ss.append(self.led.serialize())
        ss.append(self.candle_features.serialize())
        return "".join(ss)

    def deserialize(self, to_deserialize: str) -> StatusCode:
        """
        Take a string and deserialize it to this configuration

        :returns: Return code of the deserialize method
        :rtype: str
        """
        err: StatusCode = StatusCode.OK
        err = self.custom_params.deserialize(to_deserialize)
        err = self.led.deserialize(to_deserialize)
        err = self.candle_features.deserialize(to_deserialize)
        return err



class CANdleConfigurator(ParentConfigurator):
    """
 * Class for CTR Electronics' CANdle® branded device, a device that controls
 * LEDs over the CAN bus.

    This handles the configurations for CANdle
    """

    def __init__(self, id: DeviceIdentifier):
        super().__init__(id)

    def refresh(self, configs: SupportsSerialization, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Refreshes the values of the specified config group.

        Call to refresh the selected configs from the device.

        :param configs: The configs to refresh
        :type configs: name
        :param timeout_seconds: Maximum amount of time to wait when performing configuration
        :type timeout_seconds: second
        :returns: StatusCode of refreshing the configs
        :rtype: StatusCode
        """
        err, serialized_string = self._get_configs_private(timeout_seconds)
        if err.is_ok():
            # Only deserialize if we successfully got configs
            configs.deserialize(serialized_string)
        return err

    def apply(self, configs: SupportsSerialization, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Applies the contents of the specified config to the device.

        Call to apply the selected configs.

        :param configs: Configs to apply
        :type configs: SupportsSerialization
        :param timeout_seconds: Maximum amount of time to wait when performing configuration
        :type timeout_seconds: second
        :returns: StatusCode of the apply method
        :rtype: StatusCode
        """
        if hasattr(configs, "future_proof_configs"):
            # If this object has a future_proof_configs member variable, use it
            future_proof_configs = getattr(configs, "future_proof_configs")
        else:
            # Otherwise default to not using it so our config-groups don't overwrite other groups
            future_proof_configs = False
        return self._set_configs_private(configs.serialize(), timeout_seconds, future_proof_configs, False)

    
    def clear_sticky_faults(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear the sticky faults in the device.
        
        This typically has no impact on the device functionality.  Instead, it
        just clears telemetry faults that are accessible via API and Tuner
        Self-Test.
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.SPN_CLEAR_STICKY_FAULTS.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_hardware(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Hardware fault occurred
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_HARDWARE.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_undervoltage(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device supply voltage dropped to near brownout
        levels
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_UNDERVOLTAGE.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_boot_during_enable(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device boot while detecting the enable signal
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_BOOT_DURING_ENABLE.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_unlicensed_feature_in_use(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: An unlicensed feature is in use, device may not
        behave as expected.
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_UNLICENSED_FEATURE_IN_USE.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_overvoltage(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device supply voltage is too high (above 30 V).
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_CANDLE_OVERVOLTAGE.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_5_v_too_high(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device 5V line is too high (above 6 V).
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_CANDLE_5_V_TOO_HIGH.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_5_v_too_low(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device 5V line is too low (below 4 V).
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_CANDLE_5_V_TOO_LOW.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_thermal(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: Device temperature exceeded limit.
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_CANDLE_THERMAL.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_software_fuse(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: CANdle output current exceeded the 6 A limit.
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_CANDLE_SOFTWARE_FUSE.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    
    
    def clear_sticky_fault_short_circuit(self, timeout_seconds: second = 0.100) -> StatusCode:
        """
        Clear sticky fault: CANdle has detected the output pin is shorted.
        
        This is available in the configurator in case the user wants
        to initialize their device entirely without passing a device
        reference down to the code that performs the initialization.
        In this case, the user passes down the configurator object
        and performs all the initialization code on the object.
        
        :param timeout_seconds: Maximum time to wait up to in seconds.
        :type timeout_seconds: second
        :returns: StatusCode of the set command
        :rtype: StatusCode
        """
    
        value = ctypes.c_char_p()
        Native.instance().c_ctre_phoenix6_serialize_double(SpnValue.CLEAR_STICKY_FAULT_CANDLE_SHORT_CIRCUIT.value, 0, ctypes.byref(value))
        if value.value is not None:
            serialized = str(value.value, encoding='utf-8')
            Native.instance().c_ctre_phoenix6_free_memory(ctypes.byref(value))
        else:
            serialized = ""
        return self._set_configs_private(serialized, timeout_seconds, False, True)
    

