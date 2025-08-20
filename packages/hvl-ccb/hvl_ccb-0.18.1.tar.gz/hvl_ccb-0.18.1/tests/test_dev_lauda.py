#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Testing Lauda PRO RP245E driver. Makes use of the socket library (TCP comm).
"""

from collections.abc import Generator

import pytest

from hvl_ccb.dev.lauda import (
    LaudaProRp245e,
    LaudaProRp245eCommand,
    LaudaProRp245eCommandError,
    LaudaProRp245eConfig,
    LaudaProRp245eTcpCommunicationConfig,
)
from mocked_comm.tcp import LocalLaudaServer, get_free_tcp_port


@pytest.fixture
def com_config() -> dict[str, str | float | int | bytes]:
    host = "127.0.0.1"
    return {
        "host": host,
        "port": get_free_tcp_port(host),
        "wait_sec_read_text_nonempty": 0.01,
        "default_n_attempts_read_text_nonempty": 2,
        "terminator": b"\r\n",
        "timeout": 0.1,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {
        "operation_mode": 2,
        "control_mode": 0,
        "upper_temp": 200,
        "lower_temp": -50,
    }


@pytest.fixture
def started_lauda_server(
    com_config, dev_config
) -> Generator[tuple[LocalLaudaServer, LaudaProRp245e], None, None]:
    ts = LocalLaudaServer(
        port=com_config["port"],
        terminator=com_config["terminator"],
        timeout=com_config["timeout"],
    )
    lauda = LaudaProRp245e(com_config, dev_config)
    with ts, lauda:
        ts._starting.join()
        yield ts, lauda


def test_com_config(com_config) -> None:
    config = LaudaProRp245eTcpCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"wait_sec_pre_read_or_write": -0.5},
        {"terminator": b"NotATerminator"},
    ],
)
def test_invalid_com_config_dict(com_config, wrong_config_dict) -> None:
    invalid_config = dict(com_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        LaudaProRp245eTcpCommunicationConfig(**invalid_config)


def test_dev_config(dev_config) -> None:
    # currently there are no non-default config values

    lauda_config = LaudaProRp245eConfig()
    assert lauda_config

    config = LaudaProRp245eConfig(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"operation_mode": 123},
        {"control_mode": 123},
        {"lower_temp": -100},
        {"upper_temp": 300},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict) -> None:
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        LaudaProRp245eConfig(**invalid_config)


def test_started_devices(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.get_device_type() == "RP245 PRO"


def test_get_device_type(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.get_device_type() == "RP245 PRO"

    ts.custom_answer = "RP245"  # without the magic "PRO"...
    with pytest.raises(LaudaProRp245eCommandError):
        lauda.get_device_type()


def test_pause(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.pause() == LaudaProRp245eCommand.STOP


def test_read_error(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    ts.custom_answer = "ERR"
    with pytest.raises(LaudaProRp245eCommandError):
        lauda.start_ramp()


def test_run(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.run() == LaudaProRp245eCommand.START


def test_set_external_temp(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    ext = 20.00
    assert (
        lauda.set_external_temp(ext)
        == f"{LaudaProRp245eCommand.EXTERNAL_TEMP}{ext:.2f}"
    )


def test_set_temp_set_point(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    ext = 25.00
    assert (
        lauda.set_temp_set_point(ext)
        == f"{LaudaProRp245eCommand.TEMP_SET_POINT}{ext:.2f}"
    )


def test_correct_pump_level(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    ext = 3
    assert lauda.set_pump_level(ext) == f"{LaudaProRp245eCommand.PUMP_LEVEL}{ext}"


def test_wrong_pump_level(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    ext = 15
    with pytest.raises(ValueError):
        lauda.set_pump_level(ext)


def test_correct_control_mode(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    ext = 0
    assert lauda.set_control_mode(0) == f"{LaudaProRp245eCommand.CONT_MODE}{ext}"


def test_wrong_control_mode(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    with pytest.raises(ValueError):
        lauda.set_control_mode(6)


def test_correct_ramp_program(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    ext = 1
    assert lauda.set_ramp_program(ext) == f"{LaudaProRp245eCommand.RAMP_SELECT}{ext}"


def test_wrong_ramp_program(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    with pytest.raises(ValueError):
        lauda.set_ramp_program(6)


def test_start_ramp(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.start_ramp() == LaudaProRp245eCommand.RAMP_START


def test_pause_ramp(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.pause_ramp() == LaudaProRp245eCommand.RAMP_PAUSE


def test_continue_ramp(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.continue_ramp() == LaudaProRp245eCommand.RAMP_CONTINUE


def test_stop_ramp(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.stop_ramp() == LaudaProRp245eCommand.RAMP_STOP


def test_set_ramp_iterations(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    ext = 3
    assert (
        lauda.set_ramp_iterations(ext)
        == f"{LaudaProRp245eCommand.RAMP_ITERATIONS}{ext}"
    )


def test_reset_ramp(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.reset_ramp() == LaudaProRp245eCommand.RAMP_DELETE


def test_set_ramp_segment(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    temp = 10.00
    dur = 0
    tol = 0.00
    pump = 3
    segment = f"{temp:.2f}_{dur}_{tol:.2f}_{pump}"
    assert (
        lauda.set_ramp_segment(temp, dur, tol, pump)
        == f"{LaudaProRp245eCommand.RAMP_SET}{segment}"
    )


def test_get_bath_temp(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.get_bath_temp() == 25.00


def test_get_ext_temp(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    assert lauda.get_external_temp() == 25.00


def test_returns_error(started_lauda_server) -> None:
    ts, lauda = started_lauda_server

    with pytest.raises(LaudaProRp245eCommandError):
        lauda.com.query_command("FOOBAR")
