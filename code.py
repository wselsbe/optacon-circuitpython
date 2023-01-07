from busio import I2C, SPI
from digitalio import DigitalInOut
import board

from drv2665 import DRV2665, DRV2665_ADDR
from shift_register import ShiftRegister

drv: DRV2665
shift_register: ShiftRegister

def get_shift_register() -> ShiftRegister:
    spi = SPI(clock = board.GP6, MOSI=board.GP7, MISO=board.GP8)

    latch = DigitalInOut(board.GP11)
    latch.switch_to_output()

    polarity=DigitalInOut(board.GP10)
    polarity.switch_to_output()

    shift_register = ShiftRegister(spi=spi, latch=latch, polarity=polarity)
    return shift_register

def get_drv() -> DRV2665:
    i2c = I2C(scl = board.GP1, sda=board.GP0)
    drv_found = scan_for_drv(i2c)
    if drv_found:
        print("DRV2665 found")
        drv = DRV2665(i2c=i2c)
        drv.reset()
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


def main():
    drv = get_drv()
    shift_register = get_shift_register()

if __name__ == "__main__":
    main()