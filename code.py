from busio import SPI
from digitalio import DigitalInOut
import board
import time

from drv2665 import *
from shift_register import ShiftRegister

drv: DRV2665
shift_register: ShiftRegister


def get_shift_register() -> ShiftRegister:
    spi = SPI(clock=board.IO36, MOSI=board.IO35, MISO=board.IO37)
    while not spi.try_lock():
        time.sleep(0)


    shift_register = ShiftRegister(spi=spi, latch=board.IO7, polarity=board.IO34)
    return shift_register
    #return None



def get_drv() -> DRV2665:
    i2c = I2C(scl=board.IO9, sda=board.IO8)
    drv_found = scan_for_drv(i2c)
    if drv_found:
        print("DRV2665 found")
        reset_drv(i2c)
        drv = DRV2665(i2c=i2c)

        drv.standby = False
        drv.input = INPUT_ANALOG
        drv.gain = GAIN_100V
        # drv.reset()
        return drv
    else:
        print("DRV2665 not found")
        return None


def scan_for_drv(i2c: I2C):
    while not i2c.try_lock():
        pass
    try:
        device_addresses = i2c.scan()
        print("I2C addresses:", [hex(device_address) for device_address in device_addresses])
        return DRV2665_ADDR in device_addresses
    finally:
        i2c.unlock()


def reset_drv(i2c: I2C):
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto(DRV2665_ADDR, bytes([0x02, 1 << 7]))
        time.sleep(1)
    finally:
        i2c.unlock()


def main():
    print("hello world")
    global drv, shift_register
    # drv = get_drv()
    shift_register = get_shift_register()
    print("get done")

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
