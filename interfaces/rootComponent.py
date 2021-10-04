import logging
import tkinter as tk
import interfaces.windowStyle as style
from interfaces.loggingComponent import Logging
from connectors.binanceFutures import BinanceFuturesClient
from interfaces.strategyComponent import StrategyEditor
from interfaces.tradesComponent import TradesWatch
from interfaces.watchlistComponent import WatchList

logger = logging.getLogger()


class Root(tk.Tk):
    def __init__(self, binance: BinanceFuturesClient):
        super().__init__()
        self.title("Trading Bot")
        self.configure(bg=style.BG_COLOR)

        self.binance = binance
        self._leftFrame = tk.Frame(self, bg=style.BG_COLOR)
        self._leftFrame.pack(side=tk.LEFT)

        self._rightFrame = tk.Frame(self, bg=style.BG_COLOR)
        self._rightFrame.pack(side=tk.LEFT)

        self._watchListFrame = WatchList(self.binance.contracts, self._leftFrame, bg=style.BG_COLOR)
        self._watchListFrame.pack(side=tk.TOP)

        self._loggingFrame = Logging(self._leftFrame, bg=style.BG_COLOR)
        self._loggingFrame.pack(side=tk.TOP)

        self._strategyEditor = StrategyEditor(self._rightFrame, bg=style.BG_COLOR)
        self._strategyEditor.pack(side=tk.TOP)

        self._tradesFrame = TradesWatch(self._rightFrame, bg=style.BG_COLOR)
        self._tradesFrame.pack(side=tk.TOP)

        self._updateUI()

    def _updateUI(self):
        for log in self.binance.logs:
            # if not log[1]:
            self._loggingFrame.addLog(log)
            # log["displayed"] = True

        try:
            # Looping through the items of the dict
            # Watching list prices
            for key, value in self._watchListFrame.bodyWidgets["symbol"].items():

                symbol = self._watchListFrame.bodyWidgets["symbol"][key].cget("text")
                exchange = self._watchListFrame.bodyWidgets["exchange"][key].cget("text")

                if exchange == "Binance":
                    if symbol not in self.binance.contracts:
                        continue

                    if symbol not in self.binance.prices:
                        self.binance.getBiAskPrice(self.binance.contracts[symbol])
                        continue

                    precision = self.binance.contracts[symbol].priceDecimals
                    prices = self.binance.prices[symbol]
                else:
                    continue

                if prices["bid"] is not None:
                    priceStr = "{0:.{prec}f}".format(prices["bid"], prec=precision)
                    self._watchListFrame.bodyWidgets["bidVar"][key].set(priceStr)

                if prices["ask"] is not None:
                    priceStr = "{0:.{prec}f}".format(prices["ask"], prec=precision)
                    self._watchListFrame.bodyWidgets["askVar"][key].set(priceStr)
        except RuntimeError as e:
            logger.error("Runtime error in watchlist: %s", e)

        self.after(1200, self._updateUI)
