#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#

import logging

import pytest

from hvl_ccb.dev.highland_t560.base import (
    AutoInstallMode,
    GateMode,
    T560Error,
    TriggerMode,
)
from hvl_ccb.dev.highland_t560.channel import Polarity
from hvl_ccb.dev.highland_t560.device import T560
from mocked_comm.tcp import LocalT560Server, get_free_tcp_port

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def com_config():
    host = "127.0.0.1"
    return {
        "host": host,
        "port": get_free_tcp_port(host),
        "timeout": 0.05,
        "wait_sec_read_text_nonempty": 0.05,
        "default_n_attempts_read_text_nonempty": 2,
    }


@pytest.fixture
def start_t560(com_config):
    ts = LocalT560Server(port=com_config["port"], timeout=com_config["timeout"])
    t560 = T560(com_config)
    with ts, t560:
        ts._starting.join()
        yield ts, t560


def test_devices(start_t560) -> None:
    ts, t560 = start_t560
    assert ts is not None
    assert t560.__class__ is T560


def test_error_response(start_t560) -> None:
    ts, t560 = start_t560
    with pytest.raises(T560Error):
        t560.com.query("Throw an error")


def test_device_settings(start_t560) -> None:
    ts, t560 = start_t560
    t560.activate_clock_output()
    t560.use_external_clock()
    t560.save_device_configuration()
    t560.load_device_configuration()
    t560.auto_install_mode = 0
    with pytest.raises(ValueError):
        t560.auto_install_mode = 3
    with pytest.raises(ValueError):
        t560.auto_install_mode = "OFF"
    assert t560.auto_install_mode == AutoInstallMode.OFF


def test_trigger_settings(start_t560) -> None:
    ts, t560 = start_t560
    t560.trigger_mode = TriggerMode.COMMAND
    assert t560.trigger_mode == TriggerMode.COMMAND
    with pytest.raises(ValueError):
        t560.trigger_level = 5
    t560.fire_trigger()
    t560.trigger_level = 2
    ts.response_dict["TR"] = "Trig REM HIZ Level 2.000 Div 00 SYN 00010000.00"
    assert t560.trigger_level == 2
    with pytest.raises(ValueError):
        t560.trigger_level = 5
    with pytest.raises(ValueError):
        t560.trigger_mode = "INT"
    t560.disarm_trigger()
    t560.frequency = 16_000_000
    ts.response_dict["TR"] = "Trig REM HIZ Level 1.250 Div 00 SYN 16,000,000"
    with pytest.raises(ValueError):
        t560.frequency = 20_000_000
    t560.period = 1e-7
    ts.response_dict["TR"] = "Trig REM HIZ Level 1.250 Div 00 SYN 10,000,000"
    with pytest.raises(ValueError):
        t560.period = 1e-8
    assert t560.period == 1e-7
    assert t560.frequency == 10_000_000
    ts.response_dict["TR"] = "T560 ERROR TEST"
    with pytest.raises(T560Error):
        assert t560._trigger_status


def test_gate_settings(start_t560) -> None:
    ts, t560 = start_t560
    t560.gate_mode = GateMode.INPUT
    with pytest.raises(ValueError):
        t560.gate_mode = "ON"
    assert t560.gate_mode == "INP"
    t560.gate_polarity = "NEG"
    ts.response_dict["GA"] = "Gate INP NEG HIZ Shots 0000000066"
    assert t560.gate_polarity == Polarity.ACTIVE_LOW
    ts.response_dict["GA"] = "T560 ERROR TEST"
    with pytest.raises(T560Error):
        assert t560._gate_status


def test_channel_settings(start_t560) -> None:
    ts, t560 = start_t560
    t560.ch_b.polarity = "NEG"
    with pytest.raises(ValueError):
        t560.ch_b.polarity = "+"
    assert t560.ch_b.polarity == Polarity.ACTIVE_LOW
    t560.ch_c.enabled = True
    assert t560.ch_c.enabled
    t560.ch_d.enabled = False
    with pytest.raises(TypeError):
        t560.ch_d.enabled = "YES"
    assert not t560.ch_d.enabled
    t560.ch_a.delay = 1e-6
    with pytest.raises(ValueError):
        t560.ch_a.delay = 100
    assert t560.ch_a.delay == 1e-6
    t560.ch_a.width = 1
    ts.response_dict["AS"] = "Ch A  POS  OFF  Dly  00.000,001  Wid  01.000,000"
    with pytest.raises(ValueError):
        t560.ch_a.width = -1
    assert t560.ch_a.width
    ts.response_dict["AS"] = "T560 ERROR TEST"
    with pytest.raises(T560Error):
        assert t560.ch_a._status
