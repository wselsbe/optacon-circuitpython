import time
from machine import I2C
from micropython import const

DRV2665_ADDR = const(0x59)

# register 0
_REGISTER_0 = const(0x00)
_FIFO_EMPTY_MASK = const(0b00000010)
_FIFO_FULL_MASK = const(0b00000001)

# register 1
_REGISTER_1 = const(0x01)
_CHIP_ID_MASK = const(0b01111000)

_INPUT_MASK = const(0b00000100)
INPUT_DIGITAL = const(0 << 2)
INPUT_ANALOG = const(1 << 2)

_GAIN_MASK = const(0b00000011)
GAIN_25V = const(0)
GAIN_50V = const(1)
GAIN_75V = const(2)
GAIN_100V = const(3)

# register 2
_REGISTER_2 = const(0x02)
_RESET = const(1 << 7)

_STANDBY_MASK = const(0b01000000)
_STANDBY_FALSE = const(0 << 6)
_STANDBY_TRUE = const(1 << 6)

_TIMEOUT_MASK = const(0b00001100)
TIMEOUT_5MS = const(0 << 2)
TIMEOUT_10MS = const(1 << 2)
TIMEOUT_15MS = const(2 << 2)
TIMEOUT_20MS = const(3 << 2)

_ENABLE_MASK = const(0b00000010)
ENABLE_AUTO = const(0 << 1)
ENABLE_OVERRIDE = const(1 << 1)

# register fifo queue for data
_REGISTER_DATA = const(0x0B)


class DRV2665:

    def __init__(self, i2c: I2C, address: int = DRV2665_ADDR) -> None:
        self._i2c = i2c
        self._address = address
        self._validate_chip_id()

        self._read_register1()
        self._read_register2()

    def _validate_chip_id(self):
        self._read_register1()
        chip_id = (self._register1_value & _CHIP_ID_MASK) >> 3
        if chip_id not in (5, 7):
            raise RuntimeError("Failed to find DRV2665 or DRV2667, check wiring!")

    def reset(self):
        self._write_u8(_REGISTER_2, _RESET)
        time.sleep_ms(500)

    @property
    def gain(self) -> int:
        self._read_register1()
        return self._register1_value & _GAIN_MASK

    @gain.setter
    def gain(self, value: int) -> None:
        assert value in (GAIN_25V, GAIN_50V, GAIN_75V, GAIN_100V)
        self._register1_value &= ~_GAIN_MASK
        self._register1_value |= value
        self._write_register1()

    @property
    def input(self) -> int:
        self._read_register1()
        return self._register1_value & _INPUT_MASK

    @input.setter
    def input(self, value: int) -> None:
        assert value in (INPUT_ANALOG, INPUT_DIGITAL)
        self._register1_value &= ~_INPUT_MASK
        self._register1_value |= value
        self._write_register1()

    @property
    def standby(self) -> bool:
        self._read_register2()
        standby_value = self._register2_value & _STANDBY_MASK
        return standby_value == _STANDBY_TRUE

    @standby.setter
    def standby(self, value: bool) -> None:
        self._register2_value &= ~_STANDBY_MASK
        self._register2_value |= _STANDBY_TRUE if value else _STANDBY_FALSE
        self._write_register2()

    @property
    def timeout(self) -> int:
        self._read_register2()
        return self._register2_value & _TIMEOUT_MASK

    @timeout.setter
    def timeout(self, value: int) -> None:
        assert value in (TIMEOUT_5MS, TIMEOUT_10MS, TIMEOUT_15MS, TIMEOUT_20MS)
        self._register2_value &= ~_TIMEOUT_MASK
        self._register2_value |= value
        self._write_register2()

    @property
    def enable(self) -> int:
        self._read_register2()
        return self._register2_value & _ENABLE_MASK

    @enable.setter
    def enable(self, value: int) -> None:
        assert value in (ENABLE_AUTO, ENABLE_OVERRIDE)
        self._register2_value &= ~_ENABLE_MASK
        self._register2_value |= value
        self._write_register2()

    @property
    def queue_empty_full(self) -> tuple[bool, bool]:
        register0_value = self._read_u8(_REGISTER_0)
        return \
            register0_value & _FIFO_EMPTY_MASK == _FIFO_EMPTY_MASK, \
            register0_value & _FIFO_FULL_MASK == _FIFO_FULL_MASK

    def write_digital(self, value: int):
        self._write_s8(_REGISTER_DATA, value)

    def _read_register1(self):
        self._register1_value = self._read_u8(_REGISTER_1)
        print(f"register1: {self._register1_value:#010b}")

    def _write_register1(self):
        self._write_u8(_REGISTER_1, self._register1_value)

    def _read_register2(self):
        self._register2_value = self._read_u8(_REGISTER_2)
        print(f"register2: {self._register2_value:#010b}")

    def _write_register2(self):
        self._write_u8(_REGISTER_2, self._register2_value)

    def _read_u8(self, register: int) -> int:
        response = self._i2c.readfrom_mem(self._address, register, 1)
        return response[0]

    def _write_u8(self, register: int, value: int) -> None:
        print(f"writing {hex(register)} {value:#010b}")
        self._i2c.writeto_mem(self._address, register, bytes(value))

    def _write_s8(self, address: int, value: int) -> None:
        assert -128 <= value <= 127
        if value < 0:
            value += 0xFF  # two's complement
        self._write_u8(address, value)
