import time
import random
import board
import busio
import digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from gpiozero import LED, Buzzer
# theoretisch geht es auch mit UV ist auch 80mal besser aber für Sie haben wir das mal auf oldschool gemacht
print("Hardware überprüfen obs klappt")

# Abschnitt 1: Hardware-Initialisierung

# SPI-Bus und GPIO-Pins für das TFT-Display konfigurieren
spi = board.SPI()
cs_pin    = digitalio.DigitalInOut(board.D6)
dc_pin    = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# DisplayTreiber mit optimierter Baudrate für flüssige Darstellung, kann sein dass das display nochmehr rotiert werden muss, je nach Positionierung halt
disp = st7789.ST7789(
    spi, rotation=270, width=240, height=320,
    cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=60000000
)

# I2C-Bus und ADS1115 ADC für die Joystick-Eingabe initialisieren
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, data_rate=860)

# Analoge Joystick-Kanäle zuweisen (Achsenzuordnung an Verkabelung angepasst)
j1_x = AnalogIn(ads, 1)
j1_y = AnalogIn(ads, 0)
j2_x = AnalogIn(ads, 3)
j2_y = AnalogIn(ads, 2)

# LED und Buzzer als Feedback-Aktoren initialisieren und zurücksetzen
red_led = LED(17)
buzzer  = Buzzer(23)
red_led.off()
buzzer.off()

# Abschnitt 2: Spielkonfiguration und Konstanten

# Display-Auflösung und Blockgröße für das Spielraster, standart auflösung für das ding
WIDTH, HEIGHT = 320, 240
BLOCK_SIZE = 8

# Schwellenwerte für die Joystick-Erkennung (Totzone zwischen LOW und HIGH (bitte kein Stickdrift danke) ) war das eine rotze alter
LOW_THR  = 10000
HIGH_THR = 20000

# Farbdefinitionen im RGB-Format für Spielelemente
COLOR_BG   = (0,   0,   0)
COLOR_P1   = (0,   255, 0)
COLOR_P2   = (0,   100, 255)
COLOR_FOOD = (255, 255, 0)

# Bewegungsintervall in Sekunden (bestimmt die Spielgeschwindigkeit)
MOVE_DELAY = 0.12


def get_direction(vx, vy, current_dir):
    """Joystick-Werte auswerten und neue Richtung zurückgeben.
    Gibt einfach die alte Richtung zurück wenns keine valide Eingabe gibt, can_change_dir brauchts damit nicht mehr."""

    # Achsen sind invertiert wegen Verkabelung WICHTIG! bin halt faul
    if vx > HIGH_THR and current_dir != (BLOCK_SIZE, 0):
        return (-BLOCK_SIZE, 0)
    elif vx < LOW_THR and current_dir != (-BLOCK_SIZE, 0):
        return (BLOCK_SIZE, 0)
    elif vy < LOW_THR and current_dir != (0, BLOCK_SIZE):
        return (0, -BLOCK_SIZE)
    elif vy > HIGH_THR and current_dir != (0, -BLOCK_SIZE):
        return (0, BLOCK_SIZE)
    return current_dir


def move_snake(snake, head, food, score):
    """Schlange bewegen und bei Nahrungsaufnahme wachsen lassen bzw länger machen."""
    snake.insert(0, head)
    if head == food:
        score += 1
        food = (random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE))
    else:
        snake.pop()
    return snake, food, score


def reset_game():
    """Setzt den Spielzustand auf die Ausgangskonfiguration zurück.
    Beide Schlangen starten an gegenüberliegenden Seiten des Spielfelds."""
    return {
        "snake1": [(32, 120), (24, 120), (16, 120)],
        "dir1":   (BLOCK_SIZE, 0),
        "snake2": [(288, 120), (296, 120), (304, 120)],
        "dir2":   (-BLOCK_SIZE, 0),
        "food":   (random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE)),
        "score1": 0,
        "score2": 0,
    }


def game_over_sequence(winner_text):
    """Führt die Game-Over-Sequenz mit LED- und Buzzer-Feedback aus
    und zeigt den Ergebnisbildschirm auf dem Display an."""
    red_led.on()
    buzzer.on()
    time.sleep(0.5)
    buzzer.off()

    img = Image.new("RGB", (WIDTH, HEIGHT))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, WIDTH, HEIGHT), fill=(50, 0, 0))
    d.text((WIDTH//2 - 40, HEIGHT//2 - 20), "GAME OVER!", fill=(255, 255, 255))
    d.text((WIDTH//2 - 50, HEIGHT//2 + 10), winner_text, fill=(255, 255, 0))
    disp.image(img)

    time.sleep(3)
    red_led.off()


state = reset_game()

# Abschnitt 3: Hauptspielschleife

# Bildpuffer für das Rendering des Spielfelds vorbereiten
image = Image.new("RGB", (WIDTH, HEIGHT))
draw  = ImageDraw.Draw(image)

last_move_time = time.time()

print("SPIEL STARTET Drücke STRG C um zu Beenden")

try:
    while True:
        # Aktuelle Joystick-Positionen beider Spieler auslesen
        v1x, v1y = j1_x.value, j1_y.value
        v2x, v2y = j2_x.value, j2_y.value

        # Richtungssteuerung für beide Spieler, spart doppelten Code (war grausam)
        state["dir1"] = get_direction(v1x, v1y, state["dir1"])
        state["dir2"] = get_direction(v2x, v2y, state["dir2"])

        # Spiellogik nur im definierten Bewegungsintervall ausführen
        if time.time() - last_move_time >= MOVE_DELAY:

            # Neue Kopfpositionen berechnen
            head1 = (state["snake1"][0][0] + state["dir1"][0], state["snake1"][0][1] + state["dir1"][1])
            head2 = (state["snake2"][0][0] + state["dir2"][0], state["snake2"][0][1] + state["dir2"][1])

            # Bildschirmränder als Durchgang behandeln damit das Game nicht direkt zuende ist (kleiner workaround)
            head1 = (head1[0] % WIDTH, head1[1] % HEIGHT)
            head2 = (head2[0] % WIDTH, head2[1] % HEIGHT)

            # Kollisionserkennung: Kollision mit Gegner
            dead1 = head1 in state["snake1"] or head1 in state["snake2"]
            dead2 = head2 in state["snake2"] or head2 in state["snake1"]

            # Frontalzusammenstoss beider Schlangen prüfen
            if head1 == head2:
                dead1 = dead2 = True

            if dead1 or dead2:
                msg = "Unentschieden!" if (dead1 and dead2) else ("P2 gewinnt!" if dead1 else "P1 gewinnt!")
                game_over_sequence(msg)
                state = reset_game()
                last_move_time = time.time()
                continue

            # Beide Schlangen bewegen, Nahrung aufnehmen und Punkte aktualisieren
            state["snake1"], state["food"], state["score1"] = move_snake(state["snake1"], head1, state["food"], state["score1"])
            state["snake2"], state["food"], state["score2"] = move_snake(state["snake2"], head2, state["food"], state["score2"])

            # Spielfeld neu zeichnen: Hintergrund, Nahrung, beide Schlangen
            draw.rectangle((0, 0, WIDTH, HEIGHT), fill=COLOR_BG)
            draw.rectangle(
                (state["food"][0], state["food"][1],
                 state["food"][0] + BLOCK_SIZE - 1, state["food"][1] + BLOCK_SIZE - 1),
                fill=COLOR_FOOD
            )

            # Beide Schlangen zeichnen, Spieler 1 in grün, Spieler 2 in blau
            for snake, color in [(state["snake1"], COLOR_P1), (state["snake2"], COLOR_P2)]:
                for s in snake:
                    draw.rectangle((s[0], s[1], s[0] + BLOCK_SIZE - 1, s[1] + BLOCK_SIZE - 1), fill=color)

            # Punktestand beider Spieler am oberen Bildschirmrand anzeigen
            draw.text((5, 5),          f"P1: {state['score1']}", fill=COLOR_P1)
            draw.text((WIDTH - 45, 5), f"P2: {state['score2']}", fill=COLOR_P2)

            # Fertig gezeichnetes Bild an das Display senden (alles mit einem Bleistift gezeichnet, Künstler wären stolz)
            disp.image(image)

            last_move_time = time.time()

        time.sleep(0.001)

# LED und Buzzer immer aufräumen egal obs crasht oder man STRG C drückt
finally:
    red_led.off()
    buzzer.off()
    print("\nSpiel beendet")