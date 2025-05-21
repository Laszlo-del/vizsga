import requests
import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import Adafruit_DHT

# GPIO beállítások
# GPIO.setmode(GPIO.BCM) - Ez a sor dönti el, hogyan számozzuk a Raspberry Pi GPIO lábait.
# A "BCM" (Broadcom SOC Channel) módszer a CPU belső GPIO pin sorszámait használja.
# Ez az ajánlott mód, és a kódban a DHT_PIN = 17 is ezt a számozást követi (ami a fizikai 11. pin).
GPIO.setmode(GPIO.BCM)

# DHT11 szenzor
DHT_SENSOR = Adafruit_DHT.DHT11 # Meghatározzuk, hogy DHT11 szenzort használunk
DHT_PIN = 17 # A DHT11 adatlábát a GPIO17-re kötöttem

# LED-ek beállítása
blue_led = PWMLED(20)   # Kék LED a GPIO 20 pinhez
red_led = PWMLED(21)    # Piros LED a GPIO 21 pinhez

# ThingSpeak API kulcs
API_KEY = 'G6SD9SSNQ5VACKKH' # <-- Ne felejtsd el kicserélni a SAJÁT ThingSpeak API kulcsodra!

# Adatok küldése ThingSpeak-re
def send_data_to_thingspeak(temp, humid):
    # A ThingSpeak API URL-je, ahová a hőmérsékletet (field1) és a páratartalmat (field2) küldjük
    url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}&field2={humid}'
    try:
        response = requests.get(url)
        # Ellenőrizzük, hogy az adatküldés sikeres volt-e (HTTP 200 OK)
        if response.status_code == 200:
            print(f"Sikeres adatküldés ThingSpeak-re: Hőmérséklet={temp:.1f}°C, Páratartalom={humid:.1f}%")
        else:
            # Hiba esetén kiírjuk a státuszkódot és a hibaüzenetet
            print(f"Sikertelen adatküldés ThingSpeak-re: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        # Hálózat vagy egyéb hiba esetén kiírjuk a kivételt
        print(f"Hiba az adatküldés során: {e}")

# Fő program futtatása try-except blokkban, hogy le lehessen állítani (Ctrl+C)
try:
    while True:
        # Beolvassuk a páratartalmat és a hőmérsékletet a DHT11-ről
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        # Ellenőrizzük, hogy az olvasás sikeres volt-e
        if humidity is not None and temperature is not None:
            print(f"Aktuális Hőmérséklet: {temperature:.1f}°C")
            print(f"Aktuális Páratartalom: {humidity:.1f}%")

            # **LED logika: 20 fok alatt PIROS, felette KÉK**
            if temperature <= 20: # Ha a hőmérséklet HŰVÖSEBB VAGY EGYENLŐ 20 fokkal
                red_led.value = 1   # Piros LED bekapcsolása (teljes fényerő)
                blue_led.value = 0  # Kék LED kikapcsolása
            else: # Ha a hőmérséklet MELEGEBB mint 20 fok
                red_led.value = 0   # Piros LED kikapcsolása
                blue_led.value = 1  # Kék LED bekapcsolása

            # Adatok küldése a ThingSpeak-re
            send_data_to_thingspeak(temperature, humidity)
        else:
            # Hiba esetén értesítést kapunk
            print("Sikertelen szenzoradat olvasás. Ellenőrizd a bekötést és a kódot.")
            # Rövid szünet, hogy ne próbálkozzon túl gyorsan újra
            time.sleep(2)

        # Várakozás 10 másodpercet a következő mérés előtt
        time.sleep(10)

except KeyboardInterrupt:
    # Amikor a felhasználó leállítja a programot (Ctrl+C)
    print("\nProgram leállítva a felhasználó által.")
finally:
    # Fontos: A GPIO lábakat mindig tisztítsuk meg a program végén!
    GPIO.cleanup()
    # A gpiozero LED objektumokat is zárjuk le
    blue_led.close()
    red_led.close()
    print("GPIO lábak tisztítva és LED-ek kikapcsolva.")
