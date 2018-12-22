import os
import json

import logging
from threading import currentThread
log = logging.getLogger(__name__)

from kivy.app import App

from .market_data import MarketData
from .notification import *
from .action import Action
from .candlesticks import CandleSticks

from builtins import int
# from idlelib.debugger_r import gui_adap_oid

import datetime



TICKINTERVAL_ONEMIN = 'oneMin'
TICKINTERVAL_FIVEMIN = 'fiveMin'
TICKINTERVAL_HOUR = 'hour'
TICKINTERVAL_THIRTYMIN = 'thirtyMin'
TICKINTERVAL_DAY = 'Day'


class Market(object):
    #===========================================================================
    # This class accepts the data from the Trader object at each tick and processes 
    # it into the various objects which generate orders and actions
    #===========================================================================


    def __init__(self, marketSummaryData, appConfig):
        #=======================================================================
        # Sets initial parameters, calls getConfig to parse config file
        # 
        # :param name: (String) The minimal abbreviation which is given by Bittrex for the market
        # :param data: (List) The initial data passed in by the trader during the initializing API call
        # :param appConfig: (dict) The configuration dictionary, which contains market specific configuration 
        #=======================================================================
        #
        #
        # Set the currency name
        self.name = marketSummaryData["Currency"]["Currency"]
        # Set default market short name
        self.abbr = marketSummaryData["BitcoinMarket"]["MarketName"]
        # Get configuration, with overrides for this market 
        self.config = self.getConfig(appConfig)
        # Instantiate market data object
        self.marketData = MarketData(marketSummaryData)
        # Set candles object to none
        self.candles = None
        # Initialize trade time at 2000-01-01, 00:00
        self.lastTradeTimestamp = datetime.datetime(2000, 1, 1, 0, 0, 0)
        # Market initialization timestamp
        self.initializeTimestamp = datetime.datetime.now()
        
        
        # :FIX ME: Used in notification.py where it calls market.checkUpToDate to update the GUI
        # Leaving for now, but should be removed...
        self.isMonitored = True




    def __repr__(self):
        return "<mkt: "+self.name+" object at "+hex(id(self))+">"
    def __str__(self):
        return "<mkt: "+self.name+" object at "+hex(id(self))+">"
    def __unicode__(self):
        return "<"+self.name+":: mkt object at "+hex(id(self))+">"



    def resetLastTradeTime(self):
        #=======================================================================
        # Resets the time of the last trade
        # 
        # returns: N/A
        #=======================================================================
        # print("\nResetting last Trade!!!")
        self.lastTradeTimestamp = datetime.datetime.now()

    def lastTradeTime(self):
        #=======================================================================
        # :returns: Timestamp - The last time at which a trade occurred
        #=======================================================================
        return self.lastTradeTimestamp

    def initTimestamp(self):
        #=======================================================================
        # :returns: Timestamp - The time at which the market was initialized
        #=======================================================================
        return self.initializeTimestamp


    def bid(self):
        #=======================================================================
        # :returns: Double - The current bid price 
        #=======================================================================
        return self.marketData.bid()
    
    def ask(self):
        #=======================================================================
        # :returns: Double - The current ask price 
        #=======================================================================
        return self.marketData.ask()

    def last(self):
        #=======================================================================
        # :returns: Double - The last price at which a trade has been executed
        #=======================================================================
        return self.marketData.last()

    def high(self):
        #=======================================================================
        # :returns: Double - The 24hr high 
        #=======================================================================
        return self.marketData.high()

    def low(self):
        #=======================================================================
        # :returns: Double - The 24hr low 
        #=======================================================================
        return self.marketData.low()

    def prevDay(self):
        #=======================================================================
        # :returns: Double - The price 24hrs ago
        #=======================================================================
        return self.marketData.prevDay()

    def baseVolume(self):
        #=======================================================================
        # :returns: Double - 24 volume (in bitcoin)
        #=======================================================================
        return self.marketData.baseVolume()



    def totalBalance(self):
        #=======================================================================
        # :returns: Double - Total balance for the market
        #=======================================================================
        return self.marketData.totalBalance()
    
    def availableBalance(self):
        #=======================================================================
        # :returns: Double - Available balance for the market (available to trade, not locked up in trades)
        #=======================================================================
        return self.marketData.availableBalance()
    
    def pendingBalance(self):
        #=======================================================================
        # :returns: Double - Pending balance
        #=======================================================================
        return self.marketData.pendingBalance()
    

    def volumeLastHr(self):
        #=======================================================================
        # :returns: Double - The volume traded over the last hour 
        #=======================================================================
        if self.candles is not None:
            return self.candles.volumeLastHr()
        else:
            return 0.
    
    def avgVolPerHourPreviousDay(self):
        #=======================================================================
        # :return: Double - The average hourly volume traded over the past day  
        #=======================================================================
        if self.candles is not None:
            return self.candles.avgVolPerHourPreviousDay()
        else:
            return 0.

    def lastOpen(self):
        #=======================================================================
        # :return: Double - The open price during the last tickInterval
        #=======================================================================
        if self.candles is not None:
            return self.candles.lastOpen()
        else:
            return 0.

    def lastClose(self):
        #=======================================================================
        # :returns: Double - The close price during the last tickInterval
        # CAVEAT: This is ill defined as the tick interval is still ongoing...
        #=======================================================================
        if self.candles is not None:
            return self.candles.lastClose()
        else:
            return 0.

    def lastHigh(self):
        #=======================================================================
        # :returns: Double - The high price during the last tickInterval
        #=======================================================================
        if self.candles is not None:
            return self.candles.lastHigh()
        else:
            return 0.

    def lastLow(self):
        #=======================================================================
        # :returns: Double - The low price during the last tickInterval
        #=======================================================================
        if self.candles is not None:
            return self.candles.lastLow()
        else:
            return 0.

    def previousDayLastOpen(self):
        #=======================================================================
        # :returns: Double - The open price of the last tick interval during the previous day
        #=======================================================================
        if self.candles is not None:
            return self.candles.previousDayLastOpen()
        else:
            return 0.

    def previousDayLastClose(self):
        #=======================================================================
        # :returns: Double - The close price of the last tick interval during the previous day
        #=======================================================================
        if self.candles is not None:
            return self.candles.previousDayLastClose()
        else:
            return 0.

    def previousDayLastHigh(self):
        #=======================================================================
        # :returns: Double - The high price of the last tick interval during the previous day
        #=======================================================================
        if self.candles is not None:
            return self.candles.previousDayLastHigh()
        else:
            return 0.

    def previousDayLastLow(self):
        #=======================================================================
        # :returns: Double - The low price of the last tick interval during the previous day
        #=======================================================================
        if self.candles is not None:
            return self.candles.previousDayLastLow()
        else:
            return 0.


    #================================================================================================
    #
    # Set of methods that return a list with a time series of the various market metrics for a past
    # period, e.g. previous day or past hour. (The list is ordered as first element is oldest, last
    # element is most recent.) These methods are meant to be used for data analysis as part of a
    # strategy, e.g. by detecting patterns in the last day.
    #
    # The following methods are provided:
    #
    # PREVIOUS DAY:
    # - getAllPreviousDayOpens():       Time series of open prices for all candels during previous day
    # - getAllPreviousDayCloses():      Time series of close prices for all candels during previous day
    # - getAllPreviousDayLows():        Time series of low prices for all candels during previous day
    # - getAllPreviousDayHighs():       Time series of high prices for all candels during previous day
    # - getAllPreviousDayVolumes():     Time series of volumes for all candels during previous day
    # - getAllPreviousDayBaseVolumes(): Time series of open prices for all candels during previous day
    #
    # LAST HOUR:
    # - getAllLastHrOpens():       Time series of open prices for all candels during previous day
    # - getAllLastHrCloses():      Time series of close prices for all candels during previous day
    # - getAllLastHrLows():        Time series of low prices for all candels during previous day
    # - getAllLastHrHighs():       Time series of high prices for all candels during previous day
    # - getAllLastHrVolumes():     Time series of volumes for all candels during previous day
    # - getAllLastHrBaseVolumes(): Time series of open prices for all candels during previous day
    #
    #================================================================================================

    def getAllPreviousDayOpens(self):
        #=======================================================================
        # :returns: List - A list with all the open prices from all the previous day candles
        #=======================================================================
        if self.candles is not None:
            return self.candles.getAllPreviousDayOpens()
        else:
            return [0]

    def getAllPreviousDayCloses(self):
        #=======================================================================
        # :returns: List - A list with all the close prices from all the previous day candles
        #=======================================================================
        if self.candles is not None:
            return self.candles.getAllPreviousDayCloses()
        else:
            return [0]

    def getAllPreviousDayLows(self):
        #=======================================================================
        # :returns: List - A list with all the low prices from all the previous day candles
        #=======================================================================
        if self.candles is not None:
            return self.candles.getAllPreviousDayLows()
        else:
            return [0]

    def getAllPreviousDayHighs(self):
        #=======================================================================
        # :returns: List - A list with all the high prices from all the previous day candles
        #=======================================================================
        if self.candles is not None:
            return self.candels.getAllPreviousDayHighs()
        else:
            return [0]

    def getAllPreviousDayVolumes(self):
        #=======================================================================
        # :returns: List - A list with all the volumes from all the previous day candles
        #=======================================================================
        if self.candels is not None:
            return self.candles.getAllPreviousDayVolumes()
        else:
            return [0]
        
    def getAllPreviousDayBaseVolumes(self):
        #=======================================================================
        # :returns: List - A list with all the base volumes from all the previous day candles
        #=======================================================================
        if self.candles is not None:
            return self.candles.getAllPreviousDayBaseVolumes()
        else:
            return [0]

    def getAllLastHrOpens(self):
        #=======================================================================
        # :returns: List - A list with all the open prices from all the last hour candles
        #=======================================================================
        if self.candles is not None:
            return self.candles.getAllLastHrOpens()
        else:
            return [0]

    def getAllLastHrCloses(self):
        #=======================================================================
        # :returns: List - A list with all the close prices from all the last hour candles
        #=======================================================================
        if self.candles is not None
            return self.candles.getAllLastHrCloses()
        else:
            return [0]

    def getAllLastHrLows(self):
        #=======================================================================
        # :returns: List - A list with all the low prices from all the last hour candles
        #=======================================================================
        if self.candles is not None:
            return self.candles.getAllLastHrLows()
        else:
            return [0]

    def getAllLastHrHighs(self):
        #=======================================================================
        # :returns: List - A list with all the high prices from all the last hour candles
        #=======================================================================
        if self.candles is not None:
            return self.candles.getAllLastHrHighs()
        else:
            return [0]

    def getAllLastHrVolumes(self):
        #=======================================================================
        # :returns: List - A list with all the volumes from all the last hour candles
        #=======================================================================
        if self.candles is not None:
            return self.candles.getAllLastHrVolumes()
        else:
            return [0]

    def getAllLastHourBaseVolume(self):
        #=======================================================================
        # :returns: List - A list with all the base volume from all the previous day candles
        #=======================================================================
        if self.candles is not None:
            return self.candles.getAllLastHourBaseVolume()
        else:
            return [0]
















    def updateCandles(self, api, totalTimeFrame=24, tickInterval=30):
        #=======================================================================
        # Creates candlesticks object if does not exist, or updates current one with newest data
        # 
        # :param data: response from API calls
        #=======================================================================
        # Get current thread ID
        threadID = currentThread().ident
        # Candles have been initialized previously
        if self.candles is not None:
            # API query - Last candle
            lastCandle = api.get_latest_candle(self.abbr, TICKINTERVAL_THIRTYMIN)
            if lastCandle["success"] == True:
                
                #===============================================================
                # print(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + 
                #       ": Market {:>9}".format(self.abbr) + " updating last candle:" +
                #       ", Last High= {:10.8f}".format(lastCandle["result"][0]["H"]) +
                #       ", Last Vol= {:20.8f}".format(lastCandle["result"][0]["V"]) +
                #       ", Timestamp= " + lastCandle["result"][0]["T"])
                #===============================================================

                log.debug("Update for market {:>9}".format(self.abbr) +
                          ", Thread ID: {:>5}".format(str(threadID)) +
                          ", Last candle: " + str(lastCandle["result"]))

                self.candles.updateCandles(lastCandle["result"][0])
            else:
                self.guiNotify("Alert", "Candles update (" + self.abbr + "): API_RESPONSE_MISS")
        # First time updating candles
        else:
            # API query - All candles
            allCandles = api.get_candles(self.abbr, TICKINTERVAL_THIRTYMIN)
            if allCandles["success"] == True:
                log.debug("Update for market {:>9}".format(self.abbr) +
                          ", Thread ID: {:>5}".format(str(threadID)) +
                          ", All Candles: " + str(allCandles['result']))
                
                self.candles = CandleSticks(allCandles["result"], totalTimeFrame, tickInterval)
            else:
                self.guiNotify("Alert", "API_RESPONSE_MISS")
        

    def updateMarketData(self, marketData):
        #=======================================================================
        # Updates the market data (object) for this market
        # 
        # :param data: response from API calls
        #=======================================================================
        if marketData is not None:
            self.marketData.update(marketData)


    def getConfig(self, appConfig):
        #=======================================================================
        # Returns an array with all the trader-general configurations replaced with 
        # the parameters specific to this market set in the config file
        #
        # :returns: (Dictionary[Dictionary]) The config array
        #=======================================================================
        config = {}
        if appConfig["currencies"].get(self.name, False):
            for key, value in appConfig.items():
                if key != "currencies" and key != "strategies":
                    config[key] = value
            for key, value in appConfig["currencies"][self.name].items():
                config[key] = value
        else:
            config = appConfig
        return config



    def checkUpToDate(self):
        #=======================================================================
        # Checks to determine whether market will have currently up-to-date data
        # :returns: (Boolean) Whether Market is currently updated
        #=======================================================================
        return self.isMonitored




     
    def guiNotify(self, msgType, guiMessage):
    #===========================================================================
    # Function to to update the market monitoring status on the GUI
    # Will either display a success or an alert
    # 
    # :guiMessage:    - The type of alert to display
    # 
    # :returns:       - None
    #===========================================================================
        # Success action
        if msgType == "Success":
            Success(guiMessage, self)
    
        # Alert action
        elif msgType == "Alert":
            Alert(guiMessage, self)
        
        #Notify something odd is happening... should not happen
        else:
            Error("Uh-Oh", self)




    def notify(self, noteType, **kwargs):
        """
        Alias for Info(_, market)
        :returns: (Info(Notification))
        """
        return Info(noteType, self, kwargs)

    def success(self, noteType, **kwar):
        """
        Alias for Success(_, market)
        :returns: (Success(Notification))
        """
        return Success(noteType, self)

    def error(self, noteType):
        """
        Alias for Error(_, market)
        :returns: (Error(Notification))
        """
        return Error(noteType, self)

    def alert(self, noteType):
        """
        Alias for Alert(_, market)
        :returns: (Alert(Notification))
        """
        return Alert(noteType, self)



    def printVolumes(self):
        if self.candles is not None:
            log.info("Average hourly volume over previous day: " +
                     str(self.candles.avgVolPerHourPreviousDay()) + "\n" +
                     "Volume over last hour: " + + str(self.candles.volumeLastHr()))
            if self.candles.volumeLastHr() > 10*self.candles.avgVolPerHourPreviousDay():
                self.guiNotify("Alert", "NOTIFY_TRADE_ALERT")

