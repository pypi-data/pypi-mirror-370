#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the OPC UA communication protocol.
"""

import sys
from time import sleep

import asyncua
import pytest
from pytest_mock import MockerFixture

from hvl_ccb.comm.opc import (
    OpcUaCommunication,
    OpcUaCommunicationConfig,
    OpcUaCommunicationIOError,
    OpcUaCommunicationTimeoutError,
    OpcUaSubHandler,
)
from masked_comm.opc import DemoServer
from masked_comm.utils import get_free_tcp_port

HOST = "127.0.0.1"
PORT = get_free_tcp_port(HOST)


@pytest.fixture(scope="module")
def com_config():
    return {
        "host": HOST,
        "port": PORT,
        "endpoint_name": "",
        "sub_handler": MySubHandler(),
        "wait_timeout_retry_sec": 0.01,
        "max_timeout_retry_nr": 3,
    }


def test_com_config(com_config) -> None:
    # test default values
    config = OpcUaCommunicationConfig(
        **{key: com_config[key] for key in OpcUaCommunicationConfig.required_keys()}
    )
    for key, value in OpcUaCommunicationConfig.optional_defaults().items():
        assert getattr(config, key) == value

    # test setting test values
    config = OpcUaCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"wait_timeout_retry_sec": -0.01},
        {"wait_timeout_retry_sec": 0},
        {"max_timeout_retry_nr": -1},
    ],
)
def test_invalid_config_dict(com_config, wrong_config_dict) -> None:
    invalid_config = dict(com_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        OpcUaCommunicationConfig(**invalid_config)


@pytest.fixture(scope="module")
def demo_opcua_server():
    opcua_server = DemoServer(100, "x", PORT)
    with opcua_server:
        yield opcua_server


@pytest.fixture(scope="module")
def connected_comm_protocol(com_config, demo_opcua_server):  # noqa: ARG001
    opc_comm = OpcUaCommunication(com_config)
    with opc_comm:
        yield opc_comm


class MySubHandler(OpcUaSubHandler):
    def __init__(self) -> None:
        self.change_counter = 0

    def datachange_notification(self, node, val, data) -> None:
        super().datachange_notification(node, val, data)
        self.change_counter += 1


def test_opcua_open_close(com_config, demo_opcua_server) -> None:  # noqa: ARG001
    # comm I/O errors on open
    config_dict = dict(com_config)
    for config_key, wrong_value in (
        ("host", "Not a host"),
        ("port", 0),
    ):
        config_dict[config_key] = wrong_value
        with pytest.raises(ValueError):
            OpcUaCommunication(config_dict)

    # successful open and close
    opc_comm = OpcUaCommunication(com_config)
    assert opc_comm is not None

    with pytest.raises(DeprecationWarning):
        assert opc_comm.is_open

    opc_comm.open()
    opc_comm.close()


def test_read(connected_comm_protocol, demo_opcua_server) -> None:
    demo_opcua_server.set_var("testvar_read", 1.23)
    assert connected_comm_protocol.read("testvar_read", 100) == 1.23


def test_write_read(com_config, demo_opcua_server) -> None:
    demo_opcua_server.set_var("testvar_write", 1.23)

    comm_protocol = OpcUaCommunication(com_config)

    with pytest.raises(OpcUaCommunicationIOError):
        comm_protocol.write("testvar_write", 100, 2.04)
    with pytest.raises(OpcUaCommunicationIOError):
        comm_protocol.read("testvar_write", 100)

    with comm_protocol:
        comm_protocol.write("testvar_write", 100, 2.04)
        assert comm_protocol.read("testvar_write", 100) == 2.04


def _test_write_client_error(
    raised_error: type(Exception),
    expected_error: type(OpcUaCommunicationIOError),
    com_config,
    demo_opcua_server: DemoServer,  # noqa: ARG001
    mocker: MockerFixture,
):
    comm_protocol = OpcUaCommunication(com_config)

    with comm_protocol:
        # patch UASocketProtocol.send_request to raise a mock TimeoutError as if coming
        # from used therein concurrent.futures.Future

        # Use bound method (otherwise live unpatch does not work):
        send_request_orig = comm_protocol._client.uaclient.protocol.send_request

        async def send_request(_self, request, *args, **kwargs):
            """
            Mocked from asyncua.client.ua_client.UASocketProtocol:
            async def send_request(self, request, timeout: Optional[float]
                = None, message_type=ua.MessageType.SecureMessage)
            """
            if isinstance(request, asyncua.ua.ReadRequest):
                msg = "mock error"
                raise raised_error(msg)
            # method already bound - ignore `self`
            return await send_request_orig(request, *args, **kwargs)

        mocker.patch(
            "asyncua.client.ua_client.UASocketProtocol.send_request",
            side_effect=send_request,
            autospec=True,
        )

        # check error caught and wrapped

        with pytest.raises(expected_error):
            comm_protocol.write("testvar_write", 100, 2.04)

        # comm is closed already on re-tries fails, but should be idempotent

        mocker.patch(
            "asyncua.client.ua_client.UASocketProtocol.send_request",
            side_effect=send_request_orig,
        )


def test_write_timeout_error(
    com_config,
    demo_opcua_server: DemoServer,
    mocker: MockerFixture,
) -> None:
    if sys.version_info < (3, 11):
        from concurrent.futures import TimeoutError as FuturesTimeoutError
    else:
        FuturesTimeoutError = TimeoutError  # noqa: N806

    _test_write_client_error(
        FuturesTimeoutError,
        OpcUaCommunicationTimeoutError,
        com_config,
        demo_opcua_server,
        mocker,
    )


def test_write_cancelled_error(
    com_config,
    demo_opcua_server: DemoServer,
    mocker: MockerFixture,
) -> None:
    from concurrent.futures import CancelledError

    _test_write_client_error(
        CancelledError,
        OpcUaCommunicationIOError,
        com_config,
        demo_opcua_server,
        mocker,
    )


def test_init_monitored_nodes(com_config, demo_opcua_server) -> None:
    demo_opcua_server.set_var("mon1", 0)
    demo_opcua_server.set_var("mon2", 0)
    demo_opcua_server.set_var("mon3", 0)

    comm_protocol = OpcUaCommunication(com_config)

    with pytest.raises(OpcUaCommunicationIOError):
        comm_protocol.init_monitored_nodes("mon1", 100)
    with pytest.raises(OpcUaCommunicationIOError):
        comm_protocol.init_monitored_nodes(["mon2", "mon3"], 100)

    with comm_protocol:
        comm_protocol.init_monitored_nodes("mon1", 100)
        comm_protocol.init_monitored_nodes(["mon2", "mon3"], 100)


def test_datachange(connected_comm_protocol, demo_opcua_server) -> None:
    demo_opcua_server.set_var("test_datachange", 0.1)
    connected_comm_protocol.init_monitored_nodes("test_datachange", 100)
    sleep(0.05)

    counter_before = connected_comm_protocol._sub_handler.change_counter
    sleep(1)
    demo_opcua_server.set_var("test_datachange", 0.2)
    assert demo_opcua_server.get_var("test_datachange") == 0.2
    sleep(0.05)
    counter_after = connected_comm_protocol._sub_handler.change_counter
    assert counter_after == counter_before + 1
