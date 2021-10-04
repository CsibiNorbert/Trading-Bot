import hashlib
import hmac
import json
import logging
import time
import typing
import requests
from urllib.parse import urlencode

import websocket
import threading

from models import *

logger = logging.getLogger()


class BinanceFuturesClient:
    def __init__(self, publicKey: str, secretKey: str, testnet: bool):
        if testnet:
            self._baseUrl = "https://testnet.binancefuture.com/"
            self._wssUrl = "wss://stream.binancefuture.com/ws"
        else:
            self._baseUrl = "https://fapi.binance.com/"
            self._wssUrl = "wss://fstream.binance.com"

        self._publicK = publicKey
        self._secretK = secretKey

        self._channelId = 1

        # Setting the headers
        self._headers = {"X-MBX-APIKEY": self._publicK}

        self.prices = dict()
        self.contracts = self.getContracts()
        self.balances = self.getBalances()

        self._ws = None
        self.logs = []

        # running in parallel
        t = threading.Thread(target=self._startWebsocket)
        t.start()

        logger.info("Binance Futures Client Successfully Initialized.")

    def _addNewLogsBidAndAsk(self, msg: str):
        logger.info("%s", msg)
        self.logs.append({"log": msg, "displayed": False})

    def _generateSignature(self, data: typing.Dict) -> str:
        return hmac.new(self._secretK.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()

    def getContracts(self) -> typing.Dict[str, Contract]:
        exchangeInfo = self._makeRequest("fapi/v1/exchangeInfo", "GET", dict())
        contracts = dict()

        if exchangeInfo is not None:
            for contract_data in exchangeInfo["symbols"]:
                contracts[contract_data["symbol"]] = Contract(contract_data)
        return contracts

    def getHistoricalCandles(self, contract: Contract, interval: str) -> typing.List[Candle]:
        data = dict()

        data["symbol"] = contract.symbol
        data["interval"] = interval
        data["limit"] = 1000

        rawCandles = self._makeRequest("fapi/v1/klines", "GET", data)

        candles = []
        if rawCandles is not None:
            for candleInfo in rawCandles:
                candles.append(Candle(candleInfo))

        return candles

    def getBiAskPrice(self, contract: Contract) -> typing.Dict[str, float]:
        data = dict()
        data["symbol"] = contract.symbol
        orderBookData = self._makeRequest("fapi/v1/ticker/bookTicker", "GET", data)

        if orderBookData is not None:
            if contract.symbol not in self.prices:
                self.prices[contract.symbol] = {"bid": float(orderBookData["bidPrice"]),
                                                "ask": float(orderBookData["askPrice"])}
            else:
                self.prices[contract.symbol]["bid"] = float(orderBookData["bidPrice"])
                self.prices[contract.symbol]["ask"] = float(orderBookData["askPrice"])

            return self.prices[contract.symbol]

    def _makeRequest(self, endpoint: str, httpMethod: str, data: typing.Dict):
        try:
            if httpMethod == "GET":
                response = requests.get(self._baseUrl + endpoint, params=data, headers=self._headers)
            elif httpMethod == "POST":
                response = requests.post(self._baseUrl + endpoint, params=data, headers=self._headers)
            elif httpMethod == "DELETE":
                response = requests.delete(self._baseUrl + endpoint, params=data, headers=self._headers)
            else:
                raise ValueError()
        except Exception as e:
            logger.error("Connection error for method: %s request to %s: s%", httpMethod, endpoint, e)
            return None

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making %s request to %s: %s (%s error code)", httpMethod, endpoint,
                         response.json(), response.status_code)

        return None

    def getBalances(self) -> typing.Dict[str, Balance]:
        data = dict()

        # converted to ms, we want the long number int
        data["timestamp"] = int(time.time() * 1000)
        data["signature"] = self._generateSignature(data)

        balances = dict()

        accountData = self._makeRequest("fapi/v1/account", "GET", data)

        if accountData is not None:
            for asset in accountData["assets"]:
                noMoney = asset["walletBalance"].startswith('0.0000')
                if not noMoney:
                    balances[asset["asset"]] = Balance(asset)
        return balances

    def placeOrder(self, contract: Contract, side: str, quantity: float, orderType: str, price=None,
                   timeInForce=None) -> OrderStatus:
        data = dict()

        data["timestamp"] = int(time.time() * 1000)
        data["symbol"] = contract.symbol
        data["side"] = side
        data["quantity"] = round(round(quantity / contract.lotSize) * contract.lotSize, 8)
        data["type"] = orderType

        if price is not None:
            data["price"] = round(round(price / contract.tickSize) * contract.tickSize, 8)
        if timeInForce is not None:
            data["timeInForce"] = timeInForce

        data["signature"] = self._generateSignature(data)

        orderStatus = self._makeRequest("fapi/v1/order", "POST", data)

        if orderStatus is not None:
            # Replacing the dict to OrderStatus obj
            orderStatus = OrderStatus(orderStatus)
        return orderStatus

    def cancelOrder(self, contract: Contract, orderId: int) -> OrderStatus:
        data = dict()

        data["timestamp"] = int(time.time() * 1000)
        data["symbol"] = contract.symbol
        data["orderId"] = orderId
        data["signature"] = self._generateSignature(data)

        orderCancelled = self._makeRequest("fapi/v1/order", "DELETE", data)
        if orderCancelled is not None:
            # Replacing the dict to OrderStatus obj
            orderCancelled = OrderStatus(orderCancelled)
        return orderCancelled

    def getOrderStatus(self, contract: Contract, orderId: int) -> OrderStatus:
        data = dict()  # dictionary of params
        data["timestamp"] = int(time.time() * 1000)
        data["symbol"] = contract.symbol

        if orderId is not None:
            data["orderId"] = orderId

        data["signature"] = self._generateSignature(data)

        orderStatus = self._makeRequest("fapi/v1/order", "GET", data)

        if orderStatus is not None:
            # Replacing the dict to OrderStatus obj
            orderStatus = OrderStatus(orderStatus)
        return orderStatus

    def _startWebsocket(self):
        self.ws = websocket.WebSocketApp(self._wssUrl,
                                         on_open=self._onOpen,
                                         on_close=self._onClose,
                                         on_error=self._onError,
                                         on_message=self._onMessage)

        # If the connection drops, it will re-connect
        while True:
            try:
                # infinite loop
                # This needs to run in a thread/task
                self.ws.run_forever()
            except Exception as e:
                logger.error("Binance error in run_forever method: %s", e)
            # Wait 2 seconds before runs the run_forever method again
            time.sleep(2)

    def _onOpen(self, ws):
        logger.info("Binance connection has been established")

        self.subscribeChannel(list(self.contracts.values()), "bookTicker")

    def _onClose(self, ws):
        logger.warning("Binance connection has been closed")

    def _onError(self, ws, msg: str):
        logger.error("An error occured during Binance connection {%s}", msg)

    def _onMessage(self, ws, msg: str):
        data = json.loads(msg)

        if "e" in data:
            if data["e"] == "bookTicker":
                symbol = data["s"]
                if symbol not in self.prices:
                    self.prices[symbol] = {"bid": float(data["b"]),
                                           "ask": float(data["a"])}
                else:
                    self.prices[symbol]["bid"] = float(data["b"])
                    self.prices[symbol]["ask"] = float(data["a"])

                if symbol == "LTCUSDT":
                    self.logs.append(symbol + " " + str(self.prices[symbol]["bid"]) + " / " + str(self.prices[symbol]["ask"]))

    def subscribeChannel(self, contracts: typing.List[Contract], channel: str):
        data = dict()
        data["method"] = "SUBSCRIBE"
        # list of channels we subscribe to
        data["params"] = []

        for contract in contracts:
            data["params"].append(contract.symbol.lower() + "@" + channel)
        data["id"] = self._channelId

        # Convert dictionary to json string
        jsonData = json.dumps(data)
        try:
            self.ws.send(jsonData)
        except Exception as e:
            logger.error("Websocket error while subscribing to %s %s updates: %s", len(contracts), channel, e)

        # This needs to be different for every channel
        self._channelId += 1
