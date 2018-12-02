from gltrader.strategy import Strategy
from gltrader.action import *

class NotifyTick(Strategy):
    name = "notifyTick"


    def run(self):
        """
        Just a test to make sure the strategies and buttons are working

        :returns: (Action) notification
        """
        if self.market.name == "BCC":
            return SendSuccess("Tick")
