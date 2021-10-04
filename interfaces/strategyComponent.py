import tkinter as tk
import typing

from interfaces.windowStyle import *

class StrategyEditor(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._allContracts = ["BTCUSDT"] # Added 1 contract because the * operator it won`t work if the list is empty
        self._allTimeframes = ["1m","5m","15m","30m","1h","4h","1d"]

        self._commandsFrame = tk.Frame(self, bg=BG_COLOR)
        self._commandsFrame.pack(side=tk.TOP)

        self._tableFrame = tk.Frame(self,bg=BG_COLOR)
        self._tableFrame.pack(side=tk.TOP)

        self._addButton = tk.Button(self._commandsFrame,text="Add Strategy", font=GLOBAL_FONT, command=self._addStrategyRow, bg=BG_COLOR_2, fg=FG_COLOR)
        self._addButton.pack(side=tk.TOP)

        self._headers = ["Strategy", "Contract", "Timeframe", "Balance %","TP %", "SL %"]
        self._strategyParameters = dict()
        self._strategyInput = dict()

        self._baseParams = [
            {"codeName": "strategyType", "widget": tk.OptionMenu, "dataType": str, "values": ["Technical", "Breakout"], "width": 10},
            {"codeName": "contract", "widget": tk.OptionMenu, "dataType": str, "values": self._allContracts, "width": 15},
            {"codeName": "timeframe", "widget": tk.OptionMenu, "dataType": str, "values": self._allTimeframes,
             "width": 7},
            {"codeName": "balancePct", "widget": tk.Entry, "dataType": float, "width": 7},
            {"codeName": "takeProfitPct", "widget": tk.Entry, "dataType": float, "width": 7},
            {"codeName": "stopLossPct", "widget": tk.Entry, "dataType": float, "width": 7},
            {"codeName": "parameters", "widget": tk.Button, "dataType": float, "text": "Parameters", "bg": BG_COLOR_2, "command": self._showPopup},
            {"codeName": "activation", "widget": tk.Button, "dataType": float, "text": "OFF", "bg": "darkred", "command": self._switchStrategy},
            {"codeName": "delete", "widget": tk.Button, "dataType": float,  "text": "X", "bg": "darkred", "command": self._deleteRow}
        ]

        self.extraParams = {
            "Technical": [
                {"codeName": "emaFast", "labelName": "MACD Fast Length", "widget": tk.Entry, "dataType": int},
                {"codeName": "emaSlow", "labelName": "MACD Slow Length", "widget": tk.Entry, "dataType": int},
                {"codeName": "emaSignal", "labelName": "MACD Signal Length", "widget": tk.Entry, "dataType": int}
            ],
            "Breakout": [
                {"codeName": "minVolume", "labelName": "Minimum Volume", "widget": tk.Entry, "dataType": float}
            ]
        }

        self.bodyWidgets = dict()

        # Create the headers
        for pos, value in enumerate(self._headers):
            header = tk.Label(self._tableFrame, text=value, bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=pos)

        for h in self._baseParams:
            self.bodyWidgets[h["codeName"]] = dict()
            if h["widget"] == tk.OptionMenu:
                self.bodyWidgets[h["codeName"] + "Var"] = dict()
        self._bodyIndex = 1


    def _addStrategyRow(self):
        bodyIndex = self._bodyIndex

        for col, baseParam in enumerate(self._baseParams):
            codeName = baseParam["codeName"]
            if baseParam["widget"] == tk.OptionMenu:
                self.bodyWidgets[codeName + "Var"][bodyIndex] = tk.StringVar()
                self.bodyWidgets[codeName + "Var"][bodyIndex].set(baseParam["values"][0])
                self.bodyWidgets[codeName][bodyIndex] = tk.OptionMenu(self._tableFrame, self.bodyWidgets[codeName + "Var"][bodyIndex],
                                                                      *baseParam["values"])

                self.bodyWidgets[codeName][bodyIndex].config(width=baseParam["width"])
            elif baseParam["widget"] == tk.Entry:
                self.bodyWidgets[codeName][bodyIndex] = tk.Entry(self._tableFrame, justify=tk.CENTER)
            elif baseParam["widget"] == tk.Button:
                self.bodyWidgets[codeName][bodyIndex] = tk.Button(self._tableFrame, text=baseParam["text"], bg=baseParam["bg"], fg=FG_COLOR, command=lambda frozenCommand=baseParam["command"]:frozenCommand(bodyIndex))
            else:
                continue

            self.bodyWidgets[codeName][bodyIndex].grid(row=bodyIndex,column=col)

        self._strategyParameters[bodyIndex] = dict()

        for strat, params in self._strategyParameters.items():
            for param in params:
                self._strategyParameters[bodyIndex][param["codeName"]] = None

        self._bodyIndex +=1

    def _showPopup(self, bodyIndex: int):
        # getting the coordinates of the button which was clicked
        x = self.bodyWidgets["parameters"][bodyIndex].winfo_rootx()
        y = self.bodyWidgets["parameters"][bodyIndex].winfo_rooty()

        self._popupWindow = tk.Toplevel(self)
        self._popupWindow.wm_title("Parameters")
        self._popupWindow.config(bg=BG_COLOR)
        self._popupWindow.attributes("-topmost","true")

        self._popupWindow.grab_set()

        self._popupWindow.geometry(f"+{x - 80}+{y + 30}")

        strategySelected = self.bodyWidgets["strategyTypeVar"][bodyIndex].get()

        rowNum = 0

        for strategy in self.extraParams[strategySelected]:
            codeName = strategy["codeName"]
            tempLabel = tk.Label(self._popupWindow,bg=BG_COLOR, fg=FG_COLOR, justify=tk.CENTER, text=strategy["labelName"], font=BOLD_FONT)

            tempLabel.grid(row=rowNum, column=0)

            if strategy["widget"] == tk.Entry:
                self._strategyInput[codeName] = tk.Entry(self._popupWindow, bg=BG_COLOR_2, fg=FG_COLOR, justify=tk.CENTER, insertbackground=FG_COLOR)
                if self.strategy[bodyIndex][codeName] is not None:
                    self.strategy[codeName].insert(tk.END, str(self._strategyParameters[bodyIndex][codeName]))
            else:
                continue

            self._strategyInput[codeName].grid(row=rowNum, column=1)
            rowNum += 1

        # Validation button

        validationButton = tk.Button(self._popupWindow,text="Validate", bg=BG_COLOR_2,fg=FG_COLOR, command=lambda: self._validateParameters(bodyIndex))

        validationButton.grid(row=rowNum, column=0, columnspan=2)

    def _validateParameters(self, bodyIndex: int):

        strategySelected = self.bodyWidgets["strategyTypeVar"][bodyIndex].get()
        print(self._strategyParameters)
        for param in self._strategyParameters[strategySelected]:
            codeName = param["codeName"]

            if self._strategyInput[codeName].get() == "":
                self._strategyParameters[bodyIndex][codeName] = None
            else:
                self._strategyParameters[bodyIndex][codeName] = param["dataType"](self._strategyInput[codeName].get())

        self._popupWindow.destroy()


    def _switchStrategy(self,bodyIndex: int):
        return

    def _deleteRow(self, bodyIndex: int):
        for element in self._baseParams:
            self.bodyWidgets[element["codeName"]][bodyIndex].grid_forget()

            del self.bodyWidgets[element["codeName"]][bodyIndex]
        return
