import requests
import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO

# GPIO beállítások
GPIO.setmode(GPIO.BCM)
sensor_pin = 17  # A KY-028 digitális kimenetéhez csatlakoztatott pin

# LED-ek beállítása
blue_led = PWMLED(20)  # Kék LED a GPIO 20 pinhez
red_led = PWMLED(21)   # Piros LED a GPIO 21 pinhez

# ThingSpeak API kulcs
API_KEY = 'G6SD9SSNQ5VACKKH'

# Adatok küldése a ThingSpeak-re
def send_data_to_thingspeak(temp):
    # URL módosítva a valós adatokkal
    url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}'
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Sikeres adatküldés: Hőmérséklet={temp}")
    else:
        print(f"Sikertelen adatküldés: {response.status_code}")

# GPIO beállítások
GPIO.setup(sensor_pin, GPIO.IN)

# Végtelen ciklus 10 másodperces időközönként
while True:
    # Digitális bemenet beolvasása a KY-028-ról
    if GPIO.input(sensor_pin):  # Ha a pin magas (1), akkor a hőmérséklet meghaladja a küszöböt
        temperature = 25  # Ezt a hőmérsékletet beállíthatod egy konstans értékként, vagy más módon
    else:
        temperature = 15  # Alacsony hőmérséklet, ha a pin alacsony (0)

    print(f"Hőmérséklet: {temperature}°C")

    # LED-ek vezérlése a hőmérséklet alapján
    if temperature > 20:
        red_led.value = 1   # Piros LED bekapcsolása
        blue_led.value = 0  # Kék LED kikapcsolása
    else:
        red_led.value = 0   # Piros LED kikapcsolása
        blue_led.value = 1  # Kék LED bekapcsolása

    # Adatok küldése a ThingSpeak-re
    send_data_to_thingspeak(temperature)

    # 10 másodperces várakozás
    time.sleep(10)
