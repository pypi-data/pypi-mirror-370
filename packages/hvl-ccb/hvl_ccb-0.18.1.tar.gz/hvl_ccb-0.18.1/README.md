# HVL Common Code Base

[![PyPI version](https://img.shields.io/pypi/v/hvl_ccb?logo=PyPi)](https://pypi.org/project/hvl_ccb/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/hvl_ccb?logo=Python)](https://pypi.org/project/hvl_ccb/)
[![Pipeline status](https://img.shields.io/gitlab/pipeline/ethz_hvl/hvl_ccb/master?logo=gitlab)](https://gitlab.com/ethz_hvl/hvl_ccb/-/tree/master)
[![Coverage report](https://img.shields.io/gitlab/coverage/ethz_hvl/hvl_ccb/master?logo=gitlab)](https://gitlab.com/ethz_hvl/hvl_ccb/commits/master)
[![Documentation Status](https://img.shields.io/readthedocs/hvl_ccb?logo=read-the-docs)](https://hvl-ccb.readthedocs.io/en/stable/)
[![Development pipeline status](https://img.shields.io/gitlab/pipeline/ethz_hvl/hvl_ccb/devel?label=devel&logo=gitlab)](https://gitlab.com/ethz_hvl/hvl_ccb/-/tree/devel)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A unified Python framework, High Voltage Laboratory common code base (HVL CCB), for controlling devices used in high-voltage research. All implemented devices are used and tested in the High Voltage Laboratory [HVL](https://hvl.ee.ethz.ch/) of the Federal Institute of Technology Zurich ([ETH Zurich](https://ethz.ch/en.html)).

* Free software: GNU General Public License v3
* Copyright (c) 2019-2025 ETH Zurich, SIS ID and HVL D-ITET

## Getting Started

Install `hvl_ccb` with [`uv`](https://docs.astral.sh/uv/):

```console
  uv pip install hvl_ccb
```

More details about how to install, please refer to [`INSTALLATION.md`](https://gitlab.com/ethz_hvl/hvl_ccb/-/blob/devel/INSTALLATION.md?ref_type=heads).

Example code for each supported device can be found in [examples](https://gitlab.com/ethz_hvl/hvl_ccb/-/tree/devel/examples?ref_type=heads).

## Features

For managing multi-device experiments instantiate the `ExperimentManager`
utility class.

### Supported Devices

The device wrappers in `hvl_ccb` provide a standardised API with configuration
dataclasses, various settings and options, as well as start/stop methods.
Currently wrappers are available to control the following devices:

| Function/Type           | Devices |
|-------------------------|------------------------------------------------------------|
| Bench Multimeter        | Fluke 8845A and 8846A  |
|                         | 6.5 Digit Precision Multimeter  |
| Data acquisition        | LabJack (T4, T7, T7-PRO; requires [LJM Library](https://labjack.com/ljm))  |
|                         | Pico Technology PT-104 Platinum Resistance Data Logger (requires [PicoSDK](https://www.picotech.com/downloads)/[libusbpt104](https://labs.picotech.com/debian/pool/main/libu/libusbpt104/))  |
| Digital Delay Generator | Highland T560  |
| Digital IO              | LabJack (T4, T7, T7-PRO; requires [LJM Library](https://labjack.com/ljm))  |
| Experiment control      | HVL Cube with and without Power Inverter  |
| Filter      | Precision Filters Inc. PFA-2  |
| Gas Analyser            | MBW 973-SF6 gas dew point mirror analyzer  |
|                         | Pfeiffer Vacuum TPG (25x, 26x and 36x) controller for compact pressure gauges  |
|                         | SST Luminox oxygen sensor  |
| Laser                   | CryLaS pulsed laser  |
|                         | CryLaS laser attenuator  |
| Oscilloscope            | Rhode & Schwarz RTO 1024  |
|                         | TiePie (HS5, HS6, WS5)  |
| Power supply            | Elektro-Automatik PSI9000  |
|                         | FuG Elektronik  |
|                         | Heinzinger PNC  |
|                         | Technix capacitor charger  |
|                         | Korad Lab Bench DC Power Supply KA3000  |
| Stepper motor drive     | Newport SMC100PP  |
|                         | Schneider Electric ILS2T  |
| Temperature control     | Lauda PRO RP 245 E circulation thermostat  |
| Waveform generator      | TiePie (HS5, WS5)  |

Each device uses at least one standardised communication protocol wrapper.

### Communication protocols

In `hvl_ccb` by "communication protocol" we mean different levels of
communication standards, from the low level actual communication protocols like
serial communication to application level interfaces like VISA TCP standard. There
are also devices in `hvl_ccb` that use a dummy communication protocol;
this is because these devices are build on proprietary manufacturer libraries that
communicate with the corresponding devices, as in the case of TiePie or LabJack devices.

The communication protocol wrappers in `hvl_ccb` provide a standardised API with
configuration dataclasses, as well as open/close and read/write/query methods.
Currently, wrappers for the following communication protocols are available:

| Communication Protocol | Devices Using |
|------------------------|-------------------------------------------------------------|
| Modbus TCP             | Schneider Electric ILS2T stepper motor drive |
| OPC UA                 | HVL Cube with and without Power Inverter |
| Serial                 | CryLaS pulsed laser and laser attenuator |
|                        | FuG Elektronik power supply (e.g. capacitor charger HCK) using the Probus V protocol  |
|                        | Heinzinger PNC power supply using Heinzinger Digital Interface I/II  |
|                        | SST Luminox oxygen sensor  |
|                        | MBW 973-SF6 gas dew point mirror analyzer  |
|                        | Newport SMC100PP single axis driver for 2-phase stepper motors  |
|                        | Pfeiffer Vacuum TPG (25x, 26x and 36x) controller for compact pressure gauges  |
|                        | Technix capacitor charger  |
|                        | Korad Lab Bench DC Power Supply KA3000  |
| TCP                    | Digital Delay Generator Highland T560  |
|                        | Fluke 8845A and 8846  |
|                        | Lauda PRO RP 245 E circulation thermostat  |
|                        | Technix capacitor charger  |
| VISA TCP               | Elektro-Automatik PSI9000 DC power supply  |
|                        | Rhode & Schwarz RTO 1024 oscilloscope  |
| *Proprietary*          | LabJack (T4, T7, T7-PRO) devices, which communicate via [LJM Library](https://labjack.com/ljm)  |
|                        | Pico Technology PT-104 Platinum Resistance Data Logger, which communicates via [PicoSDK](https://www.picotech.com/downloads)/[libusbpt104](https://labs.picotech.com/debian/pool/main/libu/libusbpt104/)  |
|                        | TiePie (HS5, HS6, WS5) oscilloscopes and generators, which communicate via [LibTiePie SDK](https://www.tiepie.com/en/libtiepie-sdk)  |

### Sensor and Unit Conversion Utility

The Conversion Utility is a submodule that allows on the one hand a unified implementation of hardware-sensors and on the other hand provides a unified way to convert units. Furthermore it is possible to map two ranges on to each other. This can be useful to convert between for example and 4 - 20 mA and 0 - 10 V, both of them are common as sensor out- or input. Moreover, a subclass allows the mapping of a bit-range to any other range. For example a 12 bit number (0-4095) to 0 - 10. All utilities can be used with single numbers (`int`, `float`) as well as array-like structures containing single numbers (`np.array()`, `list`, `dict`, `tuple`).

Currently the following sensors are implemented:

* LEM LT 4000S
* LMT 70A

The following unit conversion classes are implemented:

* Temperature (Kelvin, Celsius, Fahrenheit)
* Pressure (Pascal, Bar, Atmosphere, Psi, Torr, Millimeter Mercury)

## Documentation

Note: if you're planning to contribute to the `hvl_ccb` project read
the [`CONTRIBUTING.md`](https://gitlab.com/ethz_hvl/hvl_ccb/-/blob/devel/CONTRIBUTING.md?ref_type=heads) section in the HVL CCB documentation.

Do either:

* read [HVL CCB documentation at RTD](https://readthedocs.org/projects/hvl-ccb/)

or

* build and read HVL CCB documentation locally; install first [Graphviz](https://graphviz.org/) (make sure
  to have the `dot` command in the executable search path) and the Python
  build requirements for documentation::

    ```console
    pip install docs/requirements.txt
    ```

  and then either on Windows in Git BASH run::

    ```console
    ./make.sh docs
    ```

  or from any other shell with GNU Make installed run::

    ```console
    make docs
    ```

  The target index HTML (`"docs/_build/html/index.html"`) should open
  automatically in your Web browser.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
