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

print("Hardware überprüfen obs klappt")

#  1 HARDWARE SETUP 
spi = board.SPI()
cs_pin = digitalio.DigitalInOut(board.D6)    # Pin 31
dc_pin = digitalio.DigitalInOut(board.D24)   # Pin 18
reset_pin = digitalio.DigitalInOut(board.D25)# Pin 22

disp = st7789.ST7789(
    spi, rotation=270, width=240, height=320,
    cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=60000000 
)

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, data_rate=860) 

j1_x = AnalogIn(ads, 1) 
j1_y = AnalogIn(ads, 0) 
j2_x = AnalogIn(ads, 3) 
j2_y = AnalogIn(ads, 2) 

red_led = LED(17)
buzzer = Buzzer(23)
red_led.off()
buzzer.off()

#  2 SPIEL-KONFIGURATION 
WIDTH, HEIGHT = 320, 240
BLOCK_SIZE = 8

LOW_THR = 10000
HIGH_THR = 20000

COLOR_BG = (0, 0, 0)
COLOR_P1 = (0, 255, 0)
COLOR_P2 = (0, 100, 255)
COLOR_FOOD = (255, 255, 0)

MOVE_DELAY = 0.12 

def reset_game():
    s1 = [(32, 120), (24, 120), (16, 120)]
    d1 = (BLOCK_SIZE, 0)
    s2 = [(288, 120), (296, 120), (304, 120)]
    d2 = (-BLOCK_SIZE, 0)
    f = (random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE))
    return s1, d1, s2, d2, f, 0, 0

snake1, dir1, snake2, dir2, food, score1, score2 = reset_game()

def game_over_sequence(winner_text):
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

# 3 HAUPTSCHLEIFE 
image = Image.new("RGB", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

last_move_time = time.time()
can_change_dir1 = True
can_change_dir2 = True

print("SPIEL STARTET Drücke STRG C um ui Beenden")

try:
    while True:
        v1x, v1y = j1_x.value, j1_y.value
        v2x, v2y = j2_x.value, j2_y.value

        # STEUERUNG P1 
        if can_change_dir1:
            # X-Achse (Links/Rechts) - LOGIK UMGEDREHT WEIL FALSCH VERKABELT bin halt faul bro kb mehr auf Kabel gehabt
            if v1x > HIGH_THR and dir1 != (BLOCK_SIZE, 0):    
                dir1 = (-BLOCK_SIZE, 0); can_change_dir1 = False  # Links
            elif v1x < LOW_THR and dir1 != (-BLOCK_SIZE, 0): 
                dir1 = (BLOCK_SIZE, 0); can_change_dir1 = False   # Rechts
            
            # Y-Achse (Hoch/Runter) 
            elif v1y < LOW_THR and dir1 != (0, BLOCK_SIZE):   
                dir1 = (0, -BLOCK_SIZE); can_change_dir1 = False  # Hoch
            elif v1y > HIGH_THR and dir1 != (0, -BLOCK_SIZE): 
                dir1 = (0, BLOCK_SIZE); can_change_dir1 = False   # Runter

        #  STEUERUNG P2 
        if can_change_dir2:
            # X-Achse (Links/Rechts) - LOGIK UMGEDREHT SIEHE OBEN LASS DAS SO 
            if v2x > HIGH_THR and dir2 != (BLOCK_SIZE, 0):    
                dir2 = (-BLOCK_SIZE, 0); can_change_dir2 = False
            elif v2x < LOW_THR and dir2 != (-BLOCK_SIZE, 0): 
                dir2 = (BLOCK_SIZE, 0); can_change_dir2 = False
                
            # Y-Achse (Hoch/Runter)  Bleibt gleich
            elif v2y < LOW_THR and dir2 != (0, BLOCK_SIZE):   
                dir2 = (0, -BLOCK_SIZE); can_change_dir2 = False
            elif v2y > HIGH_THR and dir2 != (0, -BLOCK_SIZE): 
                dir2 = (0, BLOCK_SIZE); can_change_dir2 = False

        if time.time() - last_move_time >= MOVE_DELAY:
            head1 = (snake1[0][0] + dir1[0], snake1[0][1] + dir1[1])
            head2 = (snake2[0][0] + dir2[0], snake2[0][1] + dir2[1])

            head1 = (head1[0] % WIDTH, head1[1] % HEIGHT)
            head2 = (head2[0] % WIDTH, head2[1] % HEIGHT)

            dead1 = head1 in snake1 or head1 in snake2
            dead2 = head2 in snake2 or head2 in snake1
            
            if head1 == head2: dead1 = dead2 = True

            if dead1 or dead2:
                msg = "Unentschieden!" if (dead1 and dead2) else ("P2 gewinnt!" if dead1 else "P1 gewinnt!")
                game_over_sequence(msg)
                snake1, dir1, snake2, dir2, food, score1, score2 = reset_game()
                last_move_time = time.time()
                can_change_dir1 = can_change_dir2 = True
                continue

            snake1.insert(0, head1)
            if head1 == food:
                score1 += 1
                food = (random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE))
            else:
                snake1.pop()

            snake2.insert(0, head2)
            if head2 == food:
                score2 += 1
                food = (random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE))
            else:
                snake2.pop()

            draw.rectangle((0, 0, WIDTH, HEIGHT), fill=COLOR_BG)
            draw.rectangle((food[0], food[1], food[0]+BLOCK_SIZE-1, food[1]+BLOCK_SIZE-1), fill=COLOR_FOOD)
            
            for s in snake1: draw.rectangle((s[0], s[1], s[0]+BLOCK_SIZE-1, s[1]+BLOCK_SIZE-1), fill=COLOR_P1)
            for s in snake2: draw.rectangle((s[0], s[1], s[0]+BLOCK_SIZE-1, s[1]+BLOCK_SIZE-1), fill=COLOR_P2)

            draw.text((5, 5), f"P1: {score1}", fill=COLOR_P1)
            draw.text((WIDTH - 45, 5), f"P2: {score2}", fill=COLOR_P2)

            disp.image(image)

            last_move_time = time.time()
            can_change_dir1 = True
            can_change_dir2 = True

        time.sleep(0.001)

except KeyboardInterrupt:
    red_led.off()
    buzzer.off()
    print("\nSpiel beendet")
