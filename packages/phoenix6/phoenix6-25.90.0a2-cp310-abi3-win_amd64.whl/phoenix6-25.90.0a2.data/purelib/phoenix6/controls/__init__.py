"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

from . import compound
from .duty_cycle_out import DutyCycleOut
from .torque_current_foc import TorqueCurrentFOC
from .voltage_out import VoltageOut
from .position_duty_cycle import PositionDutyCycle
from .position_voltage import PositionVoltage
from .position_torque_current_foc import PositionTorqueCurrentFOC
from .velocity_duty_cycle import VelocityDutyCycle
from .velocity_voltage import VelocityVoltage
from .velocity_torque_current_foc import VelocityTorqueCurrentFOC
from .motion_magic_duty_cycle import MotionMagicDutyCycle
from .motion_magic_voltage import MotionMagicVoltage
from .motion_magic_torque_current_foc import MotionMagicTorqueCurrentFOC
from .differential_duty_cycle import DifferentialDutyCycle
from .differential_voltage import DifferentialVoltage
from .differential_position_duty_cycle import DifferentialPositionDutyCycle
from .differential_position_voltage import DifferentialPositionVoltage
from .differential_velocity_duty_cycle import DifferentialVelocityDutyCycle
from .differential_velocity_voltage import DifferentialVelocityVoltage
from .differential_motion_magic_duty_cycle import DifferentialMotionMagicDutyCycle
from .differential_motion_magic_voltage import DifferentialMotionMagicVoltage
from .follower import Follower
from .strict_follower import StrictFollower
from .differential_follower import DifferentialFollower
from .differential_strict_follower import DifferentialStrictFollower
from .neutral_out import NeutralOut
from .coast_out import CoastOut
from .static_brake import StaticBrake
from .music_tone import MusicTone
from .motion_magic_velocity_duty_cycle import MotionMagicVelocityDutyCycle
from .motion_magic_velocity_torque_current_foc import MotionMagicVelocityTorqueCurrentFOC
from .motion_magic_velocity_voltage import MotionMagicVelocityVoltage
from .motion_magic_expo_duty_cycle import MotionMagicExpoDutyCycle
from .motion_magic_expo_voltage import MotionMagicExpoVoltage
from .motion_magic_expo_torque_current_foc import MotionMagicExpoTorqueCurrentFOC
from .dynamic_motion_magic_duty_cycle import DynamicMotionMagicDutyCycle
from .dynamic_motion_magic_voltage import DynamicMotionMagicVoltage
from .dynamic_motion_magic_torque_current_foc import DynamicMotionMagicTorqueCurrentFOC
from .modulate_v_bat_out import ModulateVBatOut
from .solid_color import SolidColor
from .empty_animation import EmptyAnimation
from .color_flow_animation import ColorFlowAnimation
from .fire_animation import FireAnimation
from .larson_animation import LarsonAnimation
from .rainbow_animation import RainbowAnimation
from .rgb_fade_animation import RgbFadeAnimation
from .single_fade_animation import SingleFadeAnimation
from .strobe_animation import StrobeAnimation
from .twinkle_animation import TwinkleAnimation
from .twinkle_off_animation import TwinkleOffAnimation


__all__ = [
    "compound",
    "DutyCycleOut",
    "TorqueCurrentFOC",
    "VoltageOut",
    "PositionDutyCycle",
    "PositionVoltage",
    "PositionTorqueCurrentFOC",
    "VelocityDutyCycle",
    "VelocityVoltage",
    "VelocityTorqueCurrentFOC",
    "MotionMagicDutyCycle",
    "MotionMagicVoltage",
    "MotionMagicTorqueCurrentFOC",
    "DifferentialDutyCycle",
    "DifferentialVoltage",
    "DifferentialPositionDutyCycle",
    "DifferentialPositionVoltage",
    "DifferentialVelocityDutyCycle",
    "DifferentialVelocityVoltage",
    "DifferentialMotionMagicDutyCycle",
    "DifferentialMotionMagicVoltage",
    "Follower",
    "StrictFollower",
    "DifferentialFollower",
    "DifferentialStrictFollower",
    "NeutralOut",
    "CoastOut",
    "StaticBrake",
    "MusicTone",
    "MotionMagicVelocityDutyCycle",
    "MotionMagicVelocityTorqueCurrentFOC",
    "MotionMagicVelocityVoltage",
    "MotionMagicExpoDutyCycle",
    "MotionMagicExpoVoltage",
    "MotionMagicExpoTorqueCurrentFOC",
    "DynamicMotionMagicDutyCycle",
    "DynamicMotionMagicVoltage",
    "DynamicMotionMagicTorqueCurrentFOC",
    "ModulateVBatOut",
    "SolidColor",
    "EmptyAnimation",
    "ColorFlowAnimation",
    "FireAnimation",
    "LarsonAnimation",
    "RainbowAnimation",
    "RgbFadeAnimation",
    "SingleFadeAnimation",
    "StrobeAnimation",
    "TwinkleAnimation",
    "TwinkleOffAnimation",
]
