import requests
import time
import random
from gpiozero import PWMLED
from time import sleep

blue_led = PWMLED(20)  # Kék LED a GPIO 20 pinhez
red_led = PWMLED(21)   # Piros LED a GPIO 21 pinhez


# ThingSpeak API kulcs
API_KEY = 'G6SD9SSNQ5VACKKH'

# Adatok küldése a ThingSpeak-re
def send_data_to_thingspeak(temp, pressure):
    url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}&field2={pressure}'
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Sikeres adatküldés: Hőmérséklet={temp}, Légnyomás={pressure}")
    else:
        print(f"Sikertelen adatküldés: {response.status_code}")

# Végtelen ciklus 10 másodperces időközönként
while True:

    # Véletlenszerű hőmérséklet és légnyomás generálása
    temperature = round(random.uniform(15.0, 25.0), 2)  # Példa: 15-25°C között
    pressure = round(random.uniform(990.0, 1010.0), 2)   # Példa: 990-1010 hPa között
    print(f"Hőmérséklet: {temperature}°C, Légnyomás: {pressure} hPa")

    # led-ek kapcsolása a hőmérséklet alapján

    if temperature > 20:
        red_led.value = 1    # Piros LED bekapcsolása
        blue_led.value = 0   # Kék LED kikapcsolása
    else:
        red_led.value = 0    # Piros LED kikapcsolása
        blue_led.value = 1   # Kék LED bekapcsolása


    # Adatok küldése
    send_data_to_thingspeak(temperature, pressure)

    # 10 másodperces várakozás
    time.sleep(10)
