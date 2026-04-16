import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

print("Joystick Signal vorhanden ")

try:
    # 1 I2C Bus Verbindung
    i2c = busio.I2C(board.SCL, board.SDA)

    # 2 ob er den ads findet
    ads = ADS.ADS1115(i2c)
    print("ADS1115 da")

    # 3. Die 4 Kanäle definieren (Wir nutzen einfach 0, 1, 2, 3)
    # Das ist der Ersatz für ADS.P0, ADS.P1 etc.
    j1_x = AnalogIn(ads, 0)
    j1_y = AnalogIn(ads, 1)
    j2_x = AnalogIn(ads, 2)
    j2_y = AnalogIn(ads, 3)

    print("-" * 40)
    print("Sticks bewegen")
    print("Abbrechen mit STRG+C Roger")
    print("-" * 40)

    while True:
        # Werte auslesen zum checken
        v1x, v1y = j1_x.value, j1_y.value
        v2x, v2y = j2_x.value, j2_y.value

        # Anzeige der deadzones bzw. Werte, kp was das heißt sieht man in der Doku)
        print(f"J1: X={v1x:>5} Y={v1y:>5}  |  J2: X={v2x:>5} Y={v2y:>5}", end="\r")
        
        time.sleep(0.1)

except Exception as e:
    print(f"\nFehler: {e}")
    print("i2c fehler")

except KeyboardInterrupt:
    print("\n\nTest beendet")