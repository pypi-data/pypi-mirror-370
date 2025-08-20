#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for .dev sub-package fluke8845a multimeter
"""

import logging

import pytest

from hvl_ccb.dev.fluke884x.base import (
    Fluke8845a,
    Fluke8845aError,
    MeasurementFunction,
    TriggerSource,
)
from mocked_comm.tcp import LocalFluke8845aServer, get_free_tcp_port

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def com_config():
    host = "127.0.0.1"
    return {
        "host": host,
        "port": get_free_tcp_port(host),
        "timeout": 0.01,
        "wait_sec_read_text_nonempty": 0.01,
        "default_n_attempts_read_text_nonempty": 2,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {}


@pytest.fixture
def start_fluke8845a(com_config, dev_config):
    # Start server and listen
    ts = LocalFluke8845aServer(port=com_config["port"], timeout=com_config["timeout"])
    fluke = Fluke8845a(com_config, dev_config)
    with ts, fluke:
        ts._starting.join()
        yield ts, fluke


def test_devices(start_fluke8845a) -> None:
    ts, fluke = start_fluke8845a
    assert ts is not None
    assert fluke.__class__ is Fluke8845a

    with pytest.raises(Fluke8845aError):
        fluke.display_enable = True


def test_identification_string(start_fluke8845a) -> None:
    ts, fluke = start_fluke8845a
    assert fluke.identification == "FLUKE,8845A,2540017,08/02/10-11:53"


def test_display(start_fluke8845a) -> None:
    ts, fluke = start_fluke8845a

    ts.custom_answer = "1"
    fluke.display_enable = True
    assert fluke.display_enable is True

    ts.custom_answer = '"123456789123"'
    fluke.display_message = "123456789123456"
    assert fluke.display_message == ts.custom_answer

    ts.custom_answer = ""
    fluke.clear_display_message()

    ts.custom_answer = "0"
    fluke.display_enable = False

    # if display fails
    ts.custom_answer = '"1234"'
    with pytest.raises(Fluke8845aError):
        fluke.display_message = "123"

    ts.custom_answer = "1"
    with pytest.raises(Fluke8845aError):
        fluke.display_enable = False


def test_input_function(start_fluke8845a) -> None:
    ts, fluke = start_fluke8845a

    with pytest.raises(Fluke8845aError):
        fluke.measurement_function = "TEST"

    ts.custom_answer = "CURR"
    with pytest.raises(Fluke8845aError):
        fluke.measurement_function = MeasurementFunction.VOLTAGE_AC

    ts.custom_answer = "HVL"
    with pytest.raises(Fluke8845aError):
        _ = fluke.measurement_function

    ts.custom_answer = "PER"
    fluke.measurement_function = MeasurementFunction.PERIOD


def test_current(start_fluke8845a) -> None:
    ts, fluke = start_fluke8845a

    ts.custom_answer = "CURR:AC"
    fluke.measurement_function = MeasurementFunction.CURRENT_AC
    assert fluke.measurement_function == "CURR:AC"

    ts.custom_answer = "1.0"
    fluke.ac_current_range = 0.8
    assert fluke.ac_current_range == 1.0

    ts.custom_answer = "20"
    fluke.current_filter = 20

    ts.custom_answer = "CURR:AC"
    assert fluke.measure() == 1.234

    ts.custom_answer = "3.0"
    with pytest.raises(Fluke8845aError):
        fluke.ac_current_range = 1.0


def test_trigger(start_fluke8845a) -> None:
    ts, fluke = start_fluke8845a

    with pytest.raises(Fluke8845aError):
        fluke.trigger_source = "BUSS"

    ts.custom_answer = "BUS"
    fluke.trigger_source = "BUS"
    assert fluke.trigger_source == "BUS"

    ts.custom_answer = "1.0"
    fluke.trigger_delay = 1
    assert fluke.trigger_delay == 1

    with pytest.raises(TypeError):
        fluke.trigger_delay = 1.0
    with pytest.raises(ValueError):
        fluke.trigger_delay = 4000

    ts.custom_answer = "BUS"
    with pytest.raises(Fluke8845aError):
        fluke.trigger_source = TriggerSource.EXTERNAL

    ts.custom_answer = "2.0"
    with pytest.raises(Fluke8845aError):
        fluke.trigger_delay = 1

    ts.custom_answer = "BUSS"
    with pytest.raises(Fluke8845aError):
        _ = fluke.trigger_source


def test_unit(start_fluke8845a) -> None:
    ts, fluke = start_fluke8845a

    ts.custom_answer = "CURR"
    fluke.measurement_function = MeasurementFunction.CURRENT_DC
    ts.custom_answer = "1.0"
    fluke.dc_current_range = 1.0

    ts.custom_answer = "VOLT"
    fluke.measurement_function = MeasurementFunction.VOLTAGE_DC
    ts.custom_answer = "1.0"
    fluke.dc_voltage_range = 1.0

    ts.custom_answer = "VOLT:AC"
    fluke.measurement_function = MeasurementFunction.VOLTAGE_AC
    ts.custom_answer = "1.0"
    fluke.ac_voltage_range = 1.0

    ts.custom_answer = "RES"
    fluke.measurement_function = MeasurementFunction.TWO_WIRE_RESISTANCE
    ts.custom_answer = "100.0"
    fluke.two_wire_resistance_range = 100.0

    ts.custom_answer = "FREQ"
    fluke.measurement_function = MeasurementFunction.FREQUENCY
    ts.custom_answer = "1.0"
    fluke.frequency_aperture = 1.0

    with pytest.raises(ValueError):
        fluke.dc_current_range = 100.0
    with pytest.raises(TypeError):
        fluke.dc_current_range = "test"
