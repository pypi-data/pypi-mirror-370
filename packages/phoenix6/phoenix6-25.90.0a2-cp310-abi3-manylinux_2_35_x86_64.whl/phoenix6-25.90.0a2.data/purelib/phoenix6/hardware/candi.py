"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

from phoenix6.hardware.core.core_candi import CoreCANdi

try:
    import hal
    from hal import SimDevice, simulation
    from wpilib import RobotBase

    from phoenix6 import utils
    from phoenix6.canbus import CANBus
    from phoenix6.phoenix_native import Native
    from phoenix6.sim.device_type import DeviceType
    from phoenix6.wpiutils.auto_feed_enable import AutoFeedEnable
    from phoenix6.wpiutils.replay_auto_enable import ReplayAutoEnable

    import copy
    import ctypes

    class CANdi(CoreCANdi):
        """
        Constructs a new CANdi object.

        :param device_id: ID of the device, as configured in Phoenix Tuner.
        :type device_id: int
        :param canbus: The CAN bus this device is on.
        :type canbus: CANBus, optional
        """

        __SIM_DEVICE_TYPE = DeviceType.P6_CANdiType

        def __init__(self, device_id: int, canbus: CANBus = CANBus()):
            CoreCANdi.__init__(self, device_id, canbus)

            # The StatusSignal getters are copies so that calls
            # to the WPI interface do not update any references

            if RobotBase.isSimulation():
                # run in both swsim and hwsim
                AutoFeedEnable.get_instance().start()
            if utils.is_replay():
                ReplayAutoEnable.get_instance().start()

            self.__sim_candi = SimDevice("CAN:CANdi (v6)", device_id)
            base = "CANdi (v6)[" + str(device_id) + "]/"

            self.__sim_pwm1 = SimDevice("CANDutyCycle:" + base + "PWM1")
            self.__sim_pwm2 = SimDevice("CANDutyCycle:" + base + "PWM2")
            self.__sim_quadrature = SimDevice("CANEncoder:" + base + "Quadrature")
            self.__sim_s1_dio = SimDevice("CANDIO:" + base + "S1")
            self.__sim_s2_dio = SimDevice("CANDIO:" + base + "S2")

            self.__sim_periodic_before_callback: simulation.SimCB | None = None
            self.__sim_value_changed_callbacks: list[simulation.SimValueCB] = []

            if self.__sim_candi:
                self.__sim_periodic_before_callback = simulation.registerSimPeriodicBeforeCallback(self.__on_periodic)

                self.__sim_supply_voltage = self.__sim_candi.createDouble("supplyVoltage", SimDevice.Direction.kInput, 12.0)
                self.__sim_requested_output_current = self.__sim_candi.createDouble("requestedOutputCurrent", SimDevice.Direction.kInput, 0)
                self.__sim_output_current = self.__sim_candi.createDouble("outputCurrent", SimDevice.Direction.kOutput, 0)

                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_supply_voltage, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_requested_output_current, self.__on_value_changed, True))


            if self.__sim_pwm1:
                self.__sim_pwm1_position = self.__sim_pwm1.createDouble("position", SimDevice.Direction.kInput, 0)
                self.__sim_pwm1_connected = self.__sim_pwm1.createBoolean("connected", SimDevice.Direction.kInput, True)
                self.__sim_pwm1_velocity = self.__sim_pwm1.createDouble("velocity", SimDevice.Direction.kInput, 0)
                self.__sim_pwm1_rise_rise = self.__sim_pwm1.createDouble("riseToRise", SimDevice.Direction.kInput, 0.004)
                self.__sim_pwm1_rise_fall = self.__sim_pwm1.createDouble("riseToFall", SimDevice.Direction.kInput, 0)

                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm1_position, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm1_connected, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm1_velocity, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm1_rise_rise, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm1_rise_fall, self.__on_value_changed, True))
            
            if self.__sim_pwm2:
                self.__sim_pwm2_position = self.__sim_pwm2.createDouble("position", SimDevice.Direction.kInput, 0)
                self.__sim_pwm2_connected = self.__sim_pwm2.createBoolean("connected", SimDevice.Direction.kInput, True)
                self.__sim_pwm2_velocity = self.__sim_pwm2.createDouble("velocity", SimDevice.Direction.kInput, 0)
                self.__sim_pwm2_rise_rise = self.__sim_pwm2.createDouble("riseToRise", SimDevice.Direction.kInput, 0.004)
                self.__sim_pwm2_rise_fall = self.__sim_pwm2.createDouble("riseToFall", SimDevice.Direction.kInput, 0)

                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm2_position, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm2_connected, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm2_velocity, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm2_rise_rise, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_pwm2_rise_fall, self.__on_value_changed, True))

            if self.__sim_quadrature:
            
                self.__sim_quadrature.createBoolean("init", SimDevice.Direction.kOutput, True)

                self.__sim_quad_pos = self.__sim_quadrature.createDouble("position", SimDevice.Direction.kOutput, 0)

                self.__sim_quad_raw_pos = self.__sim_quadrature.createDouble("rawPositionInput", SimDevice.Direction.kInput, 0)
                self.__sim_quad_vel = self.__sim_quadrature.createDouble("velocity", SimDevice.Direction.kInput, 0)

                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_quad_raw_pos, self.__on_value_changed, True))
                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_quad_vel, self.__on_value_changed, True))
            
            if self.__sim_s1_dio:
            
                self.__sim_s1_dio.createBoolean("init", SimDevice.Direction.kOutput, True)
                self.__sim_s1_dio.createBoolean("input", SimDevice.Direction.kOutput, True)
                self.__sim_s1_closed = self.__sim_s1_dio.createBoolean("value", SimDevice.Direction.kOutput, False)
                self.__sim_s1_state = self.__sim_s1_dio.createEnum("state", SimDevice.Direction.kInput, ["Floating", "Low", "High"], 0)

                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_s1_state, self.__on_value_changed, True))
            
            if self.__sim_s2_dio:
            
                self.__sim_s2_dio.createBoolean("init", SimDevice.Direction.kOutput, True)
                self.__sim_s2_dio.createBoolean("input", SimDevice.Direction.kOutput, True)
                self.__sim_s2_closed = self.__sim_s2_dio.createBoolean("value", SimDevice.Direction.kOutput, False)
                self.__sim_s2_state = self.__sim_s2_dio.createEnum("state", SimDevice.Direction.kInput, ["Floating", "Low", "High"], 0)

                self.__sim_value_changed_callbacks.append(simulation.registerSimValueChangedCallback(self.__sim_s2_state, self.__on_value_changed, True))
            

        def __enter__(self) -> 'CANdi':
            return self

        def __exit__(self, *_):
            self.close()

        def close(self):
            if self.__sim_periodic_before_callback is not None:
                self.__sim_periodic_before_callback.cancel()
                self.__sim_periodic_before_callback = None

            for callback in self.__sim_value_changed_callbacks:
                callback.cancel()
            self.__sim_value_changed_callbacks.clear()

            AutoFeedEnable.get_instance().stop()
            ReplayAutoEnable.get_instance().stop()

        # ----- Callbacks for Sim -----
        def __on_value_changed(self, name: str, handle: int, _: hal.SimValueDirection, value: hal.Value):
            device_name = simulation.getSimDeviceName(simulation.getSimValueDeviceHandle(handle))
            phys_type = device_name + ":" + name
            Native.instance().c_ctre_phoenix6_platform_sim_set_physics_input(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes(phys_type, 'utf-8')),
                float(value.value),
            )

        def __on_periodic(self):
            value = ctypes.c_double()
            err: int = 0

            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("SupplyVoltage", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_supply_voltage.set(value.value)

            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("RequestedOutputCurrent", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_requested_output_current.set(value.value)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("OutputCurrent", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_output_current.set(value.value)
            

            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM1Position", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm1_position.set(value.value)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM1Connected", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm1_connected.set(int(value.value) != 0)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM1Velocity", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm1_velocity.set(value.value)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM1RiseToRise", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm1_rise_rise.set(value.value)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM1RiseToFall", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm2_rise_fall.set(value.value)
            
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM2Position", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm2_position.set(value.value)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM2Connected", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm2_connected.set(int(value.value) != 0)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM2Velocity", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm2_velocity.set(value.value)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM2RiseToRise", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm2_rise_rise.set(value.value)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("PWM2RiseToFall", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_pwm2_rise_fall.set(value.value)
            

            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("QuadraturePosition", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_quad_pos.set(value.value)

            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("RawQuadraturePosition", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_quad_raw_pos.set(value.value)
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("QuadratureVelocity", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_quad_vel.set(value.value)
            

            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("S1State", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_s1_state.set(int(value.value))
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("S1Closed", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_s1_closed.set(int(value.value) != 0)
            

            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("S2State", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_s2_state.set(int(value.value))
            
            err = Native.instance().c_ctre_phoenix6_platform_sim_get_physics_value(
                self.__SIM_DEVICE_TYPE.value,
                self.device_id,
                ctypes.c_char_p(bytes("S2Closed", 'utf-8')),
                ctypes.byref(value),
            )
            if err == 0:
                self.__sim_s2_closed.set(int(value.value) != 0)
            

except ImportError:
    class CANdi(CoreCANdi):
        # Stub class to remove the "Core" string of CANdi
        pass
