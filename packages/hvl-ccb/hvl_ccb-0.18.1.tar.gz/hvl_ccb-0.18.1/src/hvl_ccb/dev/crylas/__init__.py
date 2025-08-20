#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Device classes for a CryLas pulsed laser controller and a CryLas laser attenuator,
using serial communication.

There are three modes of operation for the laser
1. Laser-internal hardware trigger (default): fixed to 20 Hz and max energy per pulse.
2. Laser-internal software trigger (for diagnosis only).
3. External trigger: required for arbitrary pulse energy or repetition rate. Switch to
"external" on the front panel of laser controller for using option 3.

After switching on the laser with laser_on(), the system must stabilize
for some minutes. Do not apply abrupt changes of pulse energy or repetition rate.

Manufacturer homepage:
https://www.crylas.de/products/pulsed_laser.html
"""

from .crylas import (  # noqa: F401
    CryLasAttenuator,
    CryLasAttenuatorConfig,
    CryLasAttenuatorError,
    CryLasAttenuatorSerialCommunication,
    CryLasAttenuatorSerialCommunicationConfig,
    CryLasLaser,
    CryLasLaserConfig,
    CryLasLaserError,
    CryLasLaserNotReadyError,
    CryLasLaserSerialCommunication,
    CryLasLaserSerialCommunicationConfig,
)
