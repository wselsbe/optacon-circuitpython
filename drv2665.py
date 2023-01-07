
from adafruit_bus_device import i2c_device
from busio import I2C


DRV2665_ADDR = 0x59

#register 0
_REGISTER_0 = 0x00
_FIFO_EMPTY_MASK = 0b00000010
_FIFO_FULL_MASK = 0b00000001

#register 1
_REGISTER_1 = 0x01
_CHIPID_MASK = 0b01111000

_INPUT_MASK = 0b00000100
INPUT_DIGITAL = 0 << 2
INPUT_ANALOG = 1 << 2

_GAIN_MASK = 0b00000011
GAIN_25V = 0
GAIN_50V = 1
GAIN_75V = 2
GAIN_100V = 3

#register 2
_REGISTER_2 = 0x02
_RESET = 1 << 7

_STANDBY_MASK = 0b01000000
_STANDBY_FALSE = 0 << 6
_STANDBY_TRUE = 1 << 6

_TIMEOUT_MASK = 0b00001100
TIMEOUT_5MS = 0 << 2
TIMEOUT_10MS = 1 << 2
TIMEOUT_15MS = 2 << 2
TIMEOUT_20MS = 3 << 2

_ENABLE_MASK = 0b00000010
ENABLE_AUTO = 0 << 1
ENABLE_OVERRIDE = 1 << 1

#register fifo queue for data
_REGISTER_DATA = 0x0B


class DRV2665:
    # Class-level buffer for reading and writing data.
    # This reduces memory allocations but means the code is not re-entrant or thread safe!
    _BUFFER = bytearray(2)

    def __init__(self, i2c: I2C, address: int = DRV2665_ADDR) -> None:
        self._device = i2c_device.I2CDevice(i2c, address)
        self._validate_chipid()

        self.reset()

    def _validate_chipid(self):
        self._read_register1()
        chipid = (self._register1_value & _CHIPID_MASK) >> 3
        if chipid not in (5,7):
            raise RuntimeError("Failed to find DRV2665 or DRV2667, check wiring!")

    def reset(self):
        self._write_u8(_REGISTER_2, _RESET)
        self._read_register1()
        self._read_register2()    

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
        return register0_value & _FIFO_EMPTY_MASK == _FIFO_EMPTY_MASK, register0_value & _FIFO_FULL_MASK == _FIFO_FULL_MASK

    def write_digital(self, value: int):
        self._write_s8(_REGISTER_DATA, value)

    def _read_register1(self):
        self._register1_value = self._read_u8(_REGISTER_1)
        
    def _write_register1(self):
        self._write_u8(_REGISTER_1, self._register1_value)    
    
    def _read_register2(self):
        self._register2_value = self._read_u8(_REGISTER_2)

    def _write_register2(self):
        self._write_u8(_REGISTER_2, self._register2_value)        

    def _read_u8(self, address: int) -> int:
        with self._device as i2c:
            self._BUFFER[0] = address & 0xFF
            i2c.write_then_readinto(self._BUFFER, self._BUFFER, out_end=1, in_end=1)
        return self._BUFFER[0]

    def _write_u8(self, address: int, value: int) -> None:
        with self._device as i2c:
            self._BUFFER[0] = address & 0xFF
            self._BUFFER[1] = value & 0xFF
            i2c.write(self._BUFFER, end=2)

    def _write_s8(self, address: int, value: int) -> None:        
        assert -128 <= value <= 127
        if value < 0:
            value += 0xFF # two's complement
        self._write_u8(address, value)