import board
import digitalio
from adafruit_rgb_display import st7789
from PIL import Image, ImageDraw

print("Test mit ST7789 Treiber")

# SPI-Schnittstelle initialisieren für die Kommunikation mit dem Display
spi = board.SPI()

# GPIO-Pins für Chip Select, Data/Command und Reset definieren
cs_pin = digitalio.DigitalInOut(board.D6)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# ST7789 Display-Treiber mit den konfigurierten Pins und Parametern laden, Rotation anpassen je nach Montage des Displays
disp = st7789.ST7789(
    spi,
    rotation=90,
    width=240,
    height=320,
    x_offset=0,
    y_offset=0,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=24000000
)

# Bildpuffer mit der nativen Display-Auflösung erzeugen
width = 320
height = 240
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

# Testbild zeichnen: grüner Hintergrund mit schwarzem Rahmen und zentriertem Text
draw.rectangle((0, 0, width, height), fill=(0, 255, 0))
draw.rectangle((0, 0, width-1, height-1), outline=(0, 0, 0), width=10)
draw.text((width // 2 - 40, height // 2), "ST7789 TEST", fill="black")

# Bild an das Display senden, bei Fehler alternative Rotation versuchen
try:
    disp.image(image)
    print("geklappt")
except ValueError:
    print("kritischer Hase")
    disp.image(image, rotation=90)
