from binance.spot import Spot
import sys
import time
import RSIcalc as RSI
import discord
from discord.ext import tasks

RSIPERIOD = 6
MAXLIMIT = 50
CLOSEINDEX = 4
CHANNELID = 1005216984218210306
DISCORDCLIENT = discord.Client()
TOKEN = "Aint"
APIKEY = "No"
SECRETKEY = "Way"

class Tracker:

    def __init__(self, ticker, period, lowerLimit, upperLimit, client):
        self.ticker = ticker
        self.period = period
        self.client = client
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit
        klines = self.client.klines(self.ticker, self.period, limit = MAXLIMIT)
        closePriceList = ExtractClosePriceList(klines)
        self.prevAvgGain, self.prevAvgLoss = RSI.getAvgValues(closePriceList, MAXLIMIT-1, RSIPERIOD)
        self.currentTimeStamp = klines[-1][0]
        self.prevTimeStamp = self.currentTimeStamp

    def getRSI(self):
        klines = self.client.klines(self.ticker, self.period, limit = 2)
        self.currentTimeStamp = klines[-1][0]
        if self.prevTimeStamp != self.currentTimeStamp:
            self.prevTimeStamp = self.currentTimeStamp
            open = float(klines[0][1])
            close = float(klines[0][4])
            self.prevAvgGain = RSI.getAvgGain(open, close, self.prevAvgGain, RSIPERIOD)
            self.prevAvgLoss = RSI.getAvgLoss(open, close, self.prevAvgLoss, RSIPERIOD)
        closePriceList = ExtractClosePriceList(klines)
        open = closePriceList[0]
        current = closePriceList[1]
        self.currentAvgGain = RSI.getAvgGain(open, current, self.prevAvgGain, RSIPERIOD)
        self.currentAvgLoss = RSI.getAvgGain(open, current, self.prevAvgLoss, RSIPERIOD)
        return RSI.getRSI(self.currentAvgGain, self.currentAvgLoss)

def ExtractClosePriceList(klines):
    closePriceList = [item[CLOSEINDEX] for item in klines]
    closePriceList = list(map(float, closePriceList))
    return closePriceList

@tasks.loop(seconds=30)
async def test(objectList):
    channel = DISCORDCLIENT.get_channel(CHANNELID)
    for tracker in objectList:
        myRSI = tracker.getRSI()
        if myRSI < tracker.lowerLimit:
            await channel.send("Oversold levels for %s".format(tracker.ticker))
        if myRSI > tracker.upperLimit:
            await channel.send("Overbought levels for %s".format(tracker.ticker))
        time.sleep(1)

@DISCORDCLIENT.event
async def on_ready():
    client = Spot(key=APIKEY, secret=SECRETKEY)
    sys.setrecursionlimit(1500)
    ticker = "BTCUSDT"

    lowerLimit = 30
    upperLimit = 70

    period = "4h"
    btcusdt4h = Tracker(ticker, period, lowerLimit, upperLimit, client)
    period = "1h"
    btcusdt1h = Tracker(ticker, period, lowerLimit, upperLimit, client)
    period = "15m"
    btcusdt15m = Tracker(ticker, period, lowerLimit, upperLimit, client)
    period = "5m"
    btcusdt5m = Tracker(ticker, period, lowerLimit, upperLimit, client)
    objectList = [btcusdt4h, btcusdt1h, btcusdt15m, btcusdt5m]
    test.start(objectList)

DISCORDCLIENT.run(TOKEN)