from gpiozero import Buzzer
import time

# GPIO pin 
buzzer = Buzzer(23)

print("Starte Buzzer-Test...")
print("Du solltest jetzt 3 kurze Pieptöne hören.")

try:
    for i in range(3):
        print(f"Piep {i+1}...")
        buzzer.on()
        time.sleep(0.2)  
        buzzer.off()
        time.sleep(0.2)  

    print("Hat geklappt, ist zu ende")
    
    # random auf github gefunden, ist ganz nice eigtl. 
    while True:
        buzzer.beep(on_time=0.1, off_time=0.5)
        time.sleep(2)

except KeyboardInterrupt:
    buzzer.off()
    print("\nBuzzer stumm geschaltet. Test zu ende")