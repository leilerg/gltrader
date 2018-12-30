
import os

import logging
log = logging.getLogger(__name__)


from kivy.app import App

from .action import *
from .notification import *




class Strategy(object):

    # Set default strategy name
    strName = "Invalid Strategy"
    

    def __init__(self, market, appConfig):
        self.market = market
        self.trader = App.get_running_app().trader
        self.action = False
        self.config = {}
        if not appConfig.get("strategies", False):
            raise ValueError("Config file must contain entry for this strategy")
            sys.exit("invalid config file")
        for key, value in appConfig.items():
            if key != "currencies" and key != "strategies":
                self.config[key] = value
        for key, value in appConfig["strategies"].get(self.strName, {}).items():
            self.config[key] = value
        if appConfig.get("strategies", False):
            if appConfig["strategies"].get(self.strName, False):
                for key, value in self.market.config.get("strategies", {}).items():
                    self.config[key] = value


        # NOT NEEDED... EVERY STRATEGIES SHOULD SPECIFY THE RESET INTERVAL INDEPENDENTLY
        # Changes: config.yaml + specific config file
        self.reset_interval = self.config["strategy_reset_interval"]




    # :FIX ME: Two objectives to implement
    # One - When a trade gets executed, must flag the market that the trade has happened
    # Two - At the same time, must flag that it has been executed against a specific strategy. In
    # other words, when querying for the last trade in a given market, this should also tell me what
    # is the strategy it has been executed against.
    # Could be implemented by introducing a "lastTradeTimestamp" dictionary in the market class -
    # which would return the last trade timestamp for the specific strategy, but some default if the
    # strategy has not been executed so far. Updating the timestapm would then need to happen in the
    # specific strategy and not here, as is the case now.
    #
    # The above suggestion does not seem to work as every strategy gets executed below only, and
    # hence it's only here that the app is aware if the strategy gets eecuted or not. That's why the
    # refresh happens here.
    #
    # I could use a strategy name! Then I could reset the market from below using the actual
    # strategy being executed




    # :FIX ME: Execute strategy with available balance, to check if enough money is available
    # A balance class could act as semaphore to ensure thread safety - Pause trade execution until
    # the balance is updated, i.e. a trade executed successfully
    def execute(self):
        # Check that the strategy has a valid name
        if self.strName == "Invalid Strategy":
            log.critical("Strategy must not use default name - '" + self.strName
                         + "' - Not executing")
            return None

        # At this point I can proceed with trade exacution
        self.refresh()
        # Default option: DO NOT run the strategy, and check the strategy has a valid name
        if self.config.get("run", False):
            if not self.action:
                #print("Check - Trade per tick: Pass")
                if self.trader.tradelock.acquire(False):
                    # Evaluate strategy
                    self.action = self.run()
                        
                    if self.action:
                        self.trader.trades_per_tick = self.trader.trades_per_tick + 1
                        self.note = Info("Action: "+str(self.action), self.action)
                        self.notified = True
                        if self.config["do_actions"]:
                            # Trade is executed HERE!!!
                            self.action.do()
                            # Reset timestamp for this (market, strategy) pair
                            if self.action.success:
                                self.market.resetLastTradeTime(self.strName)
                            self.note.refreshWidget()
                    self.trader.tradelock.release()


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
        return self.strName

                
                    
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



    

