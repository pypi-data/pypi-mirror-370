#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for Enum utils.
"""

from typing import Literal

import pytest

from hvl_ccb.utils.enum import (
    AutoNumberNameEnum,
    BoolEnum,
    NameEnum,
    RangeEnum,
    StrEnumBase,
    ValueEnum,
    unique,
)


def test_strenumbase() -> None:
    @unique
    class E(StrEnumBase):
        A = "a"


def test_valueenum() -> None:
    with pytest.raises(ValueError):

        @unique
        class F(ValueEnum):
            ONE = 1
            TWO = 1

    @unique
    class E(ValueEnum):
        ONE = 1
        TWO = 2

    a = E(1)
    assert E(1) == E("1")
    assert hash(a) == hash(str(a.value))
    assert str(a.value) == a
    assert a.value == 1
    assert str(a) == "1"
    assert a == E.ONE

    assert E["ONE"] is a
    with pytest.raises(KeyError):
        E["one"]
    with pytest.raises(KeyError):
        E[a]

    assert a != 0
    assert a != 1

    b = E(2)
    assert E(2) == E("2")
    assert hash(b) == hash(str(b.value))
    assert a != b
    assert a != "b"
    assert a != E.TWO


def test_nameenum() -> None:
    class E(NameEnum, init="custom_name"):
        a = 2
        b = 4

    a = E("a")
    assert hash(a) == hash(a.name)
    assert a.name == a
    assert a == "a"
    assert str(a) == "a"
    assert a == E.a

    assert a != 2
    assert a.custom_name == 2

    assert E["a"] is a
    assert E[a] is a

    b = E("b")
    assert hash(b) == hash(b.name)
    assert a != b
    assert a != "b"
    assert a != E.b


def test_autonumbernameenum() -> None:
    class E(AutoNumberNameEnum):
        a = ()
        b = ()

    a = E("a")
    assert hash(a) == hash(a.name)
    assert a.name == a
    assert a == "a"
    assert str(a) == "a"
    assert a == E.a

    assert a != 0
    assert a != 1

    assert E["a"] is a
    assert E[a] is a

    b = E("b")
    assert hash(b) == hash(b.name)
    assert a != b
    assert a != "b"
    assert a != E.b


def test_rangeenum() -> None:
    class E(RangeEnum):
        TWO = 2
        ONE = 1

        @classmethod
        def unit(cls) -> Literal["V"]:
            return "V"

    assert E(1) == 1
    assert E(1.5) == 2
    assert E(0.1) == 1

    assert E.TWO == 2
    assert E(1.5) == E.TWO
    assert str(E.ONE) == "1.0"

    assert E.unit() == "V"

    with pytest.raises(TypeError):
        E("a")
    with pytest.raises(ValueError):
        E(5)

    assert hash(E(1)) == hash(E.ONE)
    assert E.ONE != E.TWO
    assert E.ONE != "1"
    assert E.ONE != 2

    class ER(RangeEnum):
        ONE = 1
        TWO = 2

        @classmethod
        def unit(cls) -> Literal["V"]:
            return "V"

        @classmethod
        def is_reversed(cls) -> bool:
            return True

    assert ER(1.5) == 1
    assert ER(2.5) == 2

    assert ER(2.5) == ER.TWO

    with pytest.raises(TypeError):
        ER("a")
    with pytest.raises(ValueError):
        ER(0.1)


def test_boolenum() -> None:
    class SingleTruth(BoolEnum):
        TRUE = True
        FALSE = False

    assert SingleTruth.TRUE
    assert not SingleTruth.FALSE
    assert bool(SingleTruth.TRUE)
    assert not bool(SingleTruth.FALSE)

    assert SingleTruth.TRUE.name == "TRUE"
    assert SingleTruth.TRUE.value
    assert not SingleTruth.FALSE.value

    class InvertedTruth(BoolEnum, init="truth inverted"):
        TRUE = True, "False"
        FALSE = False, "True"

    assert InvertedTruth.TRUE
    assert not InvertedTruth.FALSE
    assert InvertedTruth.TRUE.inverted == "False"
    assert InvertedTruth.FALSE.inverted == "True"

    assert InvertedTruth.TRUE.value == (True, "False")

    with pytest.raises(TypeError):

        class WrongClass(BoolEnum):
            MEMBER = "str"

    with pytest.raises(ValueError):

        class WrongInitNameClass(BoolEnum, init="value invert"):
            MEMBER = True, "str"
