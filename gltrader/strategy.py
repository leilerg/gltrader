
import os

import logging
log = logging.getLogger(__name__)


from kivy.app import App

from .action import *
from .notification import *




class Strategy(object):

    # Set default strategy name
    stratName = "Invalid Strategy"
    

    def __init__(self, market, btcBalance, appConfig, tradeAPI, tradelock):
        self.market     = market
        self.btcBalance = btcBalance
        self.tradeAPI   = tradeAPI
        self.tradelock  = tradelock
        self.action = False
        self.config = getStrategyConfigOverrides(appConfig)
        


    # :FIX ME: Execute strategy with available balance, to check if enough money is available
    # A balance class could act as semaphore to ensure thread safety - Pause trade execution until
    # the balance is updated, i.e. a trade executed successfully
    def execute(self):
        # Check that the strategy has a valid name
        if self.stratName == "Invalid Strategy":
            log.critical("Strategy must not use default name - '" + self.stratName
                         + "' - Not executing")
            return None

        # At this point I can proceed with trade exacution
        self.refresh()
        # Default option: DO NOT run the strategy, and check the strategy has a valid name
        if self.config.get("run", False):
            if not self.action:
                if self.tradelock.acquire(False):
                    # Evaluate strategy
                    self.action = self.run()

                    if self.action is not None:
                        self.note = Info("Action: " + str(self.action), self.action)
                        self.notified = True
                        if self.config["do_actions"]:
                            # Trade is executed HERE!!!
                            openOrders = self.action.do()
                            # Reset timestamp for this (market, strategy) pair
                            if self.action.success:
                                # Timestamp market with strategy and time of trade
                                self.market.resetLastTradeTime(self.stratName)
                            self.note.refreshWidget()
                    self.tradelock.release()


    def refresh(self):
        # if self.reset > 0:
        #     self.reset = self.reset - 1
        if self.action:
            if self.action.done:
                self.action = False
                self.notified = False
                self.note = False

                
    def name(self):
        #===============================================
        # :returns: (string) - The name of the strategy
        #===============================================
        return self.stratName


    def getStrategyConfigOverrides(masterConfig):
        #===========================================================================================
        # :returns: (dict) - A configuration dictionary where the global settings have been
        #                    overridden for a specific strategy
        #===========================================================================================
        config = {}
        if not masterConfig.get("strategies", False):
            raise ValueError("Config file must contain entry for this strategy")
            sys.exit("invalid config file")
        for key, value in masterConfig.items():
            if key != "currencies" and key != "strategies":
                config[key] = value
        for key, value in masterConfig["strategies"].get(self.stratName, {}).items():
            config[key] = value
        if masterConfig.get("strategies", False):
            if masterConfig["strategies"].get(self.stratName, False):
                for key, value in self.market.config.get("strategies", {}).items():
                    config[key] = value
        return config
        
        
                
                    
    # # :FIX ME: Execute strategy with available balance, to check if enough money is available
    # def execute(self):
    #     self.refresh()
    #     if self.reset == 0:
    #         # Default option: DO NOT run the strategy
    #         if self.config.get("run", False):
    #             if not self.action:
    #                 #print("Running strategies for " + self.market.name)
    #                 if self.trader.trades_per_tick < self.config["trades_per_tick"]:
    #                     #print("Check - Trade per tick: Pass")
    #                     if self.trader.tradelock.acquire(False):
    #                         # Evaluate strategy
    #                         self.action = self.run()
                            
    #                         if self.action:
    #                             self.reset = self.reset_interval
    #                             self.trader.trades_per_tick = self.trader.trades_per_tick + 1
    #                             self.note = Info("Action: "+str(self.action), self.action)
    #                             self.notified = True
    #                             if self.config["do_actions"]:
    #                                 # Trade is executed HERE!!!
    #                                 self.action.do()
    #                                 # MUST RESET CAN-TRADE FLAG FOR MARKET!!!
    #                                 if self.action.success:
    #                                     self.market.resetLastTradeTime()
    #                                 self.note.refreshWidget()
    #                         self.trader.tradelock.release()



    

