# ============================================================
# test_manuel.py
# Kør denne fil direkte fra Thonny under bygning og kalibrering.
# Erstatter IKKE main.py — upload begge, kør denne manuelt.
#
# Mode 2 (blå LED):
#   Joy1 Y  → base
#   Joy2 X  → skulder
#   Pot     → albue direkte
#   Joy1 SW → håndled roll venstre
#   Joy2 SW → håndled roll højre
#   sh      → griber lukket
#   sv      → griber åben
#   sn      → go home
#
# Mode 3 (rød LED):
#   Joy1 Y  → håndled pitch
#   Joy2 X  → håndled rotation
#   Pot     → håndled roll direkte
#   sh      → griber lukket
#   sv      → griber åben
#   sn      → griber neutral
# ============================================================

import espnow
import network
import ujson
import time
from machine import I2C, Pin
from pca9685 import PCA9685
from servo import Servo
import config

# ⚠️ Indsæt controllerens MAC-adresse her
CONTROLLER_MAC = b'\xXX\xXX\xXX\xXX\xXX\xXX'

# Grader armen bevæger sig per tick ved fuld joystick
STEP = 2

# --- I2C og PCA9685 ---
i2c  = I2C(0, sda=Pin(config.I2C_SDA_PIN), scl=Pin(config.I2C_SCL_PIN), freq=400000)
pca1 = PCA9685(i2c, config.PCA_ADDR_1)
pca2 = PCA9685(i2c, config.PCA_ADDR_2)
pca1.set_pwm_freq(50)
pca2.set_pwm_freq(50)

# --- Servos ---
servos = {
    'base':        Servo(pca1, 0, *config.SERVO_LIMITS['base']),
    'shoulder':    Servo(pca1, 1, *config.SERVO_LIMITS['shoulder']),
    'elbow':       Servo(pca1, 2, *config.SERVO_LIMITS['elbow']),
    'wrist':       Servo(pca1, 3, *config.SERVO_LIMITS['wrist']),
    'wrist_pitch': Servo(pca2, 0, *config.SERVO_LIMITS['wrist_pitch']),
    'wrist_roll':  Servo(pca2, 1, *config.SERVO_LIMITS['wrist_roll']),
    'gripper':     Servo(pca2, 2, *config.SERVO_LIMITS[