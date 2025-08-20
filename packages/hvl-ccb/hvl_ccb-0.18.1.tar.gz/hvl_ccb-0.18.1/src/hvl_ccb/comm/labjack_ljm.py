#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Communication protocol for LabJack using the LJM Library.
Originally developed and tested for LabJack T7-PRO.

Makes use of the LabJack LJM Library Python wrapper.
This wrapper needs an installation of the LJM Library for Windows, Mac OS X or Linux.
Go to:
https://labjack.com/support/software/installers/ljm
and
https://labjack.com/support/software/examples/ljm/python
"""

import logging
from collections.abc import Sequence

from labjack import ljm

from hvl_ccb._dev import labjack
from hvl_ccb.comm import CommunicationError, CommunicationProtocol
from hvl_ccb.configuration import configdataclass
from hvl_ccb.utils.enum import AutoNumberNameEnum
from hvl_ccb.utils.typing import Number

logger = logging.getLogger(__name__)


class LJMCommunicationError(CommunicationError):
    """
    Errors coming from LJMCommunication.
    """


@configdataclass
class LJMCommunicationConfig:
    """
    Configuration dataclass for :class:`LJMCommunication`.
    """

    DeviceType = labjack.DeviceType

    #: Can be either string 'ANY', 'T7_PRO', 'T7', 'T4', or of enum :class:`DeviceType`.
    device_type: str | labjack.DeviceType = "ANY"

    class ConnectionType(AutoNumberNameEnum):
        """
        LabJack connection type.
        """

        ANY = ()
        USB = ()
        TCP = ()
        ETHERNET = ()
        WIFI = ()

    #: Can be either string or of enum :class:`ConnectionType`.
    connection_type: str | ConnectionType = "ANY"

    identifier: str = "ANY"
    """
    The identifier specifies information for the connection to be used. This can
    be an IP address, serial number, or device name. See the LabJack docs (
    https://labjack.com/support/software/api/ljm/function-reference/ljmopens/\
identifier-parameter) for more information.
    """

    def clean_values(self) -> None:
        """
        Performs value checks on device_type and connection_type.
        """
        if not isinstance(self.device_type, self.DeviceType):
            self.force_value("device_type", self.DeviceType(self.device_type))  # type: ignore[attr-defined]

        if not isinstance(self.connection_type, self.ConnectionType):
            self.force_value(  # type: ignore[attr-defined]
                "connection_type", self.ConnectionType(self.connection_type)
            )


class LJMCommunication(CommunicationProtocol):
    """
    Communication protocol implementing the LabJack LJM Library Python wrapper.
    """

    def __init__(self, configuration) -> None:
        """
        Constructor for LJMCommunication.
        """
        super().__init__(configuration)

        # reference to the ctypes handle
        self._handle = None

    @staticmethod
    def config_cls():
        return LJMCommunicationConfig

    def open(self) -> None:
        """
        Open the communication port.
        """

        logger.info("Open connection")

        # open connection and store handle
        # may throw 1227 LJME_DEVICE_NOT_FOUND if device is not found
        try:
            with self.access_lock:
                self._handle = ljm.openS(
                    self.config.device_type.type_str,
                    str(self.config.connection_type),
                    str(self.config.identifier),
                )
        except ljm.LJMError as e:
            logger.exception("Error of LabJack LJM", exc_info=e)
            # only catch "1229 LJME_DEVICE_ALREADY_OPEN", never observed
            if e.errorCode != 1229:
                raise LJMCommunicationError from e

    def close(self) -> None:
        """
        Close the communication port.
        """

        logger.info("Closing connection")

        try:
            with self.access_lock:
                ljm.close(self._handle)
        except ljm.LJMError as e:
            logger.exception("Error of LabJack LJM", exc_info=e)
            # only catch "1224 LJME_DEVICE_NOT_OPEN", thrown on invalid handle
            if e.errorCode != 1224:
                raise LJMCommunicationError from e
        self._handle = None

    @property
    def is_open(self) -> bool:
        """
        Flag indicating if the communication port is open.

        :return: `True` if the port is open, otherwise `False`
        """
        # getHandleInfo does not work with LJM DEMO_MODE - consider it always opened
        # if only set
        if str(self._handle) == labjack.constants.DEMO_MODE:
            return True

        try:
            ljm.getHandleInfo(self._handle)
        except ljm.LJMError as e:
            if e.errorCode == 1224:  # "1224 LJME_DEVICE_NOT_OPEN"
                logger.warning("Error of LabJack LJM: '1224 LJME_DEVICE_NOT_OPEN'")
                return False
            logger.exception("Error of LabJack LJM", exc_info=e)
            raise LJMCommunicationError from e
        return True

    def __del__(self) -> None:
        """
        Finalizer, closes port
        """

        self.close()

    @staticmethod
    def _cast_read_value(
        name: str,
        val: Number,
        return_num_type: type[Number] = float,
        # see: https://github.com/python/mypy/issues/3186
    ) -> Number:
        """
        Cast a read value to a numeric type, performing some extra cast validity checks.

        :param name: name of the read value, only for error reporting
        :param val: value to cast
        :param return_num_type: optional numeric type specification for return values;
            by default `float`
        :return: input value `val` casted to `return_num_type`
        :raises TypeError: if read value of type not compatible with `return_num_type`
        """
        # Note: the underlying library returns already `float` (or
        # `ctypes.c_double`?); but defensively cast again via `str`:
        # 1) in case the underlying lib behaviour changes, and
        # 2) to raise `TypeError` when got non integer `float` value and expecting
        #    `int` value
        invalid_value_type = False
        try:
            fval = float(str(val))
            if issubclass(return_num_type, int) and not fval.is_integer():
                invalid_value_type = True
            else:
                ret = return_num_type(fval)
        except ValueError:
            invalid_value_type = True
        if invalid_value_type:
            msg = (
                f"Expected {return_num_type} value for '{name}' "
                f"name, got {type(val)} value of {val}"
            )
            logger.exception(msg)
            raise TypeError(msg)
        return ret

    def read_name(
        self,
        *names: str,
        return_num_type: type[Number] = float,
        # see: https://github.com/python/mypy/issues/3186
    ) -> Number | Sequence[Number]:
        """
        Read one or more input numeric values by name.

        :param names: one or more names to read out from the LabJack
        :param return_num_type: optional numeric type specification for return values;
            by default `float`.
        :return: answer of the LabJack, either single number or multiple numbers in a
            sequence, respectively, when one or multiple names to read were given
        :raises TypeError: if read value of type not compatible with `return_num_type`
        """

        # Errors that can be returned here:
        # 1224 LJME_DEVICE_NOT_OPEN if the device is not open
        # 1239 LJME_DEVICE_RECONNECT_FAILED if the device was opened, but connection
        #   lost

        with self.access_lock:
            try:
                if len(names) == 1:
                    ret = ljm.eReadName(self._handle, names[0])
                    ret = self._cast_read_value(
                        names[0], ret, return_num_type=return_num_type
                    )
                else:
                    ret = ljm.eReadNames(self._handle, len(names), names)
                    for i, (iname, iret) in enumerate(zip(names, ret, strict=False)):
                        ret[i] = self._cast_read_value(
                            iname, iret, return_num_type=return_num_type
                        )
            except ljm.LJMError as e:
                logger.exception("Error of LabJack LJM", exc_info=e)
                raise LJMCommunicationError from e

        return ret

    def write_name(self, name: str, value: Number) -> None:
        """
        Write one value to a named output.

        :param name: String or with name of LabJack IO
        :param value: is the value to write to the named IO port
        """

        with self.access_lock:
            try:
                ljm.eWriteName(self._handle, name, value)
            except ljm.LJMError as e:
                logger.exception("Error of LabJack LJM", exc_info=e)
                raise LJMCommunicationError from e

    def write_names(self, name_value_dict: dict[str, Number]) -> None:
        """
        Write more than one value at once to named outputs.

        :param name_value_dict: is a dictionary with string names of LabJack IO as keys
            and corresponding numeric values
        """
        names = list(name_value_dict.keys())
        values = list(name_value_dict.values())
        with self.access_lock:
            try:
                ljm.eWriteNames(self._handle, len(names), names, values)
            except ljm.LJMError as e:
                logger.exception("Error of LabJack LJM", exc_info=e)
                raise LJMCommunicationError from e
