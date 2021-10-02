import tkinter as tk
import interfaces.windowStyle as style
from interfaces.loggingComponent import Logging
from connectors.binanceFutures import BinanceFuturesClient


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

        self._loggingFrame = Logging(self._leftFrame, bg=style.BG_COLOR)
        self._loggingFrame.pack(side=tk.TOP)
        self._updateUI()

    def _updateUI(self):
        someVar = 0
        for log in self.binance.logs:
            if not log["displayed"]:
                self._loggingFrame.addLog(log["log"])
                log["displayed"] = True
        self.after(1200, self._updateUI)
