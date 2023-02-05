from busio import SPI, I2C
from digitalio import DigitalInOut
import board
import time

from drv2665 import DRV2665, DRV2665_ADDR
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

def test_setup():
    global drv, shift_register
    
    drv = get_drv()
    shift_register = get_shift_register()


def test():
    global drv, shift_register
    
    print("drv I2C test...")
    drv.standby = True

    print("shift register SPI test")
    shift_register._validate()

    print("drv HV test")
    #assuming analog signal in
    drv.enable_analog()

    print("shift register HV test")
    shift_register.set_even_pins(latch=True)
    time.sleep(0.5)
    shift_register.reset(latch=True)
    time.sleep(0.5)
    shift_register.set_even_pins(latch=True)
    shift_register.toggle_polarity()
    time.sleep(0.5)
    shift_register.reset(latch=True)
    time.sleep(0.5)
    shift_register.set_odd_pins(latch=True)
    time.sleep(0.5)
    shift_register.reset(latch=True)
    time.sleep(0.5)
    shift_register.set_odd_pins(latch=True)
    shift_register.toggle_polarity()    
    time.sleep(0.5)

    print("test reset")
    shift_register.reset(latch=True)
    drv.reset()
    time.sleep(0.5)

    print("test complete")




def get_drv() -> DRV2665:
    i2c = I2C(scl=board.IO9, sda=board.IO8)
    drv_found = scan_for_drv(i2c)
    if drv_found:
        print("DRV2665 found")
        reset_drv(i2c)
        drv = DRV2665(i2c=i2c)

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
        time.sleep(0.5)
    finally:
        i2c.unlock()


def main():
    print("hello world")




if __name__ == "__main__":
    main()
