#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for .comm sub-package tcp
"""

import logging
from collections.abc import Generator

import pytest

from hvl_ccb.comm.tcp import (
    Tcp,
    TcpCommunication,
    TcpCommunicationConfig,
    TcpCommunicationError,
)
from mocked_comm.tcp import RunningDeviceMockup, get_free_tcp_port

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def com_config():
    host = "localhost"
    return {
        "host": "127.0.0.1",
        "port": get_free_tcp_port(host),  # find a free TCP port dynamically
        "timeout": 0.1,
    }


def test_com_config(com_config) -> None:
    config = TcpCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"timeout": -0.1},
    ],
)
def test_invalid_config_dict(com_config, wrong_config_dict) -> None:
    invalid_config = dict(com_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        TcpCommunicationConfig(**invalid_config)


@pytest.fixture
def started_ts_tc(
    com_config,
) -> Generator[tuple[RunningDeviceMockup, TcpCommunication], None, None]:
    # Start server and listen
    ts = RunningDeviceMockup(port=com_config["port"], timeout=com_config["timeout"])
    # Connect with the client to the server
    tc = TcpCommunication(com_config)
    # Open/accept the connection from the client to the server
    with ts, tc:
        ts._starting.join()

        # Deactivate the `listen_and_answer`-feature, that eats all the data
        ts.keep_running = False
        ts._automatic_answer_thread.join()
        yield ts, tc


def test_ts_tc(started_ts_tc) -> None:
    ts, tc = started_ts_tc
    assert ts.__class__ is RunningDeviceMockup
    assert tc.__class__ is TcpCommunication
    assert ts._ts._client is not None
    ts.close()
    tc.close()


@pytest.fixture(scope="module")
def no_host_com_config():
    return {
        "port": 23,
        "timeout": 0.01,
    }


def test_old_tcp_class_name(com_config) -> None:
    with pytest.raises(DeprecationWarning):
        Tcp(com_config)


def test_no_host_given(no_host_com_config) -> None:
    with pytest.raises(AttributeError):
        TcpCommunication(no_host_com_config)


def test_open_and_close_tc(started_ts_tc) -> None:
    ts, tc = started_ts_tc
    assert tc.is_open
    tc.open()
    assert tc.is_open
    tc.close()
    assert not tc.is_open
    tc.close()
    assert not tc.is_open
    tc.open()
    assert tc.is_open


def test_write(started_ts_tc) -> None:
    ts, tc = started_ts_tc
    assert tc.is_open

    message = "bla"
    tc.write(message)
    assert ts.get_written() == message

    tc.close()
    with pytest.raises(TcpCommunicationError):
        tc.write(message)

    assert ts.get_written() == ""


def test_read(started_ts_tc) -> None:
    ts, tc = started_ts_tc
    assert tc.is_open

    message = "blub"
    ts.put_text(message)
    assert tc.read() == message

    ts.close()
    tc.close()

    assert not tc.is_open
    with pytest.raises(TcpCommunicationError):
        tc.read_bytes()


def test_encoding(started_ts_tc) -> None:
    ts, tc = started_ts_tc
    assert tc.is_open

    assert tc.read() == ""

    message = "bla"
    ts.put_text(message)

    message = "äöü"
    ts.put_text(message, encoding="latin-1")


def test_read_on_empty(started_ts_tc) -> None:
    ts, tc = started_ts_tc
    assert tc.is_open

    assert tc.read_nonempty() is None

    message = "bla"
    ts.put_text(message)
    assert tc.read_nonempty() == message
