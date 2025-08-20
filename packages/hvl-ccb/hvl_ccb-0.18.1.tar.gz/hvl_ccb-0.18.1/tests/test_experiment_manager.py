#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the ExperimentManager class.
"""

from typing import NoReturn

import pytest

from hvl_ccb import ExperimentError, ExperimentManager, ExperimentStatus
from hvl_ccb.dev import Device, DeviceExistingError
from hvl_ccb.error import CCBError

# make Device instantiable
Device.__abstractmethods__ = frozenset()


class FailingDeviceError(CCBError):
    pass


class FailingDevice(Device):
    def start(self) -> NoReturn:
        raise FailingDeviceError

    def stop(self) -> NoReturn:
        raise FailingDeviceError


def test_manager() -> None:
    dev1 = Device()
    dev2 = Device()
    dev3 = Device()
    fail1 = FailingDevice()

    devicelist = {
        "dev1": dev1,
    }

    mgr = ExperimentManager(devicelist)

    # start / stop with failing device
    mgr.add_device("failing", fail1)
    with pytest.raises(ExperimentError):
        mgr.run()
    assert mgr.status == ExperimentStatus.ERROR
    assert mgr.is_error()

    with pytest.raises(ExperimentError):
        mgr.finish()
    assert mgr.status == ExperimentStatus.ERROR
    assert mgr.remove_device("failing") == fail1
    mgr.finish()
    assert mgr.status == ExperimentStatus.FINISHED

    # add device while running
    mgr.run()
    mgr.add_device("dev2", dev2)
    mgr.finish()

    # add failing device while running, add clean device while ERROR
    mgr.run()
    with pytest.raises(ExperimentError):
        mgr.add_device("failing", fail1)
    assert mgr.status == ExperimentStatus.ERROR

    with pytest.raises(ExperimentError):
        mgr.add_device("dev3", dev3)

    mgr.remove_device("failing")
    mgr.finish()

    # add existing device
    with pytest.raises(DeviceExistingError):
        mgr.add_device("dev1", dev3)


def test_manager_status() -> None:
    mgr = ExperimentManager({"dev1": Device()})

    assert mgr.status == ExperimentStatus.INITIALIZED

    assert not mgr.is_running()
    assert not mgr.is_finished()

    mgr.run()
    assert not mgr.is_finished()
    assert mgr.is_running()

    mgr.finish()
    assert mgr.is_finished()
    assert not mgr.is_running()

    mgr.start()
    mgr.stop()
