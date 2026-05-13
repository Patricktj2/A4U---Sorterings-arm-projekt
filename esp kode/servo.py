class Servo:
    def __init__(self, pca, channel, min_us=500, max_us=2500):
        self.pca     = pca
        self.channel = channel
        self.min_us  = min_us
        self.max_us  = max_us

    def write(self, degrees):
        degrees  = max(0, min(180, degrees))
        pulse_us = self.min_us + (self.max_us - self.min_us) * degrees / 180
        self.pca.set_pulse(self.channel, int(pulse_us))