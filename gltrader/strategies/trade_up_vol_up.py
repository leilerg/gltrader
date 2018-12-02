from gltrader.strategy import Strategy
from gltrader.action import *

import builtins



class TradeUpIfVolumeUp(Strategy):
    #===========================================================================
    # Executes a "TradeUp" action if the 24 hr trailing volume change reaches a certain threshold
    # 
    # :returns: (Action) The MinTradeUp Action, 
    # which executes 2 trades and returns a tuple (Order1, Order2) when its "do" method is called
    #===========================================================================
    name = "TradeUpIfVolumeUp"

    def run(self):
        avgChange = self.market.data.avgVolChange
        
        #Check if I should run the strategy
        ExecuteTrade = False
        if self.market.data.candles.volumeLastHour > 10*self.market.data.candles.volumePrevDayHrAverage:
            ExecuteTrade = True
            
        
        if ExecuteTrade:
            print()
            print("WEEEEEE.... TRADE should be EXECUTED!!!")
            print("Market: "+ self.market.name)
            print("Average 24h volume: " + str(self.market.data.candles.volumePrevDayHrAverage))
            print("Last hour volume: " + str(self.market.data.candles.volumeLastHour))
            print()


        # if self.market.name == "ETH":
            # pp(avgChange)
            # pp(self.market.config["volume_change_max_threshold"])




        #=======================================================================
        # if  avgChange > self.config["volume_change_max_threshold"]:
        #     return MinTradeUp(self.market)
        #=======================================================================
