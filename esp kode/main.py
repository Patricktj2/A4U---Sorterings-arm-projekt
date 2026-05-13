import usocket
import ujson
import time
from machine import I2C, Pin
from pca9685 import PCA9685
from servo import Servo
import config

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
    'gripper':     Servo(pca2, 2, *config.SERVO_LIMITS['gripper']),
}

SERVO_NAMES = ['base', 'shoulder', 'elbow', 'wrist', 'wrist_pitch', 'wrist_roll']

auto_busy = False

# ============================================================
# HJÆLPEFUNKTIONER
# ============================================================

def move_to(position, delay_ms=None):
    if delay_ms is None:
        delay_ms = config.MOVE_DELAY_MS
    for name, angle in zip(SERVO_NAMES, position):
        servos[name].write(angle)
    time.sleep_ms(delay_ms)

def grip(closed):
    angle = config.GRIPPER_CLOSED if closed else config.GRIPPER_OPEN
    servos['gripper'].write(angle)
    time.sleep_ms(config.GRIP_DELAY_MS)

def go_home():
    move_to(config.HOME)

def sort_brick(color):
    global auto_busy
    if color not in config.DROP_POSITIONS:
        return False
    auto_busy = True
    try:
        grip(closed=False)
        move_to(config.PICKUP_APPROACH)
        move_to(config.PICKUP_DOWN)
        grip(closed=True)
        move_to(config.PICKUP_APPROACH)
        move_to(config.DROP_POSITIONS[color])
        grip(closed=False)
        go_home()
    finally:
        auto_busy = False  # frigives altid, selv ved fejl
    return True

# ============================================================
# HTTP SERVER
# ============================================================

def start_server():
    addr = usocket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s    = usocket.socket()
    s.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    s.settimeout(0)
    print("HTTP server klar på port 80")
    return s

def parse_request(raw):
    try:
        idx = raw.find('\r\n\r\n')
        if idx == -1:
            return None
        return ujson.loads(raw[idx + 4:])
    except:
        return None

def handle_http(server):
    try:
        conn, addr = server.accept()
    except:
        return

    try:
        raw = conn.recv(1024).decode('utf-8')

        if 'POST /sort' in raw:
            if auto_busy:
                response = ujson.dumps({'status': 'busy'})
            else:
                data = parse_request(raw)
                if data and 'color' in data:
                    success = sort_brick(data['color'])
                    status  = 'ok' if success else 'unknown_color'
                else:
                    status = 'bad_request'
                response = ujson.dumps({'status': status})

        elif 'POST /home' in raw:
            go_home()
            response = ujson.dumps({'status': 'ok'})

        elif 'GET /ping' in raw:
            response = ujson.dumps({'status': 'alive'})

        else:
            response = ujson.dumps({'status': 'not_found'})

    except Exception as e:
        response = ujson.dumps({'status': 'error', 'msg': str(e)})

    finally:
        http = 'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n' + response
        conn.send(http.encode())
        conn.close()

# ============================================================
# START
# ============================================================
go_home()
server = start_server()
print("Klar — lytter på HTTP fra Pi")

while True:
    handle_http(server)
    time.sleep_ms(20)
