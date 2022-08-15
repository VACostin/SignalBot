from pytesseract import pytesseract
import pyautogui
import cv2
import re
import datetime
import time
import discord
from discord.ext import tasks

CHANNELID4H = 1007081273438781570
CHANNELID1H = 1007081287133179976
CHANNELID15M = 1007081299531530270
CHANNELID5M = 1007081310193463326
DISCORDCLIENT = discord.Client()
TOKEN = ''
PATH = r'C:\Users\Costin\Desktop\discordBot\muie.png'

class Tracker:
    def __init__(self, upperLimit, lowerLimit):
        self.currentRSI = 0
        self.timeInMinutes = -1
        self.marketState = 1 # 0 - oversold, 1 - normal, 2 - overbought
        self.upperLimit = upperLimit
        self.lowerLimit = lowerLimit
        self.alreadyNotified = False
    def checkRSI(self):
        if self.currentRSI > self.upperLimit:
            self.marketState = 2
            self.alreadyNotified = True
        elif self.currentRSI < self.lowerLimit:
            self.marketState = 0
            self.alreadyNotified = True
        else:
            self.marketState = 1

#set PYTHONPATH=%PYTHONPATH%;c:\users\costin\appdata\local\programs\python\python37-32\lib\site-packages
#export PYTHONPATH="${PYTHONPATH}:c:\users\costin\appdata\local\programs\python\python37-32\lib\site-packages"
def doImageProcessingMagic():
    buggyShit = True
    while (buggyShit):
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(PATH)
        path_to_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.tesseract_cmd = path_to_tesseract
        image = cv2.imread(PATH,0)
        thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        result = 255 - thresh
        text = pytesseract.image_to_string(result, lang='eng',config='--psm 6')
        RSI6 = "RSI\(6\)"
        dataPosition = [_.start() for _ in re.finditer(RSI6, text)]
        if len(dataPosition) == 4:
            rsiList = []
            buggyShit = False
            for i in range(4):
                startPos = dataPosition[i] + 7
                endPos = dataPosition[i] + 12
                try:
                    RSIval = float(text[startPos:endPos])
                    rsiList.append(RSIval)
                except:
                    buggyShit = True
                    pass
        else:
            rsiList = []
            for i in range(len(dataPosition)):
                startPos = dataPosition[i] + 7
                endPos = dataPosition[i] + 12
                try:
                    RSIval = float(text[startPos:endPos])
                    rsiList.append(RSIval)
                except:
                    buggyShit = True
                    pass
    return rsiList


@tasks.loop(seconds=5)
async def test(trackerList):
    rsiList = doImageProcessingMagic()
    tracker4h = trackerList[0]
    tracker4h.currentRSI = rsiList[0]
    tracker1h = trackerList[1]
    tracker1h.currentRSI = rsiList[1]
    tracker15m = trackerList[2]
    tracker15m.currentRSI = rsiList[2]
    tracker5m = trackerList[3]
    tracker5m.currentRSI = rsiList[3]

    now = datetime.datetime.now()
    offset = 60 #minutes
    minutes = now.hour*60 + now.minute + offset

    #4 hours
    if minutes%240 == 0 and tracker4h.timeInMinutes != minutes:
        tracker4h.timeInMinutes = minutes
        tracker4h.alreadyNotified = False
    if not tracker4h.alreadyNotified:
        tracker4h.checkRSI()
        channel = DISCORDCLIENT.get_channel(CHANNELID4H)
        if tracker4h.marketState == 2:
            await channel.send("Overbought on 4h")
        elif tracker4h.marketState == 0:
            await channel.send("Oversold on 4h")

    #1 hour

    if minutes%60 == 0 and tracker1h.timeInMinutes != minutes:
        tracker1h.timeInMinutes = minutes
        tracker1h.alreadyNotified = False
    if not tracker1h.alreadyNotified:
        tracker1h.checkRSI()
        channel = DISCORDCLIENT.get_channel(CHANNELID1H)
        if tracker1h.marketState == 2:
            await channel.send("Overbought on 1h")
        elif tracker1h.marketState == 0:
            await channel.send("Oversold on 1h")

    #15 minutes

    if minutes%15 == 0 and tracker15m.timeInMinutes != minutes:
        tracker15m.timeInMinutes = minutes
        tracker15m.alreadyNotified = False
    if not tracker15m.alreadyNotified:
        tracker15m.checkRSI()
        channel = DISCORDCLIENT.get_channel(CHANNELID15M)
        if tracker15m.marketState == 2:
            await channel.send("Overbought on 15m")
        elif tracker15m.marketState == 0:
            await channel.send("Oversold on 15m")

    #5 minutes
    if minutes%5 == 0 and tracker5m.timeInMinutes != minutes:
        tracker5m.timeInMinutes = minutes
        tracker5m.alreadyNotified = False
    if not tracker5m.alreadyNotified:
        tracker5m.checkRSI()
        channel = DISCORDCLIENT.get_channel(CHANNELID5M)
        if tracker5m.marketState == 2:
            await channel.send("Overbought on 5m")
        elif tracker5m.marketState == 0:
            await channel.send("Oversold on 5m")

@DISCORDCLIENT.event
async def on_ready():
    trackerList = []
    for i in range (0, 4):
        tracker = Tracker(70, 30)
        trackerList.append(tracker)
    test.start(trackerList)

DISCORDCLIENT.run(TOKEN)