#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for the hvl_ccb.dev.heinzinger sub-package.
"""

import logging

import pytest

from hvl_ccb.comm.serial import SerialCommunicationIOError
from hvl_ccb.dev.heinzinger.base import HeinzingerSerialCommunicationConfig
from hvl_ccb.dev.heinzinger.constants import (
    HeinzingerDeviceNotRecognizedError,
    HeinzingerSetValueError,
    RecordingsEnum,
)
from hvl_ccb.dev.heinzinger.device import Heinzinger, HeinzingerConfig
from masked_comm.serial import HeinzingerLoopSerialCommunication

logging.basicConfig(level=logging.ERROR)


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 9600,
        "parity": HeinzingerSerialCommunicationConfig.Parity.NONE,
        "stopbits": HeinzingerSerialCommunicationConfig.Stopbits.ONE,
        "bytesize": HeinzingerSerialCommunicationConfig.Bytesize.EIGHTBITS,
        "terminator": b"\r\n",
        "timeout": 3,
        "wait_sec_read_text_nonempty": 0.01,
        "default_n_attempts_read_text_nonempty": 5,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {
        "default_number_of_recordings": 16,
        "number_of_decimals": 6,
        "wait_sec_stop_commands": 0.01,
    }


class ConcreteHeinzinger(Heinzinger):
    def start(self) -> None:
        super().start()


@pytest.fixture
def started_heinzinger_device(com_config, dev_config):
    serial_port = HeinzingerLoopSerialCommunication(com_config)
    serial_port.open()
    serial_port.put_text("my_interface_version")
    serial_port.put_text("PNChp 60000-1neg 354211082")
    with Heinzinger(serial_port, dev_config) as heinzinger:
        while serial_port.get_written() is not None:
            pass
        yield serial_port, heinzinger


@pytest.fixture
def start_heinzinger_device(com_config, dev_config):
    def _start_heinzinger_device(serial_number):
        serial_port = HeinzingerLoopSerialCommunication(com_config)
        serial_port.open()
        serial_port.put_text("my_interface_version")
        serial_port.put_text(serial_number)

        def started_heinzinger():
            with Heinzinger(serial_port, dev_config) as heinzinger:
                while serial_port.get_written() is not None:
                    pass
                yield serial_port, heinzinger

        return started_heinzinger()

    return _start_heinzinger_device


def test_heinzinger_number_of_recordings(started_heinzinger_device) -> None:
    com, heinzinger = started_heinzinger_device
    # set a new value
    heinzinger.number_of_recordings = 4
    assert com.get_written() == "AVER 4"

    com.put_text("4")
    assert heinzinger.number_of_recordings == 4
    assert com.get_written() == "AVER?"

    # assigning integer not amongst accepted values
    # RangeEnum will pick a suitable value automatically, set 6 will get 8
    heinzinger.number_of_recordings = 6
    assert com.get_written() == "AVER 8"
    com.put_text("0.0")  # when device stop, voltage is set to 0


def test_com_config(com_config) -> None:
    config = HeinzingerSerialCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


def test_dev_config(dev_config) -> None:
    # currently there are no non-default config values
    HeinzingerConfig()

    config = HeinzingerConfig(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"number_of_decimals": 0},
        {"number_of_decimals": 11},
        {"wait_sec_stop_commands": 0},
        {"number_of_decimals": 6, "wait_sec_stop_commands": -1},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict) -> None:
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)
    with pytest.raises(ValueError):
        HeinzingerConfig(**invalid_config)


def test_heinzinger_instantiation(com_config, dev_config) -> None:
    heinzinger = ConcreteHeinzinger(com_config)
    assert heinzinger is not None

    heinzinger = ConcreteHeinzinger(com_config, dev_config)
    assert heinzinger is not None


def test_heinzinger_stop(started_heinzinger_device) -> None:
    com, heinzinger = started_heinzinger_device
    com.put_text("0.0")
    heinzinger.stop()
    assert com.get_written() == "VOLT 0.000000"
    assert com.get_written() == "VOLT?"
    assert com.get_written() == "OUTP OFF"

    # check that a second stop() works
    heinzinger.stop()
    assert not com.get_written()


def test_heinzinger_reset_interface(started_heinzinger_device) -> None:
    com, heinzinger = started_heinzinger_device
    heinzinger.reset_interface()
    assert com.get_written() == "*RST"
    com.put_text("0.0")  # when device stop, voltage is set to 0


def test_heinzinger_output_status_property(started_heinzinger_device) -> None:
    com, heinzinger = started_heinzinger_device
    assert heinzinger.output is None
    heinzinger.output = True
    assert heinzinger.output is True
    heinzinger.output = False
    assert heinzinger.output is False
    com.put_text("0.0")  # when device stop, voltage is set to 0


def test_heinzinger_com_error(com_config, dev_config) -> None:
    wrong_config = dict(com_config)
    wrong_config["port"] = "NOT A PORT"
    heinzinger = ConcreteHeinzinger(wrong_config, dev_config)
    assert not heinzinger.com.is_open

    with pytest.raises(SerialCommunicationIOError):
        heinzinger.start()

    heinzinger = ConcreteHeinzinger(com_config, dev_config)
    assert not heinzinger.com.is_open
    heinzinger._max_current_hardware = 1.5
    heinzinger._max_voltage_hardware = 1.5
    heinzinger._max_current = 1.5
    heinzinger._max_voltage = 1.5
    heinzinger._voltage_multiplier = 1.0
    heinzinger._current_multiplier = 1.0
    with pytest.raises(SerialCommunicationIOError):
        heinzinger.reset_interface()
    with pytest.raises(SerialCommunicationIOError):
        heinzinger.get_interface_version()
    with pytest.raises(SerialCommunicationIOError):
        heinzinger.get_serial_number()
    with pytest.raises(SerialCommunicationIOError):
        assert heinzinger.number_of_recordings
    with pytest.raises(SerialCommunicationIOError):
        heinzinger.number_of_recordings = RecordingsEnum.EIGHT
    with pytest.raises(SerialCommunicationIOError):
        heinzinger.voltage = 1
    with pytest.raises(SerialCommunicationIOError):
        assert heinzinger.voltage
    with pytest.raises(SerialCommunicationIOError):
        heinzinger.current = 1
    with pytest.raises(SerialCommunicationIOError):
        assert heinzinger.current


def test_heinzinger_deprecation_warning(started_heinzinger_device) -> None:
    com, heinzinger = started_heinzinger_device
    with pytest.raises(DeprecationWarning):
        heinzinger.output_on()
    with pytest.raises(DeprecationWarning):
        heinzinger.output_off()
    with pytest.raises(DeprecationWarning):
        heinzinger.get_number_of_recordings()
    with pytest.raises(DeprecationWarning):
        heinzinger.set_number_of_recordings()
    with pytest.raises(DeprecationWarning):
        heinzinger.measure_voltage()
    with pytest.raises(DeprecationWarning):
        heinzinger.measure_current()
    com.put_text("0.0")  # when device stop, voltage is set to 0


# test different possible serial numbers to check if the info is read correctly
devices_data = [
    ("PNChp 60000-1neg 354211082", 60000, 0.001),
    ("314807440/PNChp 60000-1neg.", 60000, 0.001),
    ("PNChp 1500-40 ump. 375214277", 1500, 0.04),
    ("PNC 100000-6pos 375214277", 100000, 0.006),
    ("PNC 600-3000pos 375214277", 600, 3),
]


@pytest.mark.parametrize("device_data", devices_data)
def test_heinzinger_start(start_heinzinger_device, device_data) -> None:
    started_heinzinger = start_heinzinger_device(device_data[0])
    com, heinzinger = next(started_heinzinger)

    # starting the device again should work
    com.put_text("my_interface_version")
    com.put_text(device_data[0])
    heinzinger.start()
    assert com.get_written() == "VERS?"
    assert com.get_written() == "*IDN?"
    assert heinzinger.max_voltage_hardware == heinzinger.max_voltage == device_data[1]
    assert heinzinger.max_current_hardware == heinzinger.max_current == device_data[2]
    assert com.get_written() == "AVER " + str(
        int(heinzinger.config.default_number_of_recordings.value)
    )


def test_heinzinger_not_recognized(start_heinzinger_device) -> None:
    with pytest.raises(HeinzingerDeviceNotRecognizedError):
        next(start_heinzinger_device("ABC 600-3000pos 375214277"))


def test_heinzinger_set_max_voltage(start_heinzinger_device) -> None:
    started_heinzinger = start_heinzinger_device("PNC 600-3000pos 375214277")
    com, heinzinger = next(started_heinzinger)

    # set max_voltage to half the current value
    next_value = heinzinger.max_voltage / 2
    heinzinger.max_voltage = next_value
    assert heinzinger.max_voltage == next_value
    heinzinger.max_voltage = None

    # assigning value higher than hardware maximum
    with pytest.raises(ValueError):
        heinzinger.max_voltage = heinzinger.max_voltage_hardware * 2

    # assigning negative value
    with pytest.raises(ValueError):
        heinzinger.max_voltage = -1


def test_pnc_set_max_current(start_heinzinger_device) -> None:
    started_heinzinger = start_heinzinger_device("PNC 600-3000pos 375214277")
    com, heinzinger = next(started_heinzinger)

    # set max_voltage to half the current value
    next_value = heinzinger.max_current / 2
    heinzinger.max_current = next_value
    assert heinzinger.max_current == next_value
    heinzinger.max_current = None

    # assigning value higher than hardware maximum
    with pytest.raises(ValueError):
        heinzinger.max_current = heinzinger.max_current_hardware * 2

    # assigning negative value
    with pytest.raises(ValueError):
        heinzinger.max_current = -1


def test_pnc_set_negative(start_heinzinger_device) -> None:
    started_heinzinger = start_heinzinger_device("PNC 600-3000pos 375214277")
    com, heinzinger = next(started_heinzinger)

    # assigning negative value
    with pytest.raises(ValueError):
        heinzinger.current = -1
    with pytest.raises(ValueError):
        heinzinger.voltage = -1


# test different values for voltage and current
# (device_name, user input value, should results command, internal value, out-of-range
# value)
devices_u = [
    ("PNC 600-3000pos 375214277", 600, "VOLT 600.000000", 600, 700),
    ("PNChp 1500-40 ump. 375214277", 1, "VOLT 1.000000", 1, 1600),
    ("PNChp 60000-1neg 354211082", 50000, "VOLT 50000.000000", 50000, 60000.1),
    ("PNC 100000-6pos 375214277", 100000, "VOLT 100.000000", 100, 101000),
]


@pytest.mark.parametrize("device_data", devices_u)
def test_heinzinger_set_voltage(start_heinzinger_device, device_data) -> None:
    started_heinzinger = start_heinzinger_device(device_data[0])
    com, heinzinger = next(started_heinzinger)

    # test if the correct text is sent to the com
    com.put_text(str(device_data[3]))
    heinzinger.voltage = device_data[1]
    assert com.get_written().strip() == device_data[2]
    com.put_text(str(device_data[3]))
    assert heinzinger.voltage == device_data[1]
    com.put_text(str(device_data[3]))
    heinzinger.set_voltage = device_data[1]
    com.put_text(str(device_data[3]))
    assert heinzinger.set_voltage == device_data[1]

    # test if an error is raised when trying to set a too high voltage
    com.put_text(str(device_data[4]))
    with pytest.raises(ValueError):
        heinzinger.voltage = device_data[4]
    com.put_text("2.0")
    with pytest.raises(HeinzingerSetValueError):
        heinzinger.voltage = device_data[1]


# test different values for voltage and current
# (device_name, user input value, should results command, internal value, out-of-range
# value)
devices_i = [
    ("PNC 600-3000pos 375214277", 3, "CURR 3.000000", 3, 10),
    ("PNChp 1500-40 ump. 375214277", 0.039, "CURR 39.000000", 39, 0.041),
    ("PNChp 60000-1neg 354211082", 0.001, "CURR 1.000000", 1, 0.002),
    ("PNC 100000-6pos 375214277", 0, "CURR 0.000000", 0, 6.1),
]


@pytest.mark.parametrize("device_data", devices_i)
def test_heinzinger_set_current(start_heinzinger_device, device_data) -> None:
    started_heinzinger = start_heinzinger_device(device_data[0])
    com, heinzinger = next(started_heinzinger)

    # test if the correct text is sent to the com
    com.put_text(str(device_data[3]))
    heinzinger.current = device_data[1]
    assert com.get_written().strip() == device_data[2]
    com.put_text(str(device_data[3]))
    assert heinzinger.current == device_data[1]
    com.put_text(str(device_data[3]))
    heinzinger.set_current = device_data[1]
    com.put_text(str(device_data[3]))
    assert heinzinger.set_current == device_data[1]

    # test if an error is raised when trying to set a too high current
    com.put_text(str(device_data[4]))
    with pytest.raises(ValueError):
        heinzinger.current = device_data[4]
    com.put_text("2.0")
    with pytest.raises(HeinzingerSetValueError):
        heinzinger.current = device_data[1]
