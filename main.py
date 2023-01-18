from machine import Pin, SPI, I2C
from drv2665 import *
from shift_register import ShiftRegister

drv: DRV2665
shift_register: ShiftRegister


def get_shift_register() -> ShiftRegister:
    spi = SPI(0, sck=Pin(6), mosi=Pin(7, mode=Pin.OUT), miso=Pin(4, mode=Pin.IN), baudrate=10_000)

    latch = Pin(5, mode=Pin.OUT)
    polarity = Pin(10, mode=Pin.OUT)

    shift_register = ShiftRegister(spi=spi, latch=latch, polarity=polarity)
    return shift_register


def get_drv() -> DRV2665:
    i2c = I2C(0, scl=Pin(1), sda=Pin(0))
    drv_found = scan_for_drv(i2c)
    if drv_found:
        print("DRV2665 found")
        drv = DRV2665(i2c=i2c)
        # drv.reset()

        drv.standby = False
        drv.input = INPUT_ANALOG
        drv.gain = GAIN_100V
        return drv
    else:
        print("DRV2665 not found")
        return None


def scan_for_drv(i2c: I2C):
    device_addresses = i2c.scan()
    print("I2C addresses:", [hex(device_address) for device_address in device_addresses])
    return DRV2665_ADDR in device_addresses


def main():
    global drv, shift_register
    # drv = get_drv()
    shift_register = get_shift_register()

    # shift_register.set_pin(1, True)
    # shift_register.set_pin(2, True)
    # shift_register.set_pin(3, True)
    # shift_register.set_pin(4, True)
    # shift_register.set_pin(5, True)
    # shift_register.set_pin(6, True)
    # shift_register.set_pin(7, True)
    # shift_register.set_pin(8, True)
    # shift_register.set_pin(9, True)
    # shift_register.set_pin(10, True)
    # shift_register.write()

    # drv.standby=False
    # drv.input=INPUT_ANALOG
    # drv.gain=GAIN_100V
    # drv.timeout=TIMEOUT_20MS
    # drv.enable=ENABLE_OVERRIDE
    time.sleep(10)


if __name__ == "__main__":
    main()
