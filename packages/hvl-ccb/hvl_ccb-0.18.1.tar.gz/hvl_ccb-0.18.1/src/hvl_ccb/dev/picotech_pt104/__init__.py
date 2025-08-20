#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Controller for the Pico Technology PT-104 temperature logger device.
The controller is written as a wrapper around Pico Technology driver for the PT-104
device.

This code is directly based on: https://github.com/trombastic/Pico_PT104/ .

Extra installation
~~~~~~~~~~~~~~~~~~

Pico Technology driver for the PT-104 device is available only on Windows and on Linux.

To use this PT-104 device wrapper:

1. install the :code:`hvl_ccb` package with a :code:`picotech` extra feature::

        $ pip install "hvl_ccb[picotech]"

   this will install the Python bindings for the library.

2. install the library

    * on Windows: download and install PicoSDK from https://www.picotech.com/downloads
      (choose "PicoLog Data Loggers" > "PT-104" > "Software");
    * on Linux:
        - for Ubuntu/Debian, install :code:`libusbpt104` from :code:`.deb` file found in
          https://labs.picotech.com/debian/pool/main/libu/libusbpt104/ (note: at the
          moment the PT-104 driver is not a part of the official :code:`picoscope`
          package; cf.
          https://www.picotech.com/support/topic40626.html );
        - for any other supported Linux distribution, follow instructions to install
          the "USB PT-104 devices" drivers in https://www.picotech.com/downloads/linux ;

"""

import sys

if sys.platform == "darwin":
    import warnings

    warnings.warn("\n\n  PicoSDK is not available for Darwin OSs\n", stacklevel=2)
else:
    try:
        from .picotech_pt104 import (  # noqa: F401
            Pt104,
            Pt104ChannelConfig,
            Pt104CommunicationType,
            Pt104DeviceConfig,
        )
    except (ImportError, ModuleNotFoundError):
        import warnings

        warnings.warn(
            "\n\n  "
            "To use PicoTech PT-104 device controller or related utilities install"
            "\n  "
            "PicoSDK and install the hvl_ccb library with a 'picotech' extra feature:"
            "\n\n  "
            "    $ pip install hvl_ccb[picotech]"
            "\n\n",
            stacklevel=2,
        )
