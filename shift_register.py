from digitalio import DigitalInOut
from busio import SPI
from adafruit_bus_device.spi_device import SPIDevice

_MASK_COMMON_U1 = 0b00111111
_MASK_COMMON_U2 = 0b11111100

_PINS_ALL = bytes([0xFF & ~_MASK_COMMON_U1, 0xFF, 0xFF, 0xFF & ~_MASK_COMMON_U2])
_PINS_NONE = bytes([0,0,0,0])

class ShiftRegister:
    
    _device: SPIDevice
    _data: bytearray

    def __init__(self,
        spi: SPI,
        latch: DigitalInOut,
        polarity: DigitalInOut,        
        baudrate: int = 1000000
    ) -> None:
        self._device = SPIDevice(spi, latch, baudrate=baudrate)
        self._data = bytearray(4)

        self._polarity = polarity
        self._polarity.value = False

        self._validate()

    def _validate(self):
        with self._device as spi:
            spi.write(_PINS_NONE)
            spi.write_readinto(_PINS_ALL, self._data)
            assert self._data[0] == _PINS_NONE[0] and self._data[1] == _PINS_NONE[1] and self._data[2] == _PINS_NONE[2] and self._data[3] == _PINS_NONE[3]
            spi.write_readinto(_PINS_NONE, self._data)
            assert self._data[0] == _PINS_ALL[0] and self._data[1] == _PINS_ALL[1] and self._data[2] == _PINS_ALL[2] and self._data[3] == _PINS_ALL[3]
            spi.write_readinto(_PINS_NONE, self._data)
            assert self._data[0] == _PINS_NONE[0] and self._data[1] == _PINS_NONE[1] and self._data[2] == _PINS_NONE[2] and self._data[3] == _PINS_NONE[3]

    def toggle_polarity(self):
        self.polarity.value = not self.polarity.value

    def set_pin(self, pin: int, value: bool):
        assert 1 <= pin <= 20
        shift_pos = pin - 1 + 6  # from 1-based to 0-based, skip PZT_Common
        byte_index = shift_pos // 8
        byte_mask = 1 << (shift_pos % 8)
        if value:
            self._data[byte_index] |= byte_mask
        else:
            self._data[byte_index] &= ~byte_mask

    def write(self):
        self._data[0] &= ~_MASK_COMMON_U1  # PZT_Common always 0
        self._data[3] &= ~_MASK_COMMON_U2
        with self._device as spi:
            spi.write(self._data)