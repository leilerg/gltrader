import os
import sys

import logging
log = logging.getLogger(__name__)

import yaml
from .bittrex import Bittrex
from .BittrexAPI import BittrexAPI
from .market import Market
from .notification import *
from .fakeapi import FakeAPI
import threading
import traceback
import importlib.util

from pprint import pprint as pp
import json
import builtins
from test.support import requires
from _ast import Or, If

import time
from pip.utils.outdated import SELFCHECK_DATE_FMT

# from idlelib.searchengine import get
# from win32file import FileRenameInfo


class Trader(object):
    #===========================================================================
    # 
    # The object which makes the tick API read calls and dispatches the data to the markets
    # 
    #===========================================================================
    # Raw API data from each tick
    data = None
    # Dict of each market object keyed by abbr of crypto used by bittrex
    markets = {}
    # List of notifications that should be displayed
    notifications = {}
    # Config is false until trader instantiated with config
    config = False
    current_trade = False
    trades_per_tick = 0
    ticknumber = 0
    
    def __init__(self, config=None):
        #=======================================================================
        # sets parameters and parses config dictionary from file
        #=======================================================================
        self.calls = 0
        self.tradelock = threading.Lock()
        self.strategies = []

        #Set the configuration
        self.config = config
        if self.config is not None:
            #create new instance of API wrapper object and set as property of trader object so it can be accessed
            self.api = BittrexAPI(self.config["exchange"]["bittrex"]["key"], self.config["exchange"]["bittrex"]["secret"])
            self.getStrategies()

        #mocked API that can be used for some basic testing of live trades (cannot replace whole API)
        self.fapi = FakeAPI()
        self.bitcoinBalance = 0

        self.markets = {}
        

    def wakeUp(self):
        #=======================================================================
        # Main method for the Trader 
        # 
        # All the trader actions are coordinated here.
        #=======================================================================
        log.debug("Trader awake!")
        
        # API call 
        response = self.getData()
        #If response is successful...
        if response is not None:
            # Get list of markets to monitor
            self.getActiveMarkets(response)
            # Update - Candles
            self.updateMarketCandles(self.config["candles_timeframe"], self.config["candles_singletick"])
            log.debug("Running strategies!")
            # Run the strategies
            self.runStrategies()

        log.info("Total markets monitored: " +str(len(self.markets)))
        log.info("API calls: " + str(self.api.getApiCalls()))
    






    def getActiveMarkets(self, exchangeResponse):
        #=======================================================================
        # Updates or constructs the dictionary of active markets
        # (that is, the dictionary of all the markets that should be monitored
        # based on the min volume config setting)
        #=======================================================================
        # Loop through ALL markets in the response
        for marketSummary in exchangeResponse:
                
            # Update the available BTC balance to the trader
            if marketSummary["Currency"]["Currency"] == "BTC":
                self.bitcoinBalance = marketSummary["Balance"]["Available"]
                log.debug("Bitcoin balance: {:>.8f}".format(self.bitcoinBalance))
                

            # Check - Is the market already being monitored?
            wasMonitored = self._wasMonitored(marketSummary)
            # Check - Monitor the market?
            getMonitored = self._getMonitored(marketSummary, wasMonitored) 
                
            # NEW MARKET TO MONITOR - NOT YET BEING MONITORED  
            if getMonitored and not wasMonitored:
                #Instantiate market
                newMarket = Market(marketSummary, self.config)
                log.debug("New market added: " + newMarket.name)
                # Add to list of mrakets to monitor
                self.markets[newMarket.name] = newMarket
                # And notify GUI
                newMarket.guiNotify("Success", "NOTIFY_NEW_MARKET")

            # EXISTING MARKET - UPDATE DATA
            if wasMonitored and getMonitored:
                log.debug("Existing market: " + marketSummary["Currency"]["Currency"])
                marketName = marketSummary["Currency"]["Currency"]
                self.markets[marketName].updateMarketData(marketSummary)

            # EXISTING MARKET - REMOVE FROM MONITORING
            if not getMonitored and wasMonitored:
                log.debug("Removing market monitoring for market: " + marketSummary["Currency"]["Currency"])
                # Remove from list of markets
                try: 
                    name = marketSummary["Currency"]["Currency"]
                    self.markets[name].guiNotify("Alert", "NOTIFY_REMOVE_MARKET")
                    del self.markets[name]
                except:
                    log.critical("Market (" + marketSummary["Currency"]["Currency"] + ") " +
                                 "removal attempt failed")
                    log.critical(self.markets)


    
    def runStrategies(self):
        #=======================================================================
        # This function executes all the strategies.
        # 
        # Each market is independently evaluated against each strategy.
        #=======================================================================
        # Loop over all strategies
        for strategy in self.strategies:
            # Log/dump the header
            strategy.printLogHeader(strategy)
            # Loop over all markets
            for marketName in self.markets:
                # Instantiate strategy
                strat = strategy(self.markets[marketName], self.config)
                # Execute strategy
                strat.execute()
                
            
        
    def updateMarketCandles(self, timeFrame, tickInterval):
        #=======================================================================
        # This function will update the candles for all markets
        # 
        # :param timeFrame: (Integer)     - What is the time frame for the candles, in hours
        # :param tickInterval: (Integer)  - Time interval of a single tick, in minutes
        #=======================================================================
        if self.markets is not None:
            #===================================================================
            # for marketName in self.markets:
            #     self.markets[marketName].updateCandles(self.api, timeFrame, tickInterval)
            #===================================================================
            threads = []
            for marketName in self.markets:
                t = threading.Thread(target=self.markets[marketName].updateCandles,
                                     args=[self.api, timeFrame, tickInterval])
                threads.append(t)
                try:
                    t.start()
                except Exception as error:
                    # log.critical("Unhandled exception in 'trader.updateMarketCandles()'\n"+
                    #              "Thread failure, Traceback dump: " + traceback.print_tb(err.__traceback__))
                    # DUMP thread stack!
                    log.exception("Unhandled exception in 'trader.updateMarketCandles()'\n" +
                                  "Error: " + str(error))
                
            # Join the threads back up so the code only proceeds once they are all done
            for t in threads:
                t.join()


    def getStrategies(self):
        for strat_name, strat_cfg in self.config["strategies"].items():
            # pp(strat_name)
            # pp(strat_cfg)
            if strat_cfg["run"]:
                spec = importlib.util.spec_from_file_location(strat_name,
                                                              os.path.join(os.environ['STRATEGIES_DIR'],
                                                              strat_cfg["file"]))
                strat_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(strat_mod)
                strat_class = getattr(strat_mod, strat_cfg["classname"])
                self.strategies.append(strat_class)
        #=======================================================================
        # print("\n\n\n")
        # pp("Strategies to run: ")
        # pp(self.strategies)
        #=======================================================================


    def _getMonitored(self, marketSummaryData, marketWasMonitored):
        #=======================================================================
        # 
        # Determines whether market should currently be monitored based on volume as well as response from API
        # 
        # :param marketSummaryData: (List)       - Response from API calls
        # :param notify:(Default=True) (Boolean) - Whether or not to make a notification when 
        #                                          this market's monitoring stops and starts
        #
        # :returns: (Boolean) Whether or not to monitor market (self.getMonitored)
        # 
        #=======================================================================
        #
        # Default - Do not monitor
        _getMonitored = False
        # Check if there is a market
        hasMarket = False
        hasMarket = self._hasMarket(marketSummaryData)
        # Set volume threshold lower bound multiplier
        volLowBoundMulti = .9 # Prevents markets dropping off due to micro vol oscillations
        

        # If there is a market for this currency, check if it needs to be monitored
        if hasMarket:
            #===================================================================
            # GLOBAL CONDITIONS
            #===================================================================
            # Set volume threshold
            volThreshold = self.config["min_volume"]
            # Adjust for existing markets
            if marketWasMonitored:
                volThreshold *= volLowBoundMulti

            # 1 - Tradeing volume above threshold
            if marketSummaryData["BitcoinMarket"]["BaseVolume"] >= volThreshold:
                _getMonitored = True

            # 2 - I just wanna monitor everything
            elif self.config["show_all"]:
                _getMonitored = True

            #===================================================================
            # CURRENCY SPECIFIC CONDITIONS
            #===================================================================
            # Get currency specific condition
            if "currencies" in self.config:
                # Get name of currency
                name = marketSummaryData["Currency"]["Currency"]
                #check if there is a currency specific config
                if name in self.config["currencies"]:
                    # Create currency specific config
                    ccyConfig = self.config["currencies"][name]

                    # 3 - Trading volume above threshold
                    if "min_volume" in ccyConfig:
                        # Set volume threshold for specific currency
                        volThreshold = ccyConfig["min_volume"]
                        # Adjust for exisitng markets
                        if marketWasMonitored:
                            volThreshold *= volLowBoundMulti
                        if marketSummaryData["BitcoinMarket"]["BaseVolume"] >= volThreshold:
                            _getMonitored = True

                    # 4 - Force monitoring override
                    if "monitor" in ccyConfig:
                        if ccyConfig["monitor"] == True:
                            _getMonitored = True
                        elif ccyConfig["monitor"] == False:
                            _getMonitored = False
                    
        return _getMonitored



    def _hasMarket(self, marketSummaryData):
        #=======================================================================
        # Checks to make sure market data exists
        # (only checking for Bitcoin markets at this stage)
        # 
        # :param data: (List) response from API calls
        #=======================================================================
        _hasMarket = False
        if "BitcoinMarket" in marketSummaryData:
            if marketSummaryData["BitcoinMarket"] is not False and \
               marketSummaryData["BitcoinMarket"] is not None and \
               marketSummaryData["BitcoinMarket"]["BaseVolume"] is not None:
                #self.hasMarket = bool(data["BitcoinMarket"])
                _hasMarket = True
        return _hasMarket

    def _wasMonitored(self, testMarketSummaryData):
        _wasMonitored = False            
        # One or more markets have been identified to be monitored
        if self.markets is not None:
            # Loop over all the markets and check if already monitoring the market
            for marketName in self.markets:
                _wasMonitored = _wasMonitored or testMarketSummaryData["Currency"]["Currency"] == marketName
 
        return _wasMonitored

    def getData(self):
        #=======================================================================
        # Makes API call to get data, returns empty if not successful
        #
        # :returns: List[Dict] if succesful, or None
        #=======================================================================
        #pp(self.api.list_bitcoin_markets())
        #get data via get_balances to limit individual calls and make sure data used down the line is synchronous
        response = self.api.get_balances()
        #if API responds
        if response["success"]:
            return response["result"]
        #allow execution to continue with failed tick without errors, but don't actually do anything
        else:
            log.info("Tick missed - " + str(response))
            Alert("Tick missed: " + response.get("message", "Tick failed, no message"))
            return None


    def getNotifications(self):
        """
        :returns: Dictionary[Notification] A dictionary with the notifications
        """
        #keeping notifications run in trader in case it is necessary in the future
        return self.notifications

    def dump(self):
        """
        Return api data from markets --- used for tests
        """
        pp(self.api.get_balances())

    def dumplist(self):
        """
        Return api data from markets --- used for tests
        """
        response = self.api.get_balances()
        return response["result"]


