"""
This lists a raw balances response from the API
"""

import threading

from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty, DictProperty
from kivy.metrics import dp, sp
from kivy.app import App
from functools import partial
from kivy.core.window import Window


from .market_table_header import MarketTableHeader
from .market_row import MarketRow

from pprint import pprint as pp


class MarketTable(GridLayout):
    #===========================================================================
    # The primary GUI layout for the market table which contains the rows for each market.  
    # Contains dict marketWidgets, which is used to refresh values
    #===========================================================================
    height=NumericProperty(dp(50))
    marketWidgets=DictProperty(None)

    def __init__(self, **kwargs):
        #=======================================================================
        # Binds object values to methods to be called when updated, adds refresh 
        # to app.rootWidget.refreshers so it will be called each tick
        #=======================================================================
        self.bind(minimum_height=self.setter("height"))
        self.bind(height=self.setter("height"))
        super(MarketTable, self).__init__(**kwargs)
        #self.bind(marketWidgets=self.refresh)
        self.app=App.get_running_app()
        #print("\n----------- Start __init__ MarketTable ----------")
        self.refresh()
        # Append refresher!
        self.app.rootWidget.refreshers.append(self.refresh)
        #print("\n----------- End   __init__ MarketTable ----------")


    def refresh(self, object=None, value=None):
        #=======================================================================
        # called when marketWidgets changes value to update table
        # 
        # :param object: instance of current object
        # :param value: new value of marketWidgets
        #=======================================================================
        #print("--------- Start MarketTable.refresh() ---------")
        #print("Before updateWidgets(): " + str(len(self.marketWidgets)))
        self.updateWidgets()
        #print("After  updateWidgets(): " + str(len(self.marketWidgets)))
        self.showMarkets()
        #print("--------- End   MarketTable.refresh() ---------")

    # def removeMarket(self, market):
    def removeMarket(self, marketName):
        #=======================================================================
        # Removes a given market from the table --- called when market.isMonitored is set to false
        # :param market: (marketName) market to be removed from table
        #=======================================================================
        if self.marketWidgets.get(marketName, False):
            # Delete refresher from global refreshers lists
            self.marketWidgets[marketName].delRefresher()
            # Remove the widget
            self.remove_widget(self.marketWidgets[marketName])
            del(self.marketWidgets[marketName])

    def addMarket(self, market):
        #=======================================================================
        # Adds a given market to the table --- called when market.isMonitored is set to true
        # :param market: (Market) market to be added to table
        #=======================================================================
        if not self.marketWidgets.get(market.name, False):
            self.marketWidgets[market.name] = MarketRow(market)
            self.add_widget(self.marketWidgets[market.name])
        # self.add_widget(self.marketWidgets[name])
        self.marketWidgets[market.name].refresh()



    def updateWidgets(self):
        #=======================================================================
        # Updates all the widgets that need to be refreshed
        # Will add new markets and remove stale ones
        #=======================================================================
        #pp("---- Start MarketTable.updateWidgets() ----")
        # Add fresh market widgets
        for name, market in self.app.trader.markets.items():
            if name not in self.marketWidgets:
                self.addMarket(market)
 
        # Identify stale market widgets
        staleMarkets = []
        for name in self.marketWidgets:
            if name not in self.app.trader.markets:
                staleMarkets.append(name)

        # Remove stale markets
        for staleMarket in staleMarkets:
                self.removeMarket(staleMarket)
        
        # Action log
        #pp("---- End   MarketTable.updateWidgets() ----")
    
    


    def showMarkets(self):
        #=======================================================================
        # Creates market rows or refreshes them (in separate threads).
        #=======================================================================
        
        
        # Update dictionary of widgets to refresh
        
        #=======================================================================
        # # Add fresh market widgets
        # for name, market in self.app.trader.markets.items():
        #     if name not in self.marketWidgets:
        #         self.addMarket(market)
        #         
        # # Remove stale market widgets
        # for name in self.marketWidgets:
        #     if name not in self.app.trader.markets:
        #         self.removeMarket(name)
        #=======================================================================
 
        # pp("------- Start MarketTable.showMarkets() -------")
        # Have all required market widgets - Update
        threads = []
        for name in self.marketWidgets:
            t = threading.Thread(target=self.marketWidgets[name].refresh)
            threads.append(t)
            t.start()
         
        # And joint threads back up
        for t in threads:
            t.join()
        # pp("------- End   MarketTable.showMarkets() -------")
                
        
        self.setter("height")
