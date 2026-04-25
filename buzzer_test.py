from gpiozero import Buzzer
import time

# Aktiven Buzzer am GPIO-Pin 23 initialisieren
buzzer = Buzzer(23)

print("Starte Buzzer-Test...")
print("Du solltest jetzt 3 kurze Pieptöne hören.")

try:
    # Drei kurze Signaltöne mit jeweils 200ms Dauer ausgeben, die 200ms wurden von meiner uhr gemessen (nicht)
    for i in range(3):
        print(f"Piep {i+1}...")
        buzzer.on()
        time.sleep(0.2)
        buzzer.off()
        time.sleep(0.2)

    print("Hat geklappt, ist zu ende")

    # 
    while True:
        buzzer.beep(on_time=0.1, off_time=0.5)
        time.sleep(2)

except KeyboardInterrupt:
    buzzer.off()
    print("\nBuzzer stumm geschaltet. Test zu ende")
