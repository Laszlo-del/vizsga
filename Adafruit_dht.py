import requests
import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import Adafruit_DHT

# GPIO beállítások
GPIO.setmode(GPIO.BCM)

# DHT11 szenzor
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 17  # GPIO17

# LED-ek beállítása
blue_led = PWMLED(20)  # Kék LED
red_led = PWMLED(21)   # Piros LED

# ThingSpeak API kulcs
API_KEY = 'G6SD9SSNQ5VACKKH'  # ← cseréld ki a sajátodra, ha kell

# Adatok küldése ThingSpeak-re
def send_data_to_thingspeak(temp, humid):
    url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}&field2={humid}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Sikeres adatküldés: {temp:.1f}°C, {humid:.1f}%")
        else:
            print(f"Sikertelen adatküldés: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Hiba az adatküldés során: {e}")

# Fő program
try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            print(f"Hőmérséklet: {temperature:.1f}°C")
            print(f"Páratartalom: {humidity:.1f}%")

            # LED logika
            if temperature > 20:
                red_led.value = 1
                blue_led.value = 0
            else:
                red_led.value = 0
                blue_led.value = 1

            # ThingSpeak adatküldés
            send_data_to_thingspeak(temperature, humidity)
        else:
            print("Sikertelen szenzorolvasás.")
            time.sleep(2)

        time.sleep(10)

except KeyboardInterrupt:
    print("Leállítás kérése érkezett.")

    
