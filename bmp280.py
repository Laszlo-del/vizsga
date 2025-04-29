import requests
import time
from smbus2 import SMBus
from bmp280 import BMP280
from gpiozero import PWMLED

# Kék LED a GPIO 20 pinhez
blue_led = PWMLED(20)
# Piros LED a GPIO 21 pinhez
red_led = PWMLED(21)

# ThingSpeak API kulcs
API_KEY = 'G6SD9SSNQ5VACKKH'

# Adatok küldése a ThingSpeak-re
def send_data_to_thingspeak(temp, pressure):
    # URL módosítva a valós adatokkal
    url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}&field2={pressure}'
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Sikeres adatküldés: Hőmérséklet={temp}, Légnyomás={pressure}")
    else:
        print(f"Sikertelen adatküldés: {response.status_code}")

# BMP280 inicializálása
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)

# Végtelen ciklus 10 másodperces időközönként
while True:
    # Szenzoradatok lekérdezése
    temperature = bmp280.get_temperature()
    pressure = bmp280.get_pressure()
    print(f"{temperature:05.2f}*C {pressure:05.2f}hPa")

    # LED-ek kapcsolása a hőmérséklet alapján
    if temperature > 20:
        red_led.value = 1   # Piros LED bekapcsolása
        blue_led.value = 0  # Kék LED kikapcsolása
    else:
        red_led.value = 0   # Piros LED kikapcsolása
        blue_led.value = 1  # Kék LED bekapcsolása

    # Adatok küldése
    send_data_to_thingspeak(temperature, pressure)

    # 10 másodperces várakozás
    time.sleep(10)
