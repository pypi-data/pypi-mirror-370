"""
Copyright (C) Cross The Road Electronics.  All rights reserved.
License information can be found in CTRE_LICENSE.txt
For support and suggestions contact support@ctr-electronics.com or file
an issue tracker at https://github.com/CrossTheRoadElec/Phoenix-Releases
"""

from enum import Enum


class DeviceType(Enum):
    """
    Enumeration of all supported device types.
    """
    TalonSRXType = 0
    VictorSPXType = 1
    PigeonIMUType = 2
    RibbonPigeonIMUType = 3
    P6_TalonFXType = 4
    P6_CANcoderType = 5
    P6_Pigeon2Type = 6
    P6_TalonFXSType = 7
    P6_CANrangeType = 8
    P6_CANdiType = 9
    P6_CANdleType = 10

