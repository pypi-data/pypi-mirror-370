#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#

from __future__ import annotations

import logging
from abc import abstractmethod

import aenum
from typing_extensions import Self

logger = logging.getLogger(__name__)


# Use abstract base class instead of Mixin to inherit from `aenum.Enum` to make Sphinx
# detect inheritance correctly and create docs for derived enums, including such as
# these in `dev.supercube.constants`. With Mixin approach, module-level enum classes
# are not documented.
class StrEnumBase(aenum.Enum):
    """
    String representation-based equality and lookup.
    """

    def __eq__(self, other) -> bool:
        return (self is other) or (other.__eq__(str(self)))

    # use only with aenum enums
    @classmethod
    def _missing_value_(cls, value):  # noqa: ANN206
        for member in cls:
            if member == value:
                return member
        return None

    @abstractmethod
    def __str__(self) -> str:
        pass  # pragma: no cover

    def __hash__(self) -> int:
        return hash(str(self))


unique = aenum.unique


class ValueEnum(StrEnumBase):
    """
    Enum with string representation of values used as string representation, and with
    lookup and equality based on this representation.
    Values do not need to be of type 'str', but they need to have
    a str-representation to enable this feature.
    The lookup is implemented in StrEnumBase with the _missing_value_ method.
    The equality is also defined at this place (__eq__).

    Use-case:

    .. code-block:: python

        class E(ValueEnum):
            ONE = 1

        E.ONE == "1"
        E.ONE != 1
        E.ONE != "ONE"

    The access would be normally with E(1), but E("1") works also.
    Therefore, E(1) == E("1")

    Attention: to avoid errors, best use together with `unique` enum decorator.
    """

    def __str__(self) -> str:
        return str(self.value)


class NameEnum(StrEnumBase, settings=aenum.Unique):  # type: ignore[call-arg]
    """
    Enum with names used as string representation, and with lookup and equality based on
    this representation.
    The lookup is implemented in StrEnumBase with the _missing_value_ method.
    The equality is also defined at this place (__eq__).

    Use-case:

    .. code-block:: python

        class E(NameEnum):
            a = 2
            b = 4

        E.a == "a"
        E.a != 2
        E.a != "2"

    The access would be normally with E["a"], but E("a") works also.
    Therefore, E["a"] == E("a")

    Attention: to avoid errors, best use together with `unique` enum decorator.
    """

    def __str__(self) -> str:
        return self.name


class AutoNumberNameEnum(NameEnum, aenum.AutoNumberEnum):
    """
    Auto-numbered enum with names used as string representation, and with lookup and
    equality based on this representation.
    """


class RangeEnum(float, ValueEnum):
    """
    Range enumeration inherit from ValueEnum, find suitable voltage/current/resistance
    input range for devices such as multimeter and oscilloscope
    """

    @classmethod
    def is_reversed(cls) -> bool:
        """
        Returns if the desired range value is not available, the next suitable range
        which is larger (is_reversed = False) or smaller (is_reversed = True) than the
        desired range value should be selected
        Default: False
        :return: True if the next suitable range should be larger than the desired value
        False if the next suitable range should be smaller than the desired value
        """
        return False

    @classmethod
    @abstractmethod
    def unit(cls) -> str:
        """
        Returns the Unit of the values in the enumeration.
        :return: the unit of the values in the enumeration in string format
        """

    @classmethod
    def _missing_value_(cls, value) -> RangeEnum | None:
        """
        Find suitable desired range value
        If the desired range value is not available, the next suitable range which is
        larger (is_reversed = False) or smaller (is_reversed = True) than the desired
        range value is selected

        :param value: is the desired range value
        :raises ValueError: when desired range value is larger (is_reversed = False)
        than device maximum value or smaller (is_reversed = True) than device minimum
        value
        :return: the desired range value according to the device setting
        """
        range_unit = cls.unit()
        is_reversed = cls.is_reversed()
        attrs = sorted([member.value for member in cls], reverse=is_reversed)  # type: ignore[attr-defined]
        chosen_range: RangeEnum | None = None
        for attr in attrs:
            if (value < attr and not is_reversed) or (value > attr and is_reversed):
                chosen_range = cls(attr)
                logger.warning(
                    f"Desired value ({value} {range_unit}) not possible."
                    f"Next {'smaller' if is_reversed else 'larger'} range "
                    f"({chosen_range.value} {range_unit}) selected."
                )
                break
        if chosen_range is None:
            if is_reversed:
                msg = (
                    f"Desired value ({value} {range_unit}) is under the min value "
                    f"({min(cls).value} {range_unit})."
                )
            else:
                msg = (
                    f"Desired value ({value} {range_unit}) is over the max value "
                    f"({max(cls).value} {range_unit})."
                )
            logger.error(msg)
            raise ValueError(msg)
        return chosen_range


class BoolEnum(NameEnum):
    """
    BoolEnum inherits from NameEnum and the type of the first value is
        enforced to be 'boolean'. For bool()-operation the __bool__ is redefined here.
    """

    def __new__(cls, *values, **_kwargs) -> Self:
        if "value" in cls.__dict__["_creating_init_"]:
            msg = "Name 'value' is reserved by 'Enum' and cannot be used."
            raise ValueError(msg)
        if not isinstance(values[0], bool):
            msg = (
                f"{cls}: first value must be bool [{values[0]} is a {type(values[0])}]"
            )
            raise TypeError(msg)
        return object.__new__(cls)

    def __bool__(self) -> bool:
        """
        If member has multiple values only the first value is returned.

        :return: Only the first value is returned. The type of this value is
            enforced to be boolean
        """
        if isinstance(self.value, bool):
            return self.value

        return self.value[0]
