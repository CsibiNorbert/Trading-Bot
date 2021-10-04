import tkinter as tk
import typing

from interfaces.windowStyle import *


class TradesWatch(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(TradesWatch, self).__init__(*args, **kwargs)

        self._headers = ["time", "symbol", "exchange", "strategy", "side", "quantity",
                         "status", "pnl"]

        self._tableFrame = tk.Frame(self,bg=BG_COLOR)
        self._tableFrame.pack(side=tk.TOP)

        # reference labels/widgets that are on each row
        self.bodyWidgets = dict()

        # Create the headers
        for pos, value in enumerate(self._headers):
            header = tk.Label(self._tableFrame, text=value.capitalize(), bg=BG_COLOR,
                              fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=pos)

        # variable parts
        for h in self._headers:
            self.bodyWidgets[h] = dict()
            if h in ["status", "pnl"]:
                self.bodyWidgets[h + "Var"] = dict()

        self._bodyIndex = 1


    def addTrade(self, data: typing.Dict):
        bodyIndex = self._bodyIndex
        tradeId = data["time"] # used as ID in  the body widgets dict

        self.bodyWidgets["time"][tradeId] = tk.Label(self._tableFrame, text=data["time"], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["time"][tradeId].grid(row=bodyIndex, column=0)

        self.bodyWidgets["symbol"][tradeId] = tk.Label(self._tableFrame, text=data["symbol"], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["symbol"][tradeId].grid(row=bodyIndex, column=1)

        self.bodyWidgets["exchange"][tradeId] = tk.Label(self._tableFrame, text=data["exchange"], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["exchange"][tradeId].grid(row=bodyIndex, column=2)

        self.bodyWidgets["strategy"][tradeId] = tk.Label(self._tableFrame, text=data["strategy"], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["strategy"][tradeId].grid(row=bodyIndex, column=3)

        self.bodyWidgets["side"][tradeId] = tk.Label(self._tableFrame, text=data["side"], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["side"][tradeId].grid(row=bodyIndex, column=4)

        self.bodyWidgets["quantity"][tradeId] = tk.Label(self._tableFrame, text=data["quantity"], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["quantity"][tradeId].grid(row=bodyIndex, column=5)

        self.bodyWidgets["statusVar"][tradeId] = tk.StringVar()
        self.bodyWidgets["status"][tradeId] = tk.Label(self._tableFrame, textvariable=self.bodyWidgets["statusVar"][tradeId], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["status"][tradeId].grid(row=bodyIndex, column=6)

        self.bodyWidgets["pnlVar"][tradeId] = tk.StringVar()
        self.bodyWidgets["pnl"][tradeId] = tk.Label(self._tableFrame, textvariable=self.bodyWidgets["pnlVar"][tradeId] , bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.bodyWidgets["pnl"][tradeId].grid(row=bodyIndex, column=7)

        self._bodyIndex += 1