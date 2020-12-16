import json
import time
from inputimeout import inputimeout, TimeoutOccurred

# NB! sisesta käsureal pip install inputimeout
# soojuspump on vaikimisi sisselülitatud.
# Raspberry puhul tähendab see et, konkreetse soojuspumba tööd
# juhtiva pin-i tase on "1":
deviceOn = True

try:
    fileName = inputimeout('Sisesta andmefaili nimi (vaikimisi maindata.txt): ', timeout=10)
except TimeoutOccurred:
    print('valisin vaikimisi andmefailiks maindata.txt')
    fileName = 'maindata.txt'

print("Alustame tööd. Kui terminalis on True, on seade sisse lülitatud, kui False, siis välja lülitatud")

# Timeri ploki algus:
while True:
    # Mida teha siis, kui faili ei ole:
    try:
        with open(fileName, 'r') as filehandle:
            mainData = json.load(filehandle)
            filehandle.close()
    except IOError:
        print('file not found')
        print('Raspberry puhul anname siin ühele väljundile pinge peale, et LED alarmeeriks')

    # kontrollime, kas seade peab olema sisse- või väljalülitatud
    # antud juhul on soojuspump top3 elektrihinnaga tundidel väljalülitatud
    if mainData[0].get('top_3') is False:
        deviceOn = False
    else:
        deviceOn = True
    # Kontrolliks prindime terminali, mis on hetke seis:
    print(deviceOn)
    # kontrollime olukorda uuesti 5 min (300sec) pärast
    # programmi testimiseks kasuta näiteks 3 sec: time.sleep(3)
    time.sleep(3)

