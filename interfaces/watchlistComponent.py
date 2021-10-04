import tkinter as tk
import typing

from models import *
from interfaces.windowStyle import *

class WatchList(tk.Frame):
    def __init__(self, binanceContracts: typing.Dict[str, Contract], *args, **kwargs):
        super(WatchList, self).__init__(*args, **kwargs)

        self.binanceSymbols = list(binanceContracts.keys())

        self._commandsFrame = tk.Frame(self, bg=BG_COLOR)
        self._commandsFrame.pack(side=tk.TOP)

        self._tableFrame = tk.Frame(self,bg=BG_COLOR)
        self._tableFrame.pack(side=tk.TOP)

        self.binanceLabel = tk.Label(self._commandsFrame, text="Binance", bg=BG_COLOR,fg=FG_COLOR, font=BOLD_FONT)
        self.binanceLabel.grid(row=0, column=0)

        self.binanceEntry = tk.Entry(self._commandsFrame, fg=FG_COLOR, justify=tk.CENTER, insertbackground=FG_COLOR, bg=BG_COLOR_2)
        self.binanceEntry.bind("<Return>", self._addBinanceSymbol)
        self.binanceEntry.grid(row=1,column=0)

        self._headers = ["symbol", "exchange", "bid", "ask", "remove"]

        self.bodyWidgets = dict()

        # Create the headers
        for pos, value in enumerate(self._headers):
            header = tk.Label(self._tableFrame, text=value.capitalize() if value != "remove" else "", bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=pos)

        for h in self._headers:
            self.bodyWidgets[h] = dict()
            if h in ["bid", "ask"]:
                self.bodyWidgets[h +"Var"] = dict()

        self._bodyIndex = 1


    def _removeSymbol(self, bodyIndex: int):
        for row in self._headers:
            self.bodyWidgets[row][bodyIndex].grid_forget()
            del self.bodyWidgets[row][bodyIndex]


    def _addBinanceSymbol(self, event):
        # get entry box content
        symbol = event.widget.get()

        if symbol in self.binanceSymbols:
            self._addSymbolToWatchlist(symbol, "Binance")

            # Clear input
            event.widget.delete(0, tk.END)

    def _addSymbolToWatchlist(self, symbol: str, exchange: str):
        body_index = self._bodyIndex

        self.bodyWidgets["symbol"][body_index] = tk.Label(self._tableFrame, text=symbol, bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["symbol"][body_index].grid(row=body_index, column=0)

        self.bodyWidgets["exchange"][body_index] = tk.Label(self._tableFrame, text=exchange, bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["exchange"][body_index].grid(row=body_index, column=1)

        self.bodyWidgets["bidVar"][body_index] = tk.StringVar()
        self.bodyWidgets["bid"][body_index] = tk.Label(self._tableFrame, textvariable=self.bodyWidgets["bidVar"][body_index], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["bid"][body_index].grid(row=body_index, column=2)

        self.bodyWidgets["askVar"][body_index] = tk.StringVar()
        self.bodyWidgets["ask"][body_index] = tk.Label(self._tableFrame, textvariable=self.bodyWidgets["askVar"][body_index], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["ask"][body_index].grid(row=body_index, column=3)

        self.bodyWidgets["remove"][body_index] = tk.Button(self._tableFrame,
                                                       text="X", bg="darkred",
                                                       fg=FG_COLOR, font=GLOBAL_FONT, command=lambda: self._removeSymbol(body_index))
        self.bodyWidgets["remove"][body_index].grid(row=body_index, column=4)

        self._bodyIndex += 1
        return
