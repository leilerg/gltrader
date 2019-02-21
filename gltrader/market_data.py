
import os
import sys
from datetime import datetime
from kivy.app import App

import gltrader.bittrex
from gltrader.notification import *
from pprint import pprint as pp

from .candlesticks import CandleSticks

import builtins


class MarketData(object):
    #===========================================================================
    # This class is where the data about prices, etc is stored.  
    # 
    # Each tick calls "update" and sends an array of data to this object per market, 
    #===========================================================================
    

    # def __init__(self, market, data):
    def __init__(self, marketSummaryData):
        #=======================================================================
        # Accepts the market which created it
        # :param market: (Market) -- the market which is associated with this object
        #=======================================================================

        self.balanceSummary = marketSummaryData["Balance"]
        self.currencySummary = marketSummaryData["Currency"]
        self.bitcoinMarketSummary = marketSummaryData["BitcoinMarket"]

        #=======================================================================
        # #Will introduce a Candlesticks object here
        # self.candles = {}
        # self.latest = {}
        #=======================================================================


    def bid(self):
        return self.bitcoinMarketSummary["Bid"]
    
    def ask(self):
        return self.bitcoinMarketSummary["Ask"]

    def last(self):
        return self.bitcoinMarketSummary["Last"]

    def previousDayHigh(self):
        return self.bitcoinMarketSummary["High"]

    def previousDayLow(self):
        return self.bitcoinMarketSummary["Low"]

    def previousDayPrice(self):
        return self.bitcoinMarketSummary["PrevDay"]

    def previousDayBaseVol(self):
        return self.bitcoinMarketSummary["BaseVolume"]
        
    def totalBalance(self):
        #=======================================================================
        # :returns: Double - The total balance of a given coin
        #=======================================================================
        return self.balanceSummary["Balance"]
    
    def availableBalance(self):
        #=======================================================================
        # :returns: Double - The balance of a coin, availalbe for trade
        #=======================================================================
        return self.balanceSummary["Available"]
    
    def pendingBalance(self):
        #=======================================================================
        # :returns: Double - The deposit pending balance of a coin
        #=======================================================================
        return self.balanceSummary["Pending"]

    def reservedBalance(self):
        #=======================================================================
        # :returns: Double - The balance reserved for an open order
        #=======================================================================
        return self.totalBalance() - self.availableBalance()
    

    def update(self, data):
        #=======================================================================
        #
        # Accepts the array of data passed by the trader at each tick
        # No checks are performed on the input data, it assumes the data is OK!!
        #
        # :returns: void
        #
        #=======================================================================
        self.balanceSummary = data["Balance"]
        self.currencySummary = data["Currency"]
        self.bitcoinMarketSummary = data["BitcoinMarket"]




