
import os

import logging
log = logging.getLogger(__name__)


from kivy.app import App

from .action import *
from .notification import *
from pprint import pprint as pp





class Strategy(object):


    def __init__(self, market, appConfig):
        self.market = market
        self.trader = App.get_running_app().trader
        self.reset = 0
        self.action = False
        self.config = {}
        if not appConfig.get("strategies", False):
            raise ValueError("Config file must contain entry for this strategy")
            sys.exit("invalid config file")
        for key, value in appConfig.items():
            if key != "currencies" and key != "strategies":
                self.config[key] = value
        for key, value in appConfig["strategies"].get(self.name, {}).items():
            self.config[key] = value
        if appConfig.get("strategies", False):
            if appConfig["strategies"].get(self.name, False):
                for key, value in self.market.config.get("strategies", {}).items():
                    self.config[key] = value

        self.reset_interval = self.config["strategy_reset_interval"]




    def execute(self):
        self.refresh()
        if self.reset == 0:
            if self.config.get("run", True):
                if not self.action:
                    #print("Running strategies for " + self.market.name)
                    if self.trader.trades_per_tick < self.config["trades_per_tick"]:
                        #print("Check - Trade per tick: Pass")
                        if self.trader.tradelock.acquire(False):
                            # Evaluate strategy
                            self.action = self.run()
                            
                            if self.action:
                                self.reset = self.reset_interval
                                self.trader.trades_per_tick = self.trader.trades_per_tick + 1
                                self.note = Info("Action: "+str(self.action), self.action)
                                self.notified = True
                                if self.config["do_actions"]:
                                    # Trade is executed HERE!!!
                                    self.action.do()
                                    # MUST RESET CAN-TRADE FLAG FOR MARKET!!!
                                    if self.action.success:
                                        self.market.resetLastTradeTime()
                                    self.note.refreshWidget()
                            self.trader.tradelock.release()


    def refresh(self):
        if self.reset > 0:
            self.reset = self.reset - 1
        if self.action:
            if self.action.done:
                self.action = False
                self.notified = False
                self.note = False

    

