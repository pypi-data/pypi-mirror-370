#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
A LabJack T-series devices wrapper around the LabJack's LJM Library; see
https://labjack.com/ljm .
The wrapper was originally developed and tested for a LabJack T7-PRO device.

Extra installation
~~~~~~~~~~~~~~~~~~

To use this LabJack T-series devices wrapper:

1. install the :code:`hvl_ccb` package with a :code:`labjack` extra feature::

        $ pip install "hvl_ccb[labjack]"

   this will install the Python bindings for the library.

2. install the library - follow instruction in
   https://labjack.com/support/software/installers/ljm .

"""

try:
    from .labjack import LabJack, LabJackError, LabJackIdentifierDIOError  # noqa: F401
except (ImportError, ModuleNotFoundError):
    import warnings

    warnings.warn(
        "\n\n  "
        "To use LabJack device controller or related utilities install LJM Library and"
        "\n  "
        "install the hvl_ccb library with a 'labjack' extra feature:"
        "\n\n  "
        "    pip install hvl_ccb[labjack]"
        "\n\n",
        stacklevel=2,
    )
