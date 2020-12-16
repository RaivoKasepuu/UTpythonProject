# Projekt Raivo Kasepuu, matrikkel B710710, MTAT 03 256

""""
ÜLESANNE:

Projekti idee (tähtaeg 16. nov, max 2 punkti)
Ülesande täpse püstituse teeb üliõpilane ise. Temaatika peab teile endale huvi pakkuma.

Programm peab vastama järgmistele nõuetele.

Peab olema enda tehtud
Orienteeruv töömaht lahendamisel 8 tundi. (Ajakulu esitada eraldi ligikaudse aruandena.). Kui teete programmi kahekesi,
siis kummalgi 8 tundi
Programm peab töötlema andmeid
Andmed võivad olla pärit veebist (stat.ee vm) või enda omad
Andmed tuleb lugeda failist (nt csv)
Programm peab midagi küsima kasutajalt (kasvõi failinime)
Võib eeldada, et kasutaja sisestab sobivate andmetega faili nime
Programm peab andmete põhjal midagi mõistlikku arvutama ja tulemuse ekraanil esitama.
Järgmistest nõuetest võib jätta kaks täitmata
graafiline väljund (diagramm vms)
filtreeritud andmete teise faili kirjutamine
kasutaja valiku põhjal arvutuste tegemine
iseseisva (ilma Pythonita käivituva) programmi tegemine

"""

import time
import datetime
import json
import requests
from os import path
from requests.exceptions import ConnectionError
from inputimeout import inputimeout, TimeoutOccurred

def getDateTimeNow():
    # käesoleva hetke inimkeeli loetava kuupäeva ja kellaaja leidmine
    return datetime.datetime.fromtimestamp(time.time()).isoformat()


def getHumanDateTime(timestamp):
    # inimkeeli loetava kuupäeva ja kellaaja leidmine etteantud timestamp-ist
    return datetime.datetime.fromtimestamp(timestamp).isoformat()


def getDateForTomorrow():
    # homse kuupäeva leidmine
    return datetime.datetime.fromtimestamp(time.time() + 24 * 3600).isoformat().split("T")[0]


def getDateForYesterday():
    # eilse kuupäeva leidmine
    return datetime.datetime.fromtimestamp(time.time() - 24 * 3600).isoformat().split("T")[0]


def getDateForToday():
    # tänase kuupäeva leidmine
    return datetime.datetime.fromtimestamp(time.time()).isoformat().split("T")[0]


def getTimestampNow():
    # hetke timestampi leidmine
    return int(time.time())

def makeEleringUrl():
    # genereerib Eleringi turuhindade teenuse küsimiseks url-i
    # Näiteks https://dashboard.elering.ee/api/nps/price?end=2020-12-01%2021%3A00&start=2020-11-30%2022%3A00
    # annab meile jsoni Eleringi hindadega 1.12.2020 -ks
    start = "start=" + str(getDateForYesterday()) + "%2022%3A00"
    end = "end=" + str(getDateForTomorrow()) + "%2021%3A00"
    return "https://dashboard.elering.ee/api/nps/price?" + end + "&" + start


def getEleringEePrices(url, market):
    while True:
        try:
            result = requests.get(url).json()["data"][market]
            if isinstance(result, list):
                return result
        except ConnectionError as e:
            # prindime erro9ri terminalile
            print(e)
            # ootame 10 sekundit ja proovime uuesti kogy try blokki
            time.sleep(10)


def addDateAndHourToPriceData(priceData):
    for i in range(len(priceData)):
        # lisame priceData sõnastikule kuupäeva:
        priceData[i]['date'] = str(getHumanDateTime(priceData[i].get('timestamp')).split("T")[0])
        # lisame pricedata sõnastikule kellaaja tunnid integerina:
        priceData[i]['hour'] = int(str(getHumanDateTime(priceData[i].get('timestamp')).split("T")[1].split(":")[0]))
    return priceData


def addTopThreeHours(priceData):
    # Lisame priceData tänase päeva sõnastikele lisaväljad top_1 .. top_3
    # markeerides sõnastikke vastavalt top3 hindadele
    topPriceOne = 0
    maxFirstHour = 0
    topPriceTwo = 0
    maxSecondHour = 0
    topPriceThree = 0
    maxThirdHour = 0
    for i in range(len(priceData)):
        if priceData[i].get('price') > topPriceOne and priceData[i].get('date') == getDateForToday():
            topPriceThree = topPriceTwo
            maxThirdHour = maxSecondHour
            topPriceTwo = topPriceOne
            maxSecondHour = maxFirstHour
            maxFirstHour = priceData[i].get('hour')
            topPriceOne = priceData[i].get('price')

    for i in range(len(priceData)):
        if priceData[i].get('hour') == maxFirstHour:
            priceData[i]['top_1'] = False
            priceData[i]['top_2'] = False
            priceData[i]['top_3'] = False
        elif priceData[i].get('hour') == maxSecondHour:
            priceData[i]['top_1'] = False
            priceData[i]['top_2'] = False
            priceData[i]['top_3'] = True
        elif priceData[i].get('hour') == maxThirdHour:
            priceData[i]['top_1'] = False
            priceData[i]['top_2'] = False
            priceData[i]['top_3'] = True
        else:
            priceData[i]['top_1'] = True
            priceData[i]['top_2'] = True
            priceData[i]['top_3'] = True
    return priceData


def fileCreationIfNeeded(fileName):
    if path.exists(fileName) is False:
        emptyData = [{"timestamp": 1}]
        with open(fileName, 'w') as filehandle:
            json.dump(emptyData, filehandle)
        filehandle.close()


# Määrame failinime, kus hoiame oma andmeid:
try:
    fileName = inputimeout('Sisesta andmefaili nimi (vaikimisi maindata.txt): ', timeout=10)
except TimeoutOccurred:
    print('valisin vaikimisi andmefailiks maindata.txt')
    fileName = 'maindata.txt'

# Kui selline fail puudub, siis tekitame selle koos triviaalsete algandmetega:
fileCreationIfNeeded(fileName)

# Loeme faili sisu json-i:
with open(fileName, 'r') as filehandle:
    mainData = json.load(filehandle)
    filehandle.close()

# Timeri bloki algus:
while True:
    # küsime viimaseid hindu Eleringi API abil
    url = makeEleringUrl()
    market = "ee"
    priceData = getEleringEePrices(url, market)
    # arvutame ja lisame json-ile kuupäeva ja tunni
    addDateAndHourToPriceData(priceData)
    # markeerime top3 hindadega sõnastikud json-is
    addTopThreeHours(priceData)
    # uuendame mainData väärtusi:
    for i in range(len(priceData)):
        if priceData[i].get('timestamp') > mainData[-1].get('timestamp'):
            mainData.append(priceData[i])
    # Kustutame üle 1h (3600 sec) vanad sõnastikud:
    while mainData[0].get('timestamp') < (getTimestampNow() - 3600):
        mainData.pop(0)
    # Prindime mainData terminalile:
    print(mainData)
    # Kirjutame andmete faili üle uute andmetega
    with open(fileName, 'w') as filehandle:
        json.dump(mainData, filehandle)
        filehandle.close()
    # kordame rutiini teatud aja jooksul sekundites.
    # Antud juhul 1h (3600sec). Testimiseks sobib näiteks 5 sekundit: time.sleep(5)
    time.sleep(5)


