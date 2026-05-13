import cv2
import numpy as np
import time
from picamera2 import Picamera2

# Definere farver og deres grænser #

COLOR_RANGES = {
    "red": [
        (np.array([0,   120, 70]), np.array([10,  255, 255])),
        (np.array([170, 120, 70]), np.array([180, 255, 255])),
    ],
    "yellow": [
        (np.array([20, 100, 100]), np.array([35, 255, 255])),
    ],
    "green": [
        (np.array([40, 70, 70]), np.array([80, 255, 255])),
    ],
}

# Definere kamera og starter det #

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(2)

# Tager selve billedet og konvertere det til et array #

frame = picam2.capture_array()                 # Gemmer billedet som en matrix array
picam2.stop() 
frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Laver en funktion som kaldes frame der konvertere RGB til BGR

# Gør billed klar til behandling #

output = frame.copy()
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)    # Laver en funktion som kaldes hsv som via opencv konvertere farver fra BGR til HSV
funde_farver = []                               # Laver en tom liste som hedder funde_farver

# Farve detektion for loop #

for farve, intervaller in COLOR_RANGES.items():
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8) # Laver en helt sort maske i samme shape som billedet
    for lower, upper in intervaller:
        mask |= cv2.inRange(hsv, lower, upper)     # Bruger den sorte maske med en OR (|=) til at kombinere røde pixels med den sorte maske
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Scanner masken og returnere der hvor der er hvide pixels
    for cnt in contours:
        if cv2.contourArea(cnt) < 400: # Beregner størrelsen af de hvide pixel områder og springer over hvis det er under 400 pixels da det er støj
            continue
        
        M = cv2.moments(cnt) # Berenger statistik omkring området og om chancen for det er en farve
        if M["m00"] == 0: # Sørger for at hvis der er et område som bliver registeret som 0 så springer den det over så det ikke crasher
            continue
        
        cx = int(M["m10"] / M["m00"]) # Begge disse er centrum koordinater
        cy = int(M["m01"] / M["m00"]) # Bliver beregnet ved at dividere de vægtede summer med det totale areal

        cv2.circle(output, (cx, cy), 10, (0, 255, 0), -1)                                               # Laver en grøn cirkel ved centrum koordinaterne
        cv2.putText(output, farve, (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)   # Skriver farve nanvet over cirklen
        funde_farver.append((farve, cx, cy))                                                            # Gemmer farven og koordinater i listen

# Billed output #

if funde_farver: 
    print("Farver fundet")

    for farve, cx, cy in funde_farver:
        print(f"{farve} på pixel ({cx},{cy})") # Printer den farve som er fundet og dets koordinater på billedet
else:
    print("Ingen farver fundet") 

cv2.imwrite("resultat.jpg", output)
print("Billed gemt som resultat.jpg")