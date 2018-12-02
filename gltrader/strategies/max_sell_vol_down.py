from gltrader.strategy import Strategy
from gltrader.action import *

class MaxSellIfVolumeDown(Strategy):
    name = "maxSellIfVolDown"


    def run(self):
        """
        Executes a "MaxSell" action if the 24 hr trailing volume change reaches a certain threshold

        :returns: (Action) The MinTradeUp Action, which executes and returns a market sell for the maximum amount when its "do" method is called
        """
        pass
