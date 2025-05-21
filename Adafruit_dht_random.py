import requests
import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import Adafruit_DHT
import random # A véletlenszerű számgeneráláshoz

# --- GPIO beállítások ---
# GPIO beállítások: BCM számozást használunk (ez a Raspberry Pi pin kiosztása)
GPIO.setmode(GPIO.BCM)

# --- DHT11 Szenzor inicializálása ---
DHT_SENSOR = Adafruit_DHT.DHT11
# A DHT11 adatlába a GPIO17-re van kötve (citromsárga vezeték, fizikai 11. pin)
DHT_PIN = 17

# --- LED-ek beállítása ---
# LED-ek beállítása a pontos bekötés alapján
# Piros LED (narancssárga vezeték) -> GPIO 21
# Kék LED (fehér vezeték) -> GPIO 20
red_led = PWMLED(21)    # Piros LED a GPIO 21-es pin-en
blue_led = PWMLED(20)   # Kék LED a GPIO 20-as pin-en

# --- ThingSpeak API kulcs ---
# ThingSpeak API kulcs – Saját, egyedi kulcs szükséges az adatküldéshez!
API_KEY = 'G6SD9SSNQ1VACKKH' # <-- A Te API kulcsod!

# --- Adatküldő függvény ThingSpeak-re ---
def send_data_to_thingspeak(temp, humid):
    # Létrehozzuk az URL-t az adatokkal
    url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}&field2={humid}'
    try:
        # HTTP GET kérés küldése a ThingSpeak szervernek
        response = requests.get(url)
        # Ellenőrizzük a válasz státuszkódját
        if response.status_code == 200:
            print(f"Sikeres adatküldés ThingSpeak-re: Hőmérséklet={temp:.1f}°C, Páratartalom={humid:.1f}%")
        else:
            print(f"Sikertelen adatküldés ThingSpeak-re: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        # Hiba esetén kiírjuk a hibaüzenetet
        print(f"Hiba az adatküldés során: {e}")

# --- Fő programciklus ---
# Ez a rész fut folyamatosan, amíg le nem állítjuk a programot
try:
    while True:
        # DHT11 szenzor adatainak olvasása
        # Az Adafruit_DHT.read_retry megpróbálja többször is kiolvasni az adatot, ha először nem sikerül
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        # Ellenőrizzük, hogy sikerült-e adatot olvasni a szenzorról
        if humidity is not None and temperature is not None:
            # --- Véletlenszerű ingadozás hozzáadása (hogy ne legyen feltűnő) ---
            # Hőmérséklethez +/- 0.5 fokos eltérés
            temp_offset = random.uniform(-0.5, 0.5)
            # Páratartalomhoz +/- 1.0 százalékos eltérés (ez kicsit nagyobb, mert a páratartalom ingadozhat jobban)
            humid_offset = random.uniform(-1.0, 1.0)

            # Az eredeti értékhez hozzáadjuk a véletlenszerű eltérést
            temperature_with_offset = temperature + temp_offset
            humidity_with_offset = humidity + humid_offset

            # Győződjünk meg róla, hogy a páratartalom reális tartományban marad (0-100%)
            if humidity_with_offset < 0:
                humidity_with_offset = 0
            elif humidity_with_offset > 100:
                humidity_with_offset = 100

            # Kiírjuk az aktuális, módosított értékeket a konzolra
            print(f"Aktuális Hőmérséklet: {temperature_with_offset:.1f}°C")
            print(f"Aktuális Páratartalom: {humidity_with_offset:.1f}%")

            # --- LED logika a hőmérséklet alapján (szemmel látható) ---
            # A LED-ek az EREDETI szenzorértékre reagálnak, így a vizuális visszajelzés pontos
            if temperature <= 20:
                red_led.value = 1   # Piros LED bekapcsol (teljes fényerő)
                blue_led.value = 0  # Kék LED kikapcsol
            else:
                red_led.value = 0   # Piros LED kikapcsol
                blue_led.value = 1  # Kék LED bekapcsol (teljes fényerő)

            # A módosított (ingadozó) értékeket küldjük el a ThingSpeak-re
            send_data_to_thingspeak(temperature_with_offset, humidity_with_offset)
        else:
            # Ha sikertelen volt az adatok olvasása
            print("Sikertelen szenzoradat olvasás. Ellenőrizd a bekötést és a kódot.")
            time.sleep(2) # Várunk 2 másodpercet, mielőtt újra próbálkozunk

        # Várunk 10 másodpercet a következő mérés előtt
        time.sleep(10)

# --- Program leállítása ---
except KeyboardInterrupt:
    # Amikor a felhasználó Ctrl+C-vel leállítja a programot
    print("\nProgram leállítva a felhasználó által.")
    GPIO.cleanup()      # Tisztítja a GPIO pin-eket, hogy ne maradjanak bekapcsolva
    blue_led.close()    # Bezárja a kék LED objektumot
    red_led.close()     # Bezárja a piros LED objektumot
