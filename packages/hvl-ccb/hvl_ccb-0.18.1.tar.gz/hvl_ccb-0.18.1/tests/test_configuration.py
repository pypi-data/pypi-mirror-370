#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for configuration.py: Mixin and class decorator configdataclass
"""

from dataclasses import field
from pathlib import Path

import pytest

from hvl_ccb.configuration import ConfigurationMixin, EmptyConfig, configdataclass


@configdataclass
class GenericTypeHintsConfiguration:
    field1: list
    field2: list[int]
    field3: list


@configdataclass
class MyConfiguration:
    field1: int
    field2: str = "hello"

    def clean_values(self) -> None:
        if self.field1 == 0:
            msg = "field1 is not allowed to be 0"
            raise ValueError(msg)

        if self.field2 == "":
            self.force_value("field2", "EMPTY")

    def post_force_value(self, fieldname, _value) -> None:
        self.post_force_value.applied_to.append(fieldname)

    post_force_value.applied_to = []  # noqa: RUF012


@configdataclass
class MyConfigurationDefaults:
    field1: int
    field2: list
    field3: int = 1
    field4: list = field(default_factory=list)


@configdataclass
class SimpleConfiguration:
    field1: str = "field1"


class MyClassHasConfiguration(ConfigurationMixin):
    @staticmethod
    def config_cls():
        return MyConfiguration


# TESTS
def test_generic_type_hints() -> None:
    GenericTypeHintsConfiguration(["a"], [1], ["a"])
    with pytest.raises(TypeError):
        GenericTypeHintsConfiguration(("a",), [1], ["a"])
    with pytest.raises(TypeError):
        GenericTypeHintsConfiguration(["a"], [1], ("a",))
    with pytest.raises(TypeError):
        GenericTypeHintsConfiguration(["a"], ["a"], ["a"])


def test_inheritance() -> None:
    @configdataclass
    class SubMyConfiguration(MyConfiguration):
        field1: int = 3
        field3: int = 5

    assert SubMyConfiguration.optional_defaults() == {
        "field1": 3,
        "field2": "hello",
        "field3": 5,
    }

    SubMyConfiguration()

    with pytest.raises(AttributeError):

        @configdataclass
        class SubFailingConfiguration(MyConfiguration):
            def keys(self):
                pass


def test_configdataclass() -> None:
    SimpleConfiguration()

    # test own clean_values implementation
    with pytest.raises(ValueError):
        MyConfiguration(0)

    # test force_value
    config = MyConfiguration(1, field2="")
    assert config.field2 == "EMPTY"
    assert config.post_force_value.applied_to == ["field2"]

    # test convenience functions
    assert MyConfiguration.optional_defaults() == {"field2": "hello"}
    assert MyConfiguration.required_keys() == ["field1"]
    assert MyConfiguration.keys() == ["field1", "field2"]

    # typing is enforced
    with pytest.raises(TypeError):
        MyConfiguration("test")


def test_default_fields() -> None:
    assert MyConfigurationDefaults.required_keys() == ["field1", "field2"]
    assert MyConfigurationDefaults.optional_defaults() == {"field3": 1, "field4": []}


def test_configdataclass_with_generic() -> None:
    @configdataclass
    class ConfigurationWithGeneric:
        number: int | float

    with pytest.raises(TypeError):
        ConfigurationWithGeneric("1")
    assert ConfigurationWithGeneric(1).number == 1
    assert ConfigurationWithGeneric(1.0).number == 1.0


def test_configdataclass_fromdict() -> None:
    test_config = {"field1": 1, "field2": "otherstring"}

    my_class = MyClassHasConfiguration(test_config)
    assert my_class.config.field1 == 1
    assert my_class.config.field2 == "otherstring"

    test_config_2 = {"field3": 3, "field4": 4}

    # superfluous fields are not allowed
    with pytest.raises(TypeError):
        MyClassHasConfiguration(test_config_2)

    # non-configdataclasses are not allowed
    class WrongDefaultConfigDataclass(ConfigurationMixin):
        @staticmethod
        def config_cls():
            class NotAConfigDataclass:
                field1: int = 0

            return NotAConfigDataclass

    with pytest.raises(TypeError):
        WrongDefaultConfigDataclass({"field1": 1})


def test_empty_config() -> None:
    config = EmptyConfig()
    assert not config.required_keys()
    assert not config.keys()


def test_configuration_mixin() -> None:
    test_config = MyConfiguration(1)
    my_class = MyClassHasConfiguration(test_config)
    assert my_class.config == test_config

    with pytest.raises(TypeError):
        MyClassHasConfiguration(object)


def test_json_save_load() -> None:
    """
    Test the JSON configuration save and load feature.
    """

    c = MyClassHasConfiguration({"field1": 1})
    c.configuration_save_json("test.json")

    # create new protocol from that JSON configuration
    d = MyClassHasConfiguration.from_json("test.json")

    # clean up, delete file
    Path("test.json").unlink()

    assert c.config == d.config


def test_unfrozen() -> None:
    @configdataclass(frozen=False)
    class Test:
        field1: int = 3

    test = Test()
    assert test.field1 == 3
    test.field1 = 5
    assert test.field1 == 5

    # attention: typing is not enforced!
    test.field1 = "bla"
    assert test.field1 == "bla"
