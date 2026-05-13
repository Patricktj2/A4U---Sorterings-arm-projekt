from machine import I2C, Pin
import time

MODE1     = 0x00
PRESCALE  = 0xFE
LED0_ON_L = 0x06

class PCA9685:
    def __init__(self, i2c, address=0x40):
        self.i2c     = i2c
        self.address = address
        self._write(MODE1, 0x00)
        time.sleep_ms(5)

    def _write(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def _read(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def set_pwm_freq(self, freq_hz):
        prescale  = int(25000000.0 / (4096 * freq_hz) - 1)
        old_mode  = self._read(MODE1)
        self._write(MODE1, (old_mode & 0x7F) | 0x10)
        self._write(PRESCALE, prescale)
        self._write(MODE1, old_mode)
        time.sleep_ms(5)
        self._write(MODE1, old_mode | 0x80)

    def set_pwm(self, channel, on, off):
        reg  = LED0_ON_L + 4 * channel
        data = bytes([on & 0xFF, on >> 8, off & 0xFF, off >> 8])
        self.i2c.writeto_mem(self.address, reg, data)

    def set_pulse(self, channel, pulse_us):
        pulse_count = int(pulse_us * 4096 / 20000)
        self.set_pwm(channel, 0, pulse_count)