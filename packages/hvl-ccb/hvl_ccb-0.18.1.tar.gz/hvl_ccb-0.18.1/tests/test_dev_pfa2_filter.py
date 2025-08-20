#  Copyright (c) ETH Zurich, SIS ID and HVL D-ITET
#
"""
Testing PFA-2 Filter.
"""

import logging

import pytest

from hvl_ccb.dev.pfa2_filter.base import (
    N_CHANNELS,
    Pfa2FilterChannelCoupling,
    Pfa2FilterChannelMode,
    Pfa2FilterCommunicationError,
    Pfa2FilterError,
    Pfa2FilterLPFMode,
    Pfa2FilterOverloadMode,
    Pfa2FilterPostGain,
    Pfa2FilterPreGain,
    Pfa2FilterSerialCommunicationConfig,
)
from hvl_ccb.dev.pfa2_filter.device import (
    Pfa2Filter,
    Pfa2FilterConfig,
)
from masked_comm.serial import Pfa2FilterLoopSerialCommunication

logging.basicConfig(level=logging.ERROR)


@pytest.fixture(scope="module")
def com_config():
    return {
        "port": "loop://?logging=debug",
        "baudrate": 57600,
        "timeout": 0.2,
        "default_n_attempts_read_text_nonempty": 2,
        "wait_sec_read_text_nonempty": 0.1,
    }


@pytest.fixture(scope="module")
def dev_config():
    return {
        "device_option_hpf": True,
        "coupling_init": Pfa2FilterChannelCoupling.DC,
        "mode_init": Pfa2FilterChannelMode.OPERATE,
        "pregain_init": 1,
        "postgain_init": 1,
        "lpf_freq_init": 127750,
        "lpf_mode_init": Pfa2FilterLPFMode.FLAT,
        "hpf_state_init": True,
        "hpf_freq_init": 1,
        "overload_limit_init": 10,
        "overload_mode_init": Pfa2FilterOverloadMode.CONTINUOUS,
    }


class ConcretePfa2Filter(Pfa2Filter):
    def start(self) -> None:
        super().start()


@pytest.fixture
def started_pfa2filter_device(com_config, dev_config):
    serial_port = Pfa2FilterLoopSerialCommunication(com_config)
    serial_port.open()
    for _ in range(N_CHANNELS):
        serial_port.put_text("DC")
        serial_port.put_text("OPERATE")
        serial_port.put_text("1")
        serial_port.put_text("1")
        serial_port.put_text("127750")
        serial_port.put_text("FLAT")
        serial_port.put_text("10")
        serial_port.put_text("CONTINUOUS")
        serial_port.put_text("ON")
        serial_port.put_text("1")

    with Pfa2Filter(serial_port, dev_config) as pfa2filter:
        while serial_port.get_written() is not None:
            pass
        yield serial_port, pfa2filter


@pytest.fixture
def start_pfa2filter_device(com_config, dev_config):
    def _start_pfa2filter_device():
        serial_port = Pfa2FilterLoopSerialCommunication(com_config)
        serial_port.open()

        def started_pfa2filter():
            with Pfa2Filter(serial_port, dev_config) as pfa2filter:
                while serial_port.get_written() is not None:
                    pass
                yield serial_port, pfa2filter

        return started_pfa2filter()

    return _start_pfa2filter_device


def test_com_config(com_config) -> None:
    config = Pfa2FilterSerialCommunicationConfig(**com_config)
    for key, value in com_config.items():
        assert getattr(config, key) == value


def test_dev_config(dev_config) -> None:
    # currently there are no non-default config values
    Pfa2FilterConfig()

    config = Pfa2FilterConfig(**dev_config)
    for key, value in dev_config.items():
        assert getattr(config, key) == value


@pytest.mark.parametrize(
    "wrong_config_dict",
    [
        {"coupling_init": True},
        {"mode_init": 2},
        {"pregain_init": "test"},
        {"postgain_init": "test"},
        {"lpf_freq_init": "test"},
        {"hpf_state_init": "test"},
        {"hpf_freq_init": "test"},
        {"overload_limit_init": "test"},
        {"overload_mode_init": 2},
    ],
)
def test_invalid_config_dict(dev_config, wrong_config_dict) -> None:
    invalid_config = dict(dev_config)
    invalid_config.update(wrong_config_dict)

    with pytest.raises(TypeError):
        Pfa2FilterConfig(**invalid_config)


def test_pfa2filter_instantiation(com_config, dev_config) -> None:
    pfa2filter_1 = ConcretePfa2Filter(com_config)
    assert pfa2filter_1 is not None

    pfa2filter_2 = ConcretePfa2Filter(com_config, dev_config)
    assert pfa2filter_2 is not None

    assert pfa2filter_2.__str__() == "PFA-2 Filter"


def test_pfa2filter_stop(started_pfa2filter_device) -> None:
    com, pfa2filter = started_pfa2filter_device
    pfa2filter.stop()

    assert not com.get_written()

    # check that a second stop() works
    pfa2filter.stop()
    assert not com.get_written()


def test_pfa2filter_channel_coupling(started_pfa2filter_device) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("DC")
    assert pfa2filter.channel_dict[0].coupling == Pfa2FilterChannelCoupling.DC
    assert com.get_written() == "0:COUPLING?"

    com.put_text("AC")
    pfa2filter.channel_dict[1].coupling = Pfa2FilterChannelCoupling.AC
    assert com.get_written() == "1:COUPLING=AC"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].coupling == Pfa2FilterChannelCoupling.DC

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].coupling = 1

    with pytest.raises(ValueError):
        pfa2filter.channel_dict[0].coupling = "tea with milk"

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[1].coupling = Pfa2FilterChannelCoupling.AC


def test_pfa2filter_channel_input_mode(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("OPERATE")
    assert pfa2filter.channel_dict[0].input_mode == Pfa2FilterChannelMode.OPERATE
    assert com.get_written() == "0:MODE?"

    com.put_text("SHORT")
    pfa2filter.channel_dict[1].input_mode = Pfa2FilterChannelMode.SHORTED
    assert com.get_written() == "1:MODE=SHORT"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].input_mode == Pfa2FilterChannelMode.OPERATE

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].input_mode = 1

    with pytest.raises(ValueError):
        pfa2filter.channel_dict[0].input_mode = "tea with milk"

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[0].input_mode = Pfa2FilterChannelMode.OPERATE


def test_pfa2filter_channel_lpf_mode(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("FLAT")
    assert pfa2filter.channel_dict[0].lpf_mode == Pfa2FilterLPFMode.FLAT
    assert com.get_written() == "0:LPFILTTYPE?"

    com.put_text("PULSE")
    assert pfa2filter.channel_dict[1].lpf_mode == Pfa2FilterLPFMode.PULSE

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].lpf_mode == Pfa2FilterLPFMode.FLAT

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].lpf_mode = True

    with pytest.raises(ValueError):
        pfa2filter.channel_dict[0].lpf_mode = "this is a test to fail"

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[0].lpf_mode = Pfa2FilterLPFMode.FLAT


def test_pfa2filter_channel_lpf_freq(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("127750")
    assert pfa2filter.channel_dict[0].lpf_freq == 127750
    assert com.get_written() == "0:LPFC?"

    com.put_text("10")
    pfa2filter.channel_dict[1].lpf_freq = 6
    assert com.get_written() == "1:LPFC=10"

    com.put_text("2750")
    pfa2filter.channel_dict[1].lpf_freq = 2700
    assert com.get_written() == "1:LPFC=2750"

    com.put_text("127500")
    pfa2filter.channel_dict[1].lpf_freq = 127700
    assert com.get_written() == "1:LPFC=127750"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].lpf_freq == 127750

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].lpf_freq = "eggs and bacon"

    with pytest.raises(ValueError):
        pfa2filter.channel_dict[0].lpf_freq = 200000

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[1].lpf_freq = 127750


def test_pfa2filter_channel_hpf_freq(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("125000")
    assert pfa2filter.channel_dict[0].hpf_freq == 125000
    assert com.get_written() == "0:HPFC?"

    com.put_text("200")
    pfa2filter.channel_dict[1].hpf_freq = 200
    assert com.get_written() == "1:HPFC=200"

    com.put_text("255")
    pfa2filter.channel_dict[1].hpf_freq = 275
    assert com.get_written() == "1:HPFC=255"

    com.put_text("10000")
    pfa2filter.channel_dict[1].hpf_freq = 10001
    assert com.get_written() == "1:HPFC=10000"

    com.put_text("12750")
    pfa2filter.channel_dict[1].hpf_freq = 12755
    assert com.get_written() == "1:HPFC=12750"

    com.put_text("127000")
    pfa2filter.channel_dict[1].hpf_freq = 127200
    assert com.get_written() == "1:HPFC=127000"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].hpf_freq == 125000

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].hpf_freq = "gin and tonic"

    with pytest.raises(ValueError):
        pfa2filter.channel_dict[0].hpf_freq = 200000

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[0].hpf_freq = 12755

    pfa2filter.channel_dict[1]._option_hpf = False
    with pytest.raises(Pfa2FilterError):
        assert pfa2filter.channel_dict[1].hpf_freq == 12755

    with pytest.raises(Pfa2FilterError):
        pfa2filter.channel_dict[1].hpf_freq = 12755


def test_pfa2filter_channel_hpf_state(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("OFF")
    assert pfa2filter.channel_dict[1].hpf_state is False
    assert com.get_written() == "1:HPFILT?"

    com.put_text("ON")
    pfa2filter.channel_dict[0].hpf_state = True
    assert com.get_written() == "0:HPFILT=ON"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].hpf_state is False

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].hpf_state = "not a boolean"

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[0].hpf_state = True

    pfa2filter.channel_dict[1]._option_hpf = False
    with pytest.raises(Pfa2FilterError):
        assert pfa2filter.channel_dict[1].hpf_state is False

    with pytest.raises(Pfa2FilterError):
        pfa2filter.channel_dict[1].hpf_state = False


def test_pfa2filter_channel_pregain(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("1.0")
    assert pfa2filter.channel_dict[0].pregain == Pfa2FilterPreGain.ONE
    assert com.get_written() == "0:PREGAIN?"

    com.put_text("4")
    pfa2filter.channel_dict[1].pregain = Pfa2FilterPreGain.FOUR
    assert com.get_written() == "1:PREGAIN=4.0"

    com.put_text("4")
    pfa2filter.channel_dict[1].pregain = 5.5
    assert com.get_written() == "1:PREGAIN=4.0"

    com.put_text("128")
    pfa2filter.channel_dict[1].pregain = 256
    assert com.get_written() == "1:PREGAIN=128.0"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].pregain == Pfa2FilterPreGain.ONE

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].pregain = "tree fiddy"

    with pytest.raises(ValueError):
        pfa2filter.channel_dict[0].pregain = 3.50e-5

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[0].pregain = Pfa2FilterPreGain.ONE


def test_pfa2filter_channel_postgain(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("0.5")
    assert pfa2filter.channel_dict[0].postgain == Pfa2FilterPostGain.ONE_HALF
    assert com.get_written() == "0:POSTGAIN?"

    com.put_text("16")
    pfa2filter.channel_dict[1].postgain = Pfa2FilterPostGain.SIXTEEN
    assert com.get_written() == "1:POSTGAIN=16.0"

    com.put_text("16")
    pfa2filter.channel_dict[1].postgain = 100
    assert com.get_written() == "1:POSTGAIN=16.0"

    com.put_text("8")
    pfa2filter.channel_dict[1].postgain = 8.5
    assert com.get_written() == "1:POSTGAIN=8.0"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].postgain == Pfa2FilterPostGain.ONE_HALF

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].postgain = "nothing or something"

    with pytest.raises(ValueError):
        pfa2filter.channel_dict[0].postgain = 0.0001

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[0].postgain = Pfa2FilterPostGain.ONE_HALF


def test_pfa2filter_channel_overload_state(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("1")
    assert pfa2filter.channel_dict[0].output_overload is True
    assert com.get_written() == "0:OUTOVLD?"

    com.put_text("0")
    assert pfa2filter.channel_dict[1].input_overload is False
    assert com.get_written() == "1:INOVLD?"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].output_overload is False

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[1].input_overload is True


def test_pfa2filter_channel_overload_limit(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("1.0")
    assert pfa2filter.channel_dict[0].overload_limit == 1.0
    assert com.get_written() == "0:OUTOVLDLIM?"

    com.put_text("4")
    pfa2filter.channel_dict[1].overload_limit = 4.0
    assert com.get_written() == "1:OUTOVLDLIM=4.0"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert pfa2filter.channel_dict[0].overload_limit == 1.0

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].overload_limit = "hello there"

    with pytest.raises(ValueError):
        pfa2filter.channel_dict[0].overload_limit = 125

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[0].overload_limit = 5


def test_pfa2filter_channel_overload_mode(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("LATCHING")
    assert pfa2filter.channel_dict[0].overload_mode == Pfa2FilterOverloadMode.LATCHING
    assert com.get_written() == "0:OVLDMODE?"

    com.put_text("CONTINUOUS")
    pfa2filter.channel_dict[1].overload_mode = Pfa2FilterOverloadMode.CONTINUOUS
    assert com.get_written() == "1:OVLDMODE=CONTINUOUS"

    with pytest.raises(Pfa2FilterCommunicationError):
        assert (
            pfa2filter.channel_dict[0].overload_mode == Pfa2FilterOverloadMode.LATCHING
        )

    with pytest.raises(TypeError):
        pfa2filter.channel_dict[0].overload_mode = 1

    with pytest.raises(ValueError):
        pfa2filter.channel_dict[0].overload_mode = "you shall not pass"

    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[0].overload_mode = Pfa2FilterOverloadMode.LATCHING


def test_pfa2filter_channel_overload_clear(
    started_pfa2filter_device,
) -> None:
    com, pfa2filter = started_pfa2filter_device

    com.put_text("LATCHING")
    com.put_text("1")
    com.put_text("0")
    com.put_text("0")

    assert pfa2filter.channel_dict[0].overload_clear() is True
    assert com.get_written() == "0:OVLDMODE?"
    assert com.get_written() == "0:OVLDCLEAR?"
    assert com.get_written() == "0:INOVLD?"
    assert com.get_written() == "0:OUTOVLD?"

    com.put_text("CONTINUOUS")
    com.put_text("0")
    com.put_text("0")
    assert pfa2filter.channel_dict[1].overload_clear() is True
    assert com.get_written() == "1:OVLDMODE?"
    assert com.get_written() == "1:INOVLD?"
    assert com.get_written() == "1:OUTOVLD?"

    com.put_text("LATCHING")
    with pytest.raises(Pfa2FilterCommunicationError):
        pfa2filter.channel_dict[0].overload_clear()
