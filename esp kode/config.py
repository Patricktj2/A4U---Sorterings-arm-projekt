# ============================================================
# NETVÆRK
# ⚠️ Ret PI_IP hvis Pi ikke sidder på .2
# ============================================================
PI_IP   = '192.168.0.2'
PI_PORT = 5000

# ============================================================
# I2C PINS
# ✅ Rør ikke medmindre ledningerne fysisk flyttes
# ============================================================
I2C_SDA_PIN = 21
I2C_SCL_PIN = 22

# ============================================================
# PCA9685 ADRESSER
# ✅ Board 1 = 0x40 (ingen broer), Board 2 = 0x41 (A0-bro loddet)
# ============================================================
PCA_ADDR_1 = 0x40
PCA_ADDR_2 = 0x41

# ============================================================
# SERVO GRÆNSER (mikrosekunder)
# ⚠️ Justér kun hvis en servo rammer mekanisk stop
# ============================================================
SERVO_LIMITS = {
    'base':        (500, 2500),
    'shoulder':    (500, 2500),
    'elbow':       (500, 2500),
    'wrist':       (500, 2500),
    'wrist_pitch': (500, 2500),
    'wrist_roll':  (500, 2500),
    'gripper':     (500, 2500),
}

# ============================================================
# ARM POSITIONER (grader 0–180)
# ⚠️ SKAL KALIBRERES FYSISK
# Format: [base, shoulder, elbow, wrist, wrist_pitch, wrist_roll]
# ============================================================
HOME            = [90, 45, 135, 90, 90, 90]
SCAN            = [90, 80, 100, 90, 90, 90]

GRIPPER_OPEN    = 30
GRIPPER_CLOSED  = 90

PICKUP_APPROACH = [90, 60, 120, 90, 90, 90]
PICKUP_DOWN     = [90, 45, 145, 90, 90, 90]

DROP_POSITIONS  = {
    'roed':  [45,  50, 130, 90, 90, 90],
    'gul':   [90,  50, 130, 90, 90, 90],
    'groen': [135, 50, 130, 90, 90, 90],
}

# ============================================================
# TIMING (millisekunder)
# ⚠️ Øg MOVE_DELAY_MS hvis armen ikke når at bevæge sig færdigt
# ============================================================
MOVE_DELAY_MS = 600
GRIP_DELAY_MS = 400