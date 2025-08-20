#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Module with base classes for devices.
"""

import logging
from abc import ABC, abstractmethod

from typing_extensions import Self

from hvl_ccb.comm import CommunicationProtocol
from hvl_ccb.configuration import ConfigurationMixin, configdataclass
from hvl_ccb.error import CCBError

logger = logging.getLogger(__name__)


class DeviceError(CCBError):
    pass


class DeviceExistingError(DeviceError):
    """
    Error to indicate that a device with that name already exists.
    """


class DeviceFailuresError(DeviceError):
    """
    Error to indicate that one or several devices failed.
    """

    def __init__(self, failures: dict[str, Exception]) -> None:
        super().__init__(failures)
        self.failures: dict[str, Exception] = failures
        """A dictionary of named devices failures (exceptions).
        """


@configdataclass
class EmptyConfig:
    """
    Empty configuration dataclass that is the default configuration for a Device.
    """


class Device(ConfigurationMixin, ABC):
    """
    Base class for devices. Implement this class for a concrete device,
    such as measurement equipment or voltage sources.

    Specifies the methods to implement for a device.
    """

    def __init__(self, dev_config=None) -> None:
        """
        Constructor for Device.
        """

        super().__init__(dev_config)

    @abstractmethod
    def start(self) -> None:
        """
        Start or restart this Device. To be implemented in the subclass.
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Stop this Device. To be implemented in the subclass.
        """

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    @staticmethod
    def config_cls():
        return EmptyConfig


class DeviceSequenceMixin:
    """
    Mixin that can be used on a device or other classes to provide facilities for
    handling multiple devices in a sequence.
    """

    def __init__(self, devices: dict[str, Device]) -> None:
        """
        Constructor for the DeviceSequenceMixin.

        :param devices: is a dictionary of devices to be added to this sequence.
        """

        super().__init__()

        self._devices: dict[str, Device] = {}
        for name, device in devices.items():
            self.add_device(name, device)

        self.devices_failed_start: dict[str, Device] = {}
        """Dictionary of named device instances from the sequence for which the most
        recent `start()` attempt failed.

        Empty if `stop()` was called last; cf. `devices_failed_stop`."""
        self.devices_failed_stop: dict[str, Device] = {}
        """Dictionary of named device instances from the sequence for which the most
        recent `stop()` attempt failed.

        Empty if `start()` was called last; cf. `devices_failed_start`."""

    def __getattribute__(self, item: str) -> Device | object:
        """
        Gets Device from the sequence or object's attribute.

        :param item: Item name to get
        :return: Device or object's attribute.
        """
        if item != "_devices" and item in self._devices:
            return self.get_device(item)
        return super().__getattribute__(item)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, DeviceSequenceMixin) and self._devices == other._devices
        )

    def get_devices(self) -> list[tuple[str, Device]]:
        """
        Get list of name, device pairs according to current sequence.

        :return: A list of tuples with name and device each.
        """
        return list(self._devices.items())

    def get_device(self, name: str) -> Device:
        """
        Get a device by name.

        :param name: is the name of the device.
        :return: the device object from this sequence.
        """

        return self._devices[name]

    def add_device(self, name: str, device: Device) -> None:
        """
        Add a new device to the device sequence.

        :param name: is the name of the device.
        :param device: is the instantiated Device object.
        :raise DeviceExistingError:
        """

        if name in self._devices:
            raise DeviceExistingError

        # disallow over-shadowing via ".DEVICE_NAME" lookup
        if hasattr(self, name):
            msg = (
                "This sequence already has an attribute called"
                f" {name}. Use different name for this device."
            )
            raise ValueError(msg)

        self._devices[name] = device

    def remove_device(self, name: str) -> Device:
        """
        Remove a device from this sequence and return the device object.

        :param name: is the name of the device.
        :return: device object or `None` if such device was not in the sequence.
        :raises ValueError: when device with given name was not found
        """

        if name not in self._devices:
            msg = f'No device named "{name}" in this sequence.'
            raise ValueError(msg)

        if name in self.devices_failed_start:
            self.devices_failed_start.pop(name)
        elif name in self.devices_failed_stop:
            self.devices_failed_stop.pop(name)

        return self._devices.pop(name)

    def start(self) -> None:
        """
        Start all devices in this sequence in their added order.

        :raises DeviceFailuresError: if one or several devices failed to start
        """

        # reset the failure dicts
        failures = {}
        self.devices_failed_start = {}
        self.devices_failed_stop = {}

        for name, device in self._devices.items():
            try:
                device.start()
            except Exception as exc:  # noqa: PERF203 Continue loop after exception
                logger.exception(f"Could not start {name}: ", exc_info=exc)
                failures[name] = exc
                self.devices_failed_start[name] = device
        if failures:
            raise DeviceFailuresError(failures)

    def stop(self) -> None:
        """
        Stop all devices in this sequence in their reverse order.

        :raises DeviceFailuresError: if one or several devices failed to stop
        """

        # reset the failure dicts
        failures: dict[str, Exception] = {}
        self.devices_failed_start = {}
        self.devices_failed_stop = {}

        for name, device in self._devices.items():
            try:
                device.stop()
            except Exception as exc:  # noqa: PERF203 Continue loop after exception
                logger.exception(f"Could not start {name}: ", exc_info=exc)
                failures[name] = exc
                self.devices_failed_stop[name] = device
        if failures:
            raise DeviceFailuresError(failures)


class SingleCommDevice(Device, ABC):
    """
    Base class for devices with a single communication protocol.
    """

    # Omitting typing hint `com: CommunicationProtocol` on purpose
    # to enable PyCharm autocompletion for subtypes.
    def __init__(self, com, dev_config=None) -> None:
        """
        Constructor for Device. Links the communication protocol and provides a
        configuration for the device.

        :param com: Communication protocol to be used with
            this device. Can be of type: - CommunicationProtocol instance, - dictionary
            with keys and values to be used as configuration together with the
            default communication protocol, or - @configdataclass to be used together
            with the default communication protocol.

        :param dev_config: configuration of the device. Can be:
            - None: empty configuration is used, or the specified config_cls()
            - @configdataclass decorated class
            - Dictionary, which is then used to instantiate the specified config_cls()
        """

        super().__init__(dev_config)

        if isinstance(com, CommunicationProtocol):
            self._com = com
        else:
            self._com = self.default_com_cls()(com)

    @staticmethod
    @abstractmethod
    def default_com_cls() -> type[CommunicationProtocol]:
        """
        Get the class for the default communication protocol used with this device.

        :return: the type of the standard communication protocol for this device
        """

    @property
    def com(self):  # noqa: ANN201
        """
        Get the communication protocol of this device.

        :return: an instance of CommunicationProtocol subtype
        """
        return self._com

    def start(self) -> None:
        """
        Open the associated communication protocol.
        """

        self.com.open()

    def stop(self) -> None:
        """
        Close the associated communication protocol.
        """

        self.com.close()
