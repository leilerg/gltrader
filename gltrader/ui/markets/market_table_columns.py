from kivy.metrics import dp, sp, cm

from .market_string_label import MarketStringLabel
from .market_percent_label import MarketPercentLabel
from .market_number_label import *


from kivy.uix.label import Label

from ..buttons import SingleMarketButton, StartButton

class MarketTableColumns(object):
    #===========================================================================
    # Creates a dictionary of getter methods that can be used to generate labels
    #===========================================================================
    widgets={}

    def __init__(self, market=None):
        ":param market: (Market) the market passed in from the MarketRow object"
        self.market = market
        self.widgets = self.setWidgets()

    def setWidgets(self):
        #=======================================================================
        # creates dict set to self.widgets
        # 
        # :returns: (Dict[Widget]) - A dictionary of wigets generated by other methods in object
        #=======================================================================
        return {
            # "Name" : self.getNameWidget() if self.market is not None else None,
            "Bid" : self.getBidWidget() if self.market is not None else None,
            "Ask" : self.getAskWidget() if self.market is not None else None,
            "24hr Volume" : self.get24VolWidget() if self.market is not None else None,
            "24hr AvgVol" : self.get24AvgVolWidget() if self.market is not None else None,
            "Last Hr Vol" : self.getLastHrVolWidget() if self.market is not None else None,
            "Vol Ratio" : self.getVolRatioWidget() if self.market is not None else None,
            "Monitor" : self.getMonitorWidget() if self.market is not None else None,
        }

    def getWidgets(self):
        #=======================================================================
        # :returns: (Dict[Widget]) - A dictionary of wigets generated by method setWidgets
        #=======================================================================
        return self.widgets

    def getLabels(self):
        #=======================================================================
        # :returns: (Dict[Widget]) - A dictionary of wigets to be used as column labels in top row
        #=======================================================================
        return {labeltext : Label(text=labeltext) for labeltext in self.widgets}


    def getNameWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the market name widget
        #=======================================================================
        def getName():
            return self.market.name
        return MarketStringLabel(getName)

    def getBidWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the latest Bid widget
        #=======================================================================
        def getBid():
            # print("Market: " + self.market.name + ", Bid = {:10.8f}".format(self.market.bid()))
            return self.market.bid()
        return MarketPriceLabel(getBid, font_size=sp(12), size_hint_x = None, width = 500)

    def getAskWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the latest Ask widget
        #=======================================================================
        def getAsk():
            return self.market.ask()
        return MarketPriceLabel(getAsk, font_size=sp(12), size_hint_x = None, width = 500)


    def get24AvgVolWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the latest hourly average volume, over 24hrs 
        #=======================================================================
        def get24AvgVol():
            return self.market.avgVolPerHourPreviousDay()
        return MarketVolumeLabel(get24AvgVol, font_size=sp(12), padding_x = 30)

    def getLastHrVolWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the volume in the last hour 
        #=======================================================================
        def getLastHrVol():
            return self.market.volumeLastHr()
        return MarketVolumeLabel(getLastHrVol, font_size=sp(12))

    def getVolRatioWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the volume in the last hour 
        #=======================================================================
        def getVolRatio():
            return self.market.volumeLastHr()/self.market.avgVolPerHourPreviousDay()
        return GenericNumberLabel(getVolRatio, font_size=sp(12))




    def get24VolWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the latest base volume widget
        #=======================================================================
        def get24Vol():
            return self.market.previousDayBaseVol()
        return GenericNumberLabel(get24Vol , font_size=sp(12))

    def get24ChangeWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the latest 24 hr volume widget
        #=======================================================================
        def get24Change():
            # yest = self.market.data.summary["PrevDay"]
            # now = self.market.data.summary["Last"]
            yest = self.market.prevDay()
            now = self.market.last()
            change = (now-yest)*100/yest
            return change
        return MarketPercentLabel(get24Change, font_size=sp(12))

    def getAvailWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the latest available balance widget
        #=======================================================================
        def getAvail():
            # return self.market.data.balance["Available"]
            return self.market.availableBalance()
        return MarketPriceLabel(getAvail , font_size=sp(12))

    def getPendingWidget(self):
        #=======================================================================
        # A getter is defined and used to create a refreshable widget
        # 
        # :returns: (Widget) a getter for the latest pending balance widget
        #=======================================================================
        def getPending():
            return self.market.pendingBalance()
        return MarketPriceLabel(getPending , font_size=sp(12))

    def getMonitorWidget(self):
        #=======================================================================
        # :returns: (Button(Widget)) A button to either view the market or 
        #                            Start monitoring the market (if show_all is selected in config)
        #=======================================================================
        if self.market.isMonitored:
            return SingleMarketButton(self.market, size_hint_x=None, width=75)
        else:
            return StartButton(self.market)
