class Balance:
    def __init__(self, info):
        # Creating instance of each key we get from json
        self.initialMargin = float(info["initialMargin"])
        self.maintenanceMargin = float(info["maintMargin"])
        self.marginBalance = float(info["marginBalance"])
        self.walletBalance = float(info["walletBalance"])
        self.unrealizedPnL = float(info["unrealizedProfit"])


class Candle:
    def __init__(self, candleInfo):
        self.timestamp = candleInfo[0]
        self.open = float(candleInfo[1])
        self.high = float(candleInfo[2])
        self.close = float(candleInfo[3])
        self.low = float(candleInfo[4])
        self.volume = float(candleInfo[5])


class Contract:
    def __init__(self, contractInfo):
        self.symbol = contractInfo["symbol"]
        self.baseAsset = contractInfo["baseAsset"]
        self.quoteAsset = contractInfo["quoteAsset"]
        self.priceDecimals = contractInfo["pricePrecision"]
        self.quantityDecimals = contractInfo["quantityPrecision"]
        self.tickSize = 1 / pow(10, contractInfo["pricePrecision"])
        self.lotSize = 1 / pow(10, contractInfo["quantityPrecision"])

# for Bitmex ( round the price to the right tick size )
def tickToDecimals(tickSize: float) -> int:
    tickSizeStr = "{0:.8f}".format(tickSize)
    while tickSizeStr[-1] == "0":
        # removing extra 0s
        tickSizeStr = tickSizeStr[:-1]

    splitTick = tickSizeStr.split(".")
    if len(splitTick) > 1:
        return len(splitTick[1])
    else:
        return 0


class OrderStatus:
    def __init__(self, orderInfo):
        self.orderId = orderInfo["orderId"]
        self.status = orderInfo["status"]
        self.avgPrice = float(orderInfo["avgPrice"])
