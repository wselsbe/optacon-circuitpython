from machine import Pin, SPI
from micropython import const

_MASK_COMMON_U1 = const(0b00111111)
_MASK_COMMON_U2 = const(0b11111100)

_PINS_ALL = bytes([0xFF, 0xFF & ~_MASK_COMMON_U1, 0xFF & ~_MASK_COMMON_U2, 0xFF])
_PINS_NONE = bytes([0, 0, 0, 0])


class ShiftRegister:
    _data: bytearray
    _read_buffer: bytearray

    def __init__(
            self,
            spi: SPI,
            latch: Pin,
            polarity: Pin
    ) -> None:
        self._spi = spi

        self._latch = latch
        self._latch.value(0)

        self._polarity = polarity
        self._polarity.value(0)

        self._data = bytearray(4)
        self._read_buffer = bytearray(4)

        self.reset()

        self._validate()

    def reset(self):
        self._data[0] = _PINS_NONE[0]
        self._data[1] = _PINS_NONE[1]
        self._data[2] = _PINS_NONE[2]
        self._data[3] = _PINS_NONE[3]

    def _validate(self):
        failed_pins = []
        for pin in range(1, 20 + 1):
            self.reset()
            self.set_pin(pin, True)
            try:
                self._write_verify()
                print(f"pin {pin} PASS")
            except AssertionError:
                print(f"pin {pin} FAIL")
                failed_pins.append(pin)
        print(f"failed pins: {failed_pins}")

    def toggle_polarity(self):
        self._polarity.value = not self._polarity.value

    def set_pin(self, pin: int, value: bool):
        assert 1 <= pin <= 20
        if pin <= 2:
            byte_index = 1
            byte_mask = 1 << (pin + 5)
        elif pin <= 10:
            byte_index = 0
            byte_mask = 1 << (pin - 3)
        elif pin <= 18:
            byte_index = 3
            byte_mask = 1 << (pin - 11)
        else:
            byte_index = 2
            byte_mask = 1 << (pin - 19)

        if value:
            self._data[byte_index] |= byte_mask
        else:
            self._data[byte_index] &= ~byte_mask

    def write(self):
        self._data[1] &= ~_MASK_COMMON_U1  # PZT_Common always 0
        self._data[2] &= ~_MASK_COMMON_U2
        self._write_verify()

    def _write_verify(self):
        print(f"writing spi {self._data[0]:#010b} {self._data[1]:#010b} {self._data[2]:#010b} {self._data[3]:#010b}")
        try:
            self._latch(0)
            self._spi.write(self._data)
            self._spi.write_readinto(self._data, self._read_buffer)
            print(f"read spi {self._read_buffer[0]:#010b} {self._read_buffer[1]:#010b} {self._read_buffer[2]:#010b} {self._read_buffer[3]:#010b}")
            assert self._data[0] == self._read_buffer[0] and \
                   self._data[1] == self._read_buffer[1] and \
                   self._data[2] == self._read_buffer[2] and \
                   self._data[3] == self._read_buffer[3]
        finally:
            self._latch(1)
