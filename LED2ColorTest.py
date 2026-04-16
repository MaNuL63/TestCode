from gpiozero import LED
import time

red = LED(17)
green = LED(26)

# Rot an
red.on()
time.sleep(1)
red.off()

# Grün an
green.on()
time.sleep(5)
green.off()

# Beide an (ergibt "Yellow")
red.on()
green.on()
