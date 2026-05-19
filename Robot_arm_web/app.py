from flask import Flask, render_template, redirect, url_for, jsonify    
import libcamera
from picamera2 import Picamera2
from datetime import datetime
import time
from sqlite3 import Connection
import urllib.request


ESP_IP="192.168.0.3"


def select_images(amount):
    if isinstance(amount, int) and amount > 0:
        con = Connection('dataarm.db')
        cur = con.cursor()
        sql = f"""SELECT filnavn, Dato_tid FROM A4U_images ORDER BY rowid DESC LIMIT {amount}"""
        cur.execute(sql)
        img_rows = cur.fetchall()
        print(img_rows)
        con.close()
        return img_rows

def insert_img(filnavn):
    con = Connection('dataarm.db')
    cur = con.cursor()
    dato_tid = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    params = (filnavn, 2, dato_tid)
    sql = """INSERT INTO A4U_images (filnavn, antal_sorteret, Dato_tid) VALUES(?, ?, ?)"""
    cur.execute(sql, params)
    con.commit()
    con.close()

    print("Gemt i databasen:", filnavn)

    

def take_picture():
    date_time = datetime.now()
    datetime_img = f"{date_time.strftime('%d-%m-%Y-%H-%M-%S')}.jpg"

    picam = Picamera2()
    config = picam.create_still_configuration(
        main={"size": (640, 480)},
        buffer_count=1
    )


    picam.configure(config)
    picam.start()
    time.sleep(2)

    picam.capture_file(f"static/img/{datetime_img}")
    insert_img(datetime_img)

    picam.stop()
    picam.close()


#take_picture()

app = Flask(__name__)

@app.route("/take_photo/")
def take_photo():
    # tager et nyt billede
    take_picture()
    # laver et redirect tilbage til home når billedet er taget
    return redirect(url_for("home"))


@app.route("/")
def home():
    latest = select_images(1)[0]
    taeller_rows = select_taeller()

    return render_template(
        "home.html",
        image=latest[0],
        dato_tid=latest[1],
        taeller_rows=taeller_rows
    )


@app.route("/galleri/")
def galleri():
    image_rows = select_images(1000)
    return render_template("galleri.html", image_rows=image_rows)


#pp.route("/site2/")
#ef site2():
    # return render_template("site2.html")
    #ass


@app.route("/robot_on/")
def robot_on():
    urllib.request.urlopen(f"http://{ESP_IP}/on")
    return redirect(url_for("home"))


@app.route("/robot_off/")
def robot_off():
    urllib.request.urlopen(f"http://{ESP_IP}/off")
    return redirect(url_for("home"))

def select_taeller():
    con = Connection('dataarm.db')
    cur = con.cursor()

    cur.execute("""SELECT farve, antal FROM "tæller" """)
    rows = cur.fetchall()

    con.close()
    return rows

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)