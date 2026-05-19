import usocket
import ujson
import time
from time import sleep
auto_busy = False

# ============================================================
# FAKE ROBOT-FUNKTIONER TIL TEST
# ============================================================

def go_home():
    print("TEST: Robot går hjem")
    return True

def sort_brick(farve, cx, cy):
    global auto_busy

    if auto_busy:
        return False

    auto_busy = True

    try:
        

        # Simuler at robotten arbejder lidt
        time.sleep(2)
        
        print("farve:", farve, "koordinater:", cx, cy)

#        print("leder efter dobbel glizzy", farve)
#        sleep(1)
#        print("leder ...", farve)
#        sleep(1)
#        print("....", farve)
#        sleep(0.5)
#        print("kun en glizzy fundet", farve)
#        sleep(1)
#        print("jeg har nu trunket single glizzy", farve)

    finally:
        auto_busy = False

    return True


# ============================================================
# HTTP SERVER
# ============================================================

def start_server():
    addr = usocket.getaddrinfo("0.0.0.0", 80)[0][-1]

    s = usocket.socket()
    s.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    s.settimeout(0)

    print("HTTP server klar på port 80")
    return s


def parse_request(raw):
    try:
        idx = raw.find("\r\n\r\n")

        if idx == -1:
            return None

        body = raw[idx + 4:]

        if not body:
            return None

        return ujson.loads(body)

    except Exception as e:
        print("JSON parse fejl:", e)
        return None


def send_response(conn, status_code, data):
    body = ujson.dumps(data)

    http = (
        "HTTP/1.1 {} OK\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
        "{}"
    ).format(status_code, len(body), body)

    conn.send(http.encode())


def handle_http(server):
    try:
        conn, addr = server.accept()
    except:
        return

    try:
        raw = conn.recv(1024).decode("utf-8")

        print("Request fra:", addr)
        print(raw)

        if raw.startswith("GET /ping"):
            send_response(conn, 200, {
                "status": "alive",
                "device": "esp32"
            })

        elif raw.startswith("POST /home"):
            go_home()
            send_response(conn, 200, {
                "status": "ok",
                "action": "home"
            })

        elif raw.startswith("POST /sort"):
            global auto_busy

            if auto_busy:
                send_response(conn, 200, {
                    "status": "busy"
                })
                return

            data = parse_request(raw)

            if data and "farve" in data:
                farve = data["farve"]
                cx = data["cx"]
                cy = data["cy"]
                success = sort_brick(farve, cx, cy)

                if success:
                    send_response(conn, 200, {
                        "status": "ok",
                        "farve": farve
                    })
                else:
                    send_response(conn, 200, {
                        "status": "busy"
                    })
            else:
                send_response(conn, 400, {
                    "status": "bad_request",
                    "msg": "Mangler farve"
                })

        else:
            send_response(conn, 404, {
                "status": "not_found"
            })

    except Exception as e:
        print("Server fejl:", e)

        try:
            send_response(conn, 500, {
                "status": "error",
                "msg": str(e)
            })
        except:
            pass

    finally:
        conn.close()


# ============================================================
# START
# ============================================================

server = start_server()
print("Klar. ESP32 lytter på HTTP.")

while True:
    handle_http(server)
    time.sleep_ms(20)