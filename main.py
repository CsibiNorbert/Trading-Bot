import tkinter as tk
import logging as log
from pprint import pprint
from interfaces.rootComponent import Root
from connectors.binanceFutures import BinanceFuturesClient

# Setting logger
logger = log.getLogger()
logger.setLevel(log.INFO)
logger.setLevel(log.DEBUG)

stream_handler = log.StreamHandler()
formatter = log.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(log.INFO)


# File handler
file_handler = log.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(log.DEBUG) # debug to file

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# This prevents to be executed if by mistake has ben imported to another module
if __name__ == '__main__':



    binance = BinanceFuturesClient("69629170dd42d7cc25101bfaa631909a50f9fb4b99758171c6d337ebfc2f13b0",
                                   "27d42554cf74747ed2f6358479b6fdf1e2cbefde701c572bef63b251fa1bf75b", True)
    # Creating a tk interface (app)
    root = Root(binance)
    root.mainloop()

