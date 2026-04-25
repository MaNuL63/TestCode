from gpiozero import LED
import time

# GPIO-Pins fürr die zweifarbige LED, wo ich aber nur die eine Farbe benutze, weil grün mir durchgebrannt ist 
red = LED(17)
green = LED(26)

# Rote LED für eine Sekunde aktivieren
red.on()
time.sleep(1)
red.off()

