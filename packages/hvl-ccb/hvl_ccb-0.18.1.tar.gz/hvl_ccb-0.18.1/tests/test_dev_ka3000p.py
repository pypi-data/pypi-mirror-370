#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the hvl_ccb.dev.ka3000p sub-package.
"""

import logging

import pytest

from hvl_ccb.dev.ka3000p import KA3000P, KA3000PError
from hvl_ccb.dev.ka3000p.base import KA3000PStatus, KA3000PTracking
from hvl_ccb.dev.ka3000p.comm import KA3000PCommunicationConfig
from masked_comm.serial import KA3000PLoopCommunication

logging.basicConfig(level=logging.ERROR)


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 9600,
        "parity": KA3000PCommunicationConfig.Parity.NONE,
        "stopbits": KA3000PCommunicationConfig.Stopbits.ONE,
        "bytesize": KA3000PCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\r\n",
        "timeout": 3,
        "wait_sec_read_text_nonempty": 0.01,
        "default_n_attempts_read_text_nonempty": 5,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {}


@pytest.fixture
def started_ka3000p_device(com_config, dev_config):
    serial_port = KA3000PLoopCommunication(com_config)
    serial_port.open()
    serial_port.put_text("KORAD KA3005P V5.9 SN:02738566")
    with KA3000P(serial_port, dev_config) as ka3000p:
        while serial_port.get_written() is not None:
            pass
        yield serial_port, ka3000p


def gen_responce_from_status(
    status: KA3000PStatus | None = None,
    *,
    ch1_cv=False,
    ch2_cv=False,
    beep=False,
    ocp=False,
    output=False,
    ovp=False,
) -> bytes:
    status = status or KA3000PStatus(
        ch1_cv=ch1_cv,
        ch2_cv=ch2_cv,
        tracking=KA3000PTracking.SINGLE,
        beep=beep,
        ocp=ocp,
        output=output,
        ovp=ovp,
    )

    status_bits: int = 0
    status_bits += status.ch1_cv << 0
    status_bits += status.ch2_cv << 1
    status_bits += status.tracking.value << 2
    status_bits += status.beep << 4
    status_bits += status.ocp << 5
    status_bits += status.output << 6
    status_bits += status.ovp << 7

    return status_bits.to_bytes(length=1, byteorder="big")


def test_com_config(com_config) -> None:
    config = KA3000PCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


def test_default_com(com_config) -> None:
    ka3000p = KA3000P(com_config)
    assert ka3000p


def test_broken_start(com_config, dev_config):
    serial_port = KA3000PLoopCommunication(com_config)

    ka3000p = KA3000P(serial_port, dev_config)
    assert not ka3000p.com.is_open
    serial_port.open()
    assert ka3000p.com.is_open
    with pytest.raises(KA3000PError):
        ka3000p.start()
    assert not ka3000p.com.is_open


def test_dev_init(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    assert ka3000p.max_voltage == 30
    assert ka3000p.max_current == 5

    assert ka3000p.brand == "KORAD"
    assert ka3000p.comm_version == "V5.9"
    assert ka3000p.serial_number == "02738566"


def test_wrong_identifier(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    com.put_text("KORADKA3005PV5.9SN:02738566")
    with pytest.raises(KA3000PError):
        ka3000p.idenify_device()


def test_broken_com(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    with pytest.raises(KA3000PError):
        ka3000p.idenify_device()


def test_voltage(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    # Read output voltage
    com.put_text("12.34")
    assert ka3000p.voltage == 12.34
    assert com.get_written() == "VOUT1?"

    # Set voltage
    ka3000p.voltage = 5.74
    assert com.get_written() == "VSET1:5.74"

    ka3000p.set_voltage = 4.56
    assert com.get_written() == "VSET1:4.56"

    # Read set voltage
    com.put_text("3.13")
    assert ka3000p.set_voltage == 3.13
    assert com.get_written() == "VSET1?"


def test_current(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    # Read output current
    com.put_text("1.234")
    assert ka3000p.current == 1.234
    assert com.get_written() == "IOUT1?"

    # Set current
    ka3000p.current = 4.74
    assert com.get_written() == "ISET1:4.740"

    ka3000p.set_current = 3.654
    assert com.get_written() == "ISET1:3.654"

    # Read set current
    com.put_text("0.135")
    assert ka3000p.set_current == 0.135
    assert com.get_written() == "ISET1?"


def test_status(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    status = KA3000PStatus(
        ch1_cv=False,
        ch2_cv=True,
        tracking=KA3000PTracking.SINGLE,
        beep=True,
        ocp=False,
        output=False,
        ovp=False,
    )
    status_byte = gen_responce_from_status(status)
    com.put_bytes(status_byte)
    assert ka3000p.status == status

    com.put_bytes(b"abc")
    with pytest.raises(KA3000PError):
        assert ka3000p.status

    com.put_bytes(b"")
    with pytest.raises(KA3000PError):
        assert ka3000p.status


def test_controlled_current_voltage(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    com.put_bytes(gen_responce_from_status(ch1_cv=False))
    assert ka3000p.controlled_current
    com.put_bytes(gen_responce_from_status(ch1_cv=False))
    assert not ka3000p.controlled_voltage

    com.put_bytes(gen_responce_from_status(ch1_cv=True))
    assert ka3000p.controlled_voltage
    com.put_bytes(gen_responce_from_status(ch1_cv=True))
    assert not ka3000p.controlled_current


def test_output(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    status_byte = gen_responce_from_status(status=None, output=False)
    com.put_bytes(status_byte)
    assert ka3000p.output is False
    assert com.get_written() == "STATUS?"

    status_byte = gen_responce_from_status(status=None, output=True)
    com.put_bytes(status_byte)
    assert ka3000p.output
    assert com.get_written() == "STATUS?"

    ka3000p.output = True
    assert com.get_written() == "OUT1"
    ka3000p.output = False
    assert com.get_written() == "OUT0"


def test_beep(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    status_byte = gen_responce_from_status(status=None, beep=False)
    com.put_bytes(status_byte)
    assert ka3000p.beep is False
    assert com.get_written() == "STATUS?"

    status_byte = gen_responce_from_status(status=None, beep=True)
    com.put_bytes(status_byte)
    assert ka3000p.beep
    assert com.get_written() == "STATUS?"

    ka3000p.beep = True
    assert com.get_written() == "BEEP1"
    ka3000p.beep = False
    assert com.get_written() == "BEEP0"


def test_lock(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    ka3000p.lock = True
    assert com.get_written() == "LOCK1"
    ka3000p.lock = False
    assert com.get_written() == "LOCK0"

    with pytest.raises(NotImplementedError):
        assert ka3000p.lock


def test_recall(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    ka3000p.recall = 3
    assert com.get_written() == "RCL3"

    with pytest.raises(ValueError):
        ka3000p.recall = -1
    with pytest.raises(ValueError):
        ka3000p.recall = 6
    with pytest.raises(TypeError):
        ka3000p.recall = 2.5

    with pytest.raises(NotImplementedError):
        assert ka3000p.recall


def test_save(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device
    ka3000p.save = 4
    assert com.get_written() == "SAV4"

    with ka3000p.save_settings_to(3):
        assert com.get_written() == "RCL3"
    assert com.get_written() == "SAV3"

    with pytest.raises(ValueError):
        ka3000p.save = -1
    with pytest.raises(ValueError):
        ka3000p.save = 6
    with pytest.raises(TypeError):
        ka3000p.save = 2.5

    with pytest.raises(NotImplementedError):
        assert ka3000p.save


def test_over_voltage_protection(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    status_byte = gen_responce_from_status(status=None, ovp=False)
    com.put_bytes(status_byte)
    assert not ka3000p.ovp
    assert com.get_written() == "STATUS?"

    status_byte = gen_responce_from_status(status=None, ovp=True)
    com.put_bytes(status_byte)
    assert ka3000p.ovp
    assert com.get_written() == "STATUS?"

    ka3000p.ovp = True
    assert com.get_written() == "OVP1"
    ka3000p.ovp = False
    assert com.get_written() == "OVP0"


def test_over_current_protection(
    started_ka3000p_device: tuple[KA3000PLoopCommunication, KA3000P],
) -> None:
    com, ka3000p = started_ka3000p_device

    status_byte = gen_responce_from_status(status=None, ocp=False)
    com.put_bytes(status_byte)
    assert not ka3000p.ocp
    assert com.get_written() == "STATUS?"

    status_byte = gen_responce_from_status(status=None, ocp=True)
    com.put_bytes(status_byte)
    assert ka3000p.ocp
    assert com.get_written() == "STATUS?"

    ka3000p.ocp = True
    assert com.get_written() == "OCP1"
    ka3000p.ocp = False
    assert com.get_written() == "OCP0"
