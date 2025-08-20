#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Facilities providing classes for handling configuration for communication protocols
and devices.
"""

import dataclasses
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from importlib import import_module
from pathlib import Path

from typeguard import TypeCheckError, check_type  # type: ignore[import-not-found]
from typing_extensions import Self

logger = logging.getLogger(__name__)


def _has_default_value(f: dataclasses.Field):
    return (
        f.default is not dataclasses.MISSING
        or f.default_factory is not dataclasses.MISSING
    )


# Hooks of configdataclass
def _clean_values(_self):
    """
    Cleans and enforces configuration values. Does nothing by default, but may be
    overridden to add custom configuration value checks.
    """


_configclass_hooks = {
    "clean_values": _clean_values,
}


# Methods of configdataclass
def ___post_init__(self):  # noqa: N807
    self._check_types()
    self.clean_values()


def _force_value(self, fieldname, value):
    """
    Forces a value to a dataclass field despite the class being frozen.

    NOTE: you can define `post_force_value` method with same signature as this method
    to do extra processing after `value` has been forced on `fieldname`.

    :param fieldname: name of the field
    :param value: value to assign
    """
    object.__setattr__(self, fieldname, value)
    if hasattr(self, "post_force_value"):
        self.post_force_value(fieldname, value)


@classmethod  # type: ignore[misc]
def _keys(cls) -> Sequence[str]:
    """
    Returns a list of all configdataclass fields key-names.

    :return: a list of strings containing all keys.
    """
    return [f.name for f in dataclasses.fields(cls)]


@classmethod  # type: ignore[misc]
def _required_keys(cls) -> Sequence[str]:
    """
    Returns a list of all configdataclass fields, that have no default value assigned
    and need to be specified on instantiation.

    :return: a list of strings containing all required keys.
    """
    return [f.name for f in dataclasses.fields(cls) if not _has_default_value(f)]


@classmethod  # type: ignore[misc]
def _optional_defaults(cls) -> dict[str, object]:
    """
    Returns a list of all configdataclass fields, that have a default value assigned
    and may be optionally specified on instantiation.

    :return: a list of strings containing all optional keys.
    """
    return {
        f.name: f.default
        if f.default_factory is dataclasses.MISSING
        else f.default_factory()
        for f in dataclasses.fields(cls)
        if _has_default_value(f)
    }


def __check_types(self):
    mod = import_module(self.__module__)
    for field in dataclasses.fields(self):
        name = field.name
        value = getattr(self, name)
        type_ = field.type
        if isinstance(type_, str):  # `from __future__ import annotations` in use
            try:
                # built-in types
                type_ = eval(type_)  # noqa: S307
            except NameError:
                # no logging at this point, try-except controls program behaviour
                # module-level defined type
                type_ = getattr(mod, type_)
        try:
            check_type(value, type_)
        except TypeCheckError as exc:
            msg = (
                f"Type of field '{name}' is '{type(value)}' "
                f"and does not match '{type_}.'"
            )
            raise TypeError(msg) from exc


_configclass_methods = {
    "__post_init__": ___post_init__,
    "force_value": _force_value,
    "keys": _keys,
    "required_keys": _required_keys,
    "optional_defaults": _optional_defaults,
    "_check_types": __check_types,
}


def configdataclass(direct_decoration=None, frozen=True) -> Callable:
    """
    Decorator to make a class a configdataclass. Types in these dataclasses are
    enforced. Implement a function clean_values(self) to do additional checking on
    value ranges etc.

    It is possible to inherit from a configdataclass and re-decorate it with
    @configdataclass. In a subclass, default values can be added to existing fields.
    Note: adding additional non-default fields is prone to errors, since the order
    has to be respected through the whole chain (first non-default fields, only then
    default-fields).

    :param frozen: defaults to True. False allows to later change configuration values.
        Attention: if configdataclass is not frozen and a value is changed, typing is
        not enforced anymore!
    """

    def decorator(cls):
        for name, method in _configclass_methods.items():
            if name in cls.__dict__:
                msg = f"configdataclass {cls.__name__} cannot define {name} method"
                raise AttributeError(msg)
            setattr(cls, name, method)
        for name, hook in _configclass_hooks.items():
            if not hasattr(cls, name):
                setattr(cls, name, hook)
        if not hasattr(cls, "is_configdataclass"):
            cls.is_configdataclass = True

        return dataclasses.dataclass(cls, frozen=frozen)

    if direct_decoration:
        return decorator(direct_decoration)

    return decorator


class ConfigurationMixin(ABC):
    """
    Mixin providing configuration to a class.
    """

    # omitting type hint of `configuration` on purpose, because type hinting
    # configdataclass is not possible. Union[dict[str, object], object] resolves to
    # object.
    def __init__(self, configuration) -> None:
        """
        Constructor for the configuration mixin.

        :param configuration: is the configuration provided either as:
        *   a dict with string keys and values, then the default config dataclass
            will be used
        *   a configdataclass object
        *   None, then the config_cls() with no parameters is instantiated
        """

        if not configuration:
            configuration = {}

        if hasattr(configuration, "is_configdataclass"):
            self._configuration = configuration
        elif isinstance(configuration, dict):
            default_configdataclass = self.config_cls()
            if not hasattr(default_configdataclass, "is_configdataclass"):
                msg = (
                    "Default configdataclass is not a configdataclass. Is"
                    "the decorator `@configdataclass` applied?"
                )
                raise TypeError(msg)
            self._configuration = default_configdataclass(**configuration)
        else:
            msg = "configuration is not a dictionary or configdataclass."
            raise TypeError(msg)

    @staticmethod
    @abstractmethod
    def config_cls():
        """
        Return the default configdataclass class.

        :return: a reference to the default configdataclass class
        """

    @property
    def config(self):  # noqa: ANN201
        """
        ConfigDataclass property.

        :return: the configuration
        """

        return self._configuration

    @classmethod
    def from_json(cls, filename: str) -> Self:
        """
        Instantiate communication protocol using configuration from a JSON file.

        :param filename: Path and filename to the JSON configuration
        """

        configuration = cls._configuration_load_json(filename)
        return cls(configuration)

    def configuration_save_json(self, path: str) -> None:
        """
        Save current configuration as JSON file.

        :param path: path to the JSON file.
        """

        self._configuration_save_json(dataclasses.asdict(self._configuration), path)

    @staticmethod
    def _configuration_load_json(path: str) -> dict[str, object]:
        """
        Load configuration from JSON file and return dict. This method is only used
        during construction, if not directly a configuration is given but rather a
        path to a JSON config file.

        :param path: Path to the JSON configuration file.
        :return: Dictionary containing the parameters read from the JSON file.
        """

        with Path(path).open() as fp:
            return json.load(fp)

    @staticmethod
    def _configuration_save_json(configuration: dict[str, object], path: str) -> None:
        """
        Store a configuration dict to a JSON file.

        :param configuration: configuration dictionary
        :param path: path to the JSON file.
        """

        with Path(path).open("w") as fp:
            json.dump(configuration, fp, indent=4)


@configdataclass
class EmptyConfig:
    """
    Empty configuration dataclass.
    """


class ConfigurationValueWarning(UserWarning):
    """
    User warnings category for values of `@configdataclass` fields.
    """
