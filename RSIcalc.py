
def getFirstAvgGain(numSeries, period):
    open = numSeries[0]
    avgGain = 0
    for close in numSeries[1:period+1]:
        change = close - open
        if change > 0:
            avgGain+=change
        open = close
    avgGain/= period
    return avgGain

def getFirstAvgLoss(numSeries, period):
    open = numSeries[0]
    avgLoss = 0
    for close in numSeries[1:period+1]:
        change = close - open
        if change < 0:
            avgLoss-=change
        open = close
    avgLoss/= period
    return avgLoss

def getAvgGain(open, current, avgGain, period):
    change = current - open
    if change > 0:
        avgGain = (avgGain * (period-1) + change) / period
    else:
        avgGain = avgGain * (period-1) / period
    return avgGain

def getAvgLoss(open, current, avgLoss, period):
    change = current - open
    if change < 0:
        avgLoss = (avgLoss * (period-1) - change) / period
    else:
        avgLoss = avgLoss * (period-1) / period
    return avgLoss

def getAvgValues(closePriceList, pos, period):
    if pos > period+1:
        prevAvgGain, prevAvgLoss = getAvgValues(closePriceList, pos-1, period)
        currAvgGain = getAvgGain(closePriceList[pos-2], closePriceList[pos-1], prevAvgGain, period)
        currAvgLoss = getAvgLoss(closePriceList[pos-2], closePriceList[pos-1], prevAvgLoss, period)
    else:
        currAvgGain = getFirstAvgGain(closePriceList[0:period+1], period)
        currAvgLoss = getFirstAvgLoss(closePriceList[0:period+1], period)
    return currAvgGain, currAvgLoss

def getRSI(avgGain, avgLoss):
    RS = avgGain/avgLoss
    RSI = 100 - 100 / (1 + RS)
    return RSI

