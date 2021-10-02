import tkinter as tk
from datetime import datetime
from interfaces.windowStyle import *


# Display messages to the user
class Logging(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loggingText = tk.Text(self, height=10, width=16, state=tk.DISABLED, bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT) # Text disabled
        self.loggingText.pack(side=tk.TOP) # place widget in the frame

    def addLog(self, msg: str):
        self.loggingText.configure(state=tk.NORMAL)
        self.loggingText.insert("1.0", datetime.utcnow().strftime("%a %H:%M:%S :: ") + msg + "\n") # 1.0 means that the text will be added at the beginning
        self.loggingText.configure(state=tk.DISABLED)



