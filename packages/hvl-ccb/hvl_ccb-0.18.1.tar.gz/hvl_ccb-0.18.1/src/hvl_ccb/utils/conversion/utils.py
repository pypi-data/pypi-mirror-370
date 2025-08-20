#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#

import enum
import logging
from types import FunctionType
from typing import Any, cast

import aenum
import numpy as np
import numpy.typing as npt
from typing_extensions import Self

from hvl_ccb.utils.validation import validate_number

logger = logging.getLogger(__name__)


def preserve_type(func):  # noqa: ANN201
    """
    This wrapper preserves the first order type of the input.
    Upto now the type of the data stored in a list, tuple, array or dict
    is not preserved.
    Integer will be converted to float!
    """

    def wrap(self, value, **kwargs):
        validate_number("value", value, (-np.inf, np.inf), logger=logger)

        is_dict = False

        if isinstance(value, dict):
            keys = list(value.keys())
            value = list(value.values())
            is_dict = True

        value_func = np.asarray(value, dtype=float)

        value_func = func(self, value_func, **kwargs)

        if is_dict:  # as 'value' is now list
            value = dict(zip(keys, list(value_func), strict=False))
        elif isinstance(value, list):
            value = list(value_func)
        elif isinstance(value, tuple) and hasattr(value, "_fields"):
            value = type(value)(*value_func)
        elif isinstance(value, tuple):
            value = tuple(value_func)
        elif isinstance(value, int | float) and not isinstance(value, np.generic):
            value = float(value_func)
        else:
            value = value_func
        return value

    return wrap


def convert_value_to_str(*value: npt.NDArray) -> list[str | list[str]]:
    """
    Converts two sets of values to strings. This is necessary because a 0-dim array
    needs different treatment than a 1-dim array

    :param value: array of values either 0-dim or 1-dim
    :return:converted se
    """
    value_str: list[str | list[str]] = []
    for val in value:
        if val.ndim == 0:
            value_str.append(f"{val:.2f}")
        else:
            value_str.append([f"{v:.2f}" for v in val])
    return cast("list[str | list[str]]", value_str)


class GetAttr:
    def __init__(self, default, name) -> None:
        self._value = default
        self._name = name

    def __get__(self, instance, owner) -> Self | Any:
        if not instance:
            return self
        return self._value

    def __set__(self, instance, value) -> None:
        msg = (
            f"It is not possible to set the value of '{self._name}'. "
            "This parameter is readonly!"
        )
        logger.error(msg)
        raise AttributeError(msg)


class SetAttr(GetAttr):
    def __init__(
        self, default, name, limits, absolut=False, dtype=(int, float), validator=None
    ) -> None:
        super().__init__(default, name)
        self._limits = limits
        self._absolut = absolut
        self._dtype = dtype
        self._validator = validator

    def __set__(self, instance, value) -> None:
        if (
            type(self._validator) is FunctionType
            and self._validator.__name__ == "validate_number"
        ):
            if self._absolut:
                self._validator(self._name, abs(value), self._limits, self._dtype)
            else:
                self._validator(self._name, value, self._limits, self._dtype)
        elif issubclass(self._validator, enum.Enum | aenum.Enum):
            self._validator(value)
        else:
            msg = "Unknown validator, please implement this version"
            logger.error(msg)
            raise NotImplementedError(msg)
        self._value = value
