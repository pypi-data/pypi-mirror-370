#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the dev.base module classes.
"""

from typing import NoReturn

import pytest

from hvl_ccb.comm import NullCommunicationProtocol
from hvl_ccb.configuration import EmptyConfig
from hvl_ccb.dev import (
    Device,
    DeviceExistingError,
    DeviceFailuresError,
    DeviceSequenceMixin,
    SingleCommDevice,
)

# make Device instantiable
Device.__abstractmethods__ = frozenset()


class DeviceFailStart(Device):
    def start(self) -> NoReturn:
        msg = "Error during start"
        raise ValueError(msg)

    def stop(self) -> None:
        pass


class DeviceFailStop(Device):
    def start(self) -> None:
        pass

    def stop(self) -> NoReturn:
        msg = "Error during start"
        raise ValueError(msg)


class DeviceSequence(DeviceSequenceMixin):
    pass


def test_device_sequence_access() -> None:
    dev = Device()

    ddict = {"dev": dev}

    dseq = DeviceSequence(ddict)

    assert dseq.get_device("dev") is dev

    for name, device in dseq.get_devices():
        assert ddict[name] is device

    # same devices, same sequence
    assert dseq == DeviceSequence(ddict)

    with pytest.raises(ValueError):
        dseq.remove_device("not there")

    with pytest.raises(DeviceExistingError):
        dseq.add_device("dev", dev)

    dev2 = Device()
    dseq.add_device("dev2", dev2)
    assert dseq.get_device("dev2") is dev2
    assert dseq != DeviceSequence(ddict)


def test_device_sequence_dot_lookup() -> None:
    dev1 = Device()
    dev2 = Device()

    ddict = {
        "dev1": dev1,
        "dev2": dev2,
    }

    seq = DeviceSequence(ddict)

    assert seq.dev1 is dev1
    assert seq.dev2 is dev2

    # adding device which name over-shadows attr/method
    with pytest.raises(ValueError):
        DeviceSequence({"dev1": dev1, "_devices": dev2})

    # adding single device which name over-shadows an attr/method
    with pytest.raises(ValueError):
        seq.add_device("start", Device())


class NullDevice(SingleCommDevice):
    @staticmethod
    def default_com_cls() -> type[NullCommunicationProtocol]:
        return NullCommunicationProtocol

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


def test_null_device() -> None:
    dev_config = EmptyConfig()
    for arg in (NullCommunicationProtocol({}), EmptyConfig(), {}, None):
        dev = NullDevice(arg, dev_config=dev_config)
        assert dev is not None
        assert isinstance(dev.com.config, EmptyConfig)

    with pytest.raises(TypeError):
        NullDevice(None, {"extra_key": 0})


def test_device_sequence_start() -> None:
    # case 1: some devices fail
    dev1 = Device()
    dev2 = DeviceFailStart()
    dev3 = Device()
    dev4 = DeviceFailStart()

    ddict = {
        "dev1": dev1,
        "dev2": dev2,
        "dev3": dev3,
        "dev4": dev4,
    }

    seq = DeviceSequence(ddict)
    # check that the error is raised
    with pytest.raises(DeviceFailuresError) as e:
        seq.start()
    # check the error arguments
    assert e.value.failures.keys() == seq.devices_failed_start.keys()
    assert all(isinstance(v, ValueError) for v in e.value.failures.values())

    assert seq.devices_failed_start == {"dev2": dev2, "dev4": dev4}
    assert not seq.devices_failed_stop

    # case 2: all devices work

    # removing failing devices
    seq.remove_device("dev2")
    seq.remove_device("dev4")
    assert seq._devices == {"dev1": dev1, "dev3": dev3}
    assert not seq.devices_failed_start

    seq.start()
    assert not seq.devices_failed_start
    assert not seq.devices_failed_stop


def test_device_sequence_stop() -> None:
    # case 1: some devices fail
    dev1 = Device()
    dev2 = DeviceFailStop()
    dev3 = Device()
    dev4 = DeviceFailStop()

    ddict = {
        "dev1": dev1,
        "dev2": dev2,
        "dev3": dev3,
        "dev4": dev4,
    }

    seq = DeviceSequence(ddict)
    # check that the error is raised
    with pytest.raises(DeviceFailuresError) as e:
        seq.stop()
    # check the error arguments
    assert e.value.failures.keys() == seq.devices_failed_stop.keys()
    assert all(isinstance(v, ValueError) for v in e.value.failures.values())

    assert seq.devices_failed_stop == {"dev2": dev2, "dev4": dev4}
    assert not seq.devices_failed_start

    # case 2: all devices work

    # removing failing devices
    seq.remove_device("dev2")
    seq.remove_device("dev4")
    assert seq._devices == {"dev1": dev1, "dev3": dev3}
    assert not seq.devices_failed_stop

    seq.stop()
    assert not seq.devices_failed_start
    assert not seq.devices_failed_stop
