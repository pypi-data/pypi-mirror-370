#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#

import logging
from typing import cast

import numpy as np
import numpy.typing as npt

from hvl_ccb.utils.typing import Number
from hvl_ccb.utils.validation import validate_number

from .utils import preserve_type


class MapRanges:
    def __init__(
        self,
        range_1: tuple[Number, Number],
        range_2: tuple[Number, Number],
        dtype_1: npt.DTypeLike,
        dtype_2: npt.DTypeLike,
        logger=None,
    ) -> None:
        self.logger = logging.getLogger(__name__) if logger is None else logger

        self._check_dtype(dtype_1, "range 1")
        self._check_dtype(dtype_2, "range 2")

        self._check_range_type(range_1, dtype_1, "Range limits of range 1")
        self._check_range_type(range_2, dtype_2, "Range limits of range 2")

        self._range_1 = range_1
        self._range_2 = range_2
        self._type_1 = dtype_1
        self._type_2 = dtype_2

    @preserve_type
    def convert_to_range2(self, value: Number) -> Number:
        """
        convert a value from range 1 to range 2

        :param value: the value in range 1
        :return: the corresponding value in range 2
        """

        self._check_value(value, self._range_1, self._type_1, "Value in range 1")
        rr = cast("Number", np.interp(value, self._range_1, self._range_2))
        if np.issubdtype(self._type_2, np.integer):
            rr = cast("Number", np.around(rr, 0).astype(self._type_2))
        return rr

    @preserve_type
    def convert_to_range1(self, value: Number) -> Number:
        """
        convert a value from range 2 to range 1

        :param value: the value in range 2
        :return: the corresponding value in range 1
        """

        self._check_value(value, self._range_2, self._type_2, "Value in range 2")
        rr = cast("Number", np.interp(value, self._range_2, self._range_1))
        if np.issubdtype(self._type_1, np.integer):
            rr = cast("Number", np.around(rr, 0).astype(self._type_1))
        return rr

    def _check_dtype(self, dtype, arange_str):
        """
        Verifies that the given dtype is either int or float.
        Both python and numpy types are accepted.

        :param dtype: either python type or numpy type
        :param arange_str: name of range
        :raises TypeError: if dtype is not part of int or float
        """

        if not np.issubdtype(dtype, np.number) or np.issubdtype(
            dtype, np.complexfloating
        ):
            msg = (
                f"Type of {arange_str} is not supported by this class. Accepted are "
                "inherited types of 'np.number' (except for 'np.complexfloating'), "
                f"but {dtype} was entered."
            )
            self.logger.error(msg)
            raise TypeError(msg)

    def _check_range_type(self, arange, dtype, arange_str):
        """
        Verifies that the limits of range are of subtype of the specified dtype.

        :param arange: a tuple with two Numbers
        :param dtype: the dtype of the range.
        :param arange_str: name of range
        :raises TypeError: if the type of range is not a subtype of dtype
        """

        if np.issubdtype(dtype, np.floating):
            validate_number(arange_str, arange, logger=self.logger)
        else:
            validate_number(arange_str, arange, number_type=dtype, logger=self.logger)

    def _check_value(self, value, arange, dtype, arange_str):
        """
        Check if the value within the given range and is a subtype of dtype.

        :param value: the value to check
        :param arange: the range
        :param dtype: the dtype of the range
        :param arange_str: name of range
        :raises TypeError: if the type of value is not a subtype of dtype
        :raises ValueError: if value is outside of range
        """

        if np.issubdtype(dtype, np.floating):
            validate_number(arange_str, value, arange, logger=self.logger)
        elif np.all(np.mod(value, 1) == 0):
            # check if value can be cast to int, wrapper converts all values to float
            value = np.asarray(value, int)
            validate_number(
                arange_str, value, arange, number_type=dtype, logger=self.logger
            )
        else:
            msg = f"{value} needs to include only numbers type 'int'"
            self.logger.error(msg)
            raise TypeError(msg)


class _MapBitRange(MapRanges):
    """
    private class to rename convert methods to an appropriate name for
    conversions involving Bits. Range 2 is reserved for bit-values.
    """

    def __init__(
        self,
        range_1: tuple[Number, Number],
        bit: int,
        dtype_1: npt.DTypeLike,
        logger=None,
    ) -> None:
        super().__init__(
            range_1=range_1,
            range_2=(0, 2**bit - 1),
            dtype_1=dtype_1,
            dtype_2=int,
            logger=logger,
        )
        validate_number("bit", bit, (1, None), int, logger=self.logger)

    def convert_to_bits(self, value: Number) -> int:
        return cast("int", self.convert_to_range2(value))

    def convert_to_number(self, value: int) -> Number:
        return self.convert_to_range1(value)


class MapBitAsymRange(_MapBitRange):
    """
    Class to convert an asymmetric arbitrary range (0 to value) to a
    bit-range (0 to 2**bit - 1).
    """

    def __init__(
        self,
        value: Number,
        bit: int,
        dtype_1: npt.DTypeLike = float,
        logger=None,
    ) -> None:
        super().__init__(range_1=(0, value), bit=bit, dtype_1=dtype_1, logger=logger)


class MapBitSymRange(_MapBitRange):
    """
    Class to convert a symmetric arbitrary range (-value to value) to a
    bit-range (0 to 2**bit - 1).
    """

    def __init__(
        self,
        value: Number,
        bit: int,
        dtype_1: npt.DTypeLike = float,
        logger=None,
    ) -> None:
        super().__init__(
            range_1=(-value, value), bit=bit, dtype_1=dtype_1, logger=logger
        )
