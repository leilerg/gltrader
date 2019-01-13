from kivy.app import App
from kivy.clock import Clock
import time
from .order import *
from .notification import *
from pprint import pprint as pp
from pip._vendor.packaging import specifiers

from .order_details import *

import logging
log = logging.getLogger(__name__)


class Action(object):
    #===========================================================================
    # Actions are initaited by "strategies" which are executed serially at each tick.  
    # An action must implement a "do" function and set "done" to true within that method. 
    # This will prevent the function from being executed by pressing the same button twice 
    # if actions are not automatically executed.  
    # 
    # An action must also implement the "checkActionComplete" method.  
    # These methods are already implemented for OrderAction and NotifyAction, 
    # so do not need to be implemented if extending those classes unless extended functionality is necessary.
    #===========================================================================
    orders = []
    done = False
    success = False
    complete = False
    notified = False
    disabled = False

    def __init__(self, market=None):
        #=======================================================================
        # Generic action init
        # 
        # :param market: (Market) This should be passed in by the strategy method when it calls the action.  
        # It is currently optional in case actions are extended beyond strategy/market situations
        #=======================================================================
        self.market = market


    def __repr__(self):
        return "<"+self.__class__.__name__+"::action object at "+hex(id(self))+">"

    def __str__(self):
        return self.__class__.__name__

    def __unicode__(self):
        return "<"+self.__class__.__name__+"::action object at "+hex(id(self))+">"

    def checkNotDisabled(self):
        #=======================================================================
        # checks whether action is complete or action is otherwise disabled via class property.
        #
        # :returns: (Boolean) whether action should be disabled
        #=======================================================================
        complete = self.checkActionComplete()
        if self.disabled:
            Alert("action "+self.__class__.__name__+" disabled", self)
        return complete and not self.disabled

    def checkActionComplete(self):
        #===========================================================================
        # Checks whether action is complete. Stub method here should be implemented according to needs
        # for subclasses.  Optionally, self.success can be defined as well.  
        #
        # :returns: (Boolean) whether action has completed.
        #===========================================================================
        return self.complete

class OrderAction(Action):

    def checkActionComplete(self):
        #===========================================================================
        # iterates over a list of Orders stored in self.orders to check if they are all completed
        # successfully 
        #
        # :returns: (Boolean) whether all orders have completed.
        #===========================================================================
        if not self.complete:
            for order in self.orders:
                if not order.isCompleted:
                    if not order.checkOrderComplete():
                        # Info("order not complete", self.market)
                        return False
                else:
                    if not order.success:
                        self.success = False
                        self.complete = True
                        return False
            self.complete = True
            self.success = True
            return True
        return True





class MarketBuyLimitSellTrade(OrderAction):
    #===========================================================================
    # Trade action used to exploit a pump and dump attempt
    # 
    # It places a market buy order and a higher limit sell order.
    # The trade amount and the limit order price multiplier are specified in the config file   
    #===========================================================================

    def __init__(self, market, marketBuyDetails, expRet, tradeAPI):
        #=======================================================================
        # Initialize the action
        # 
        # Input:
        # :market:           - (Market object) For the market to trade
        # :marketBuyDetails: - (BittrexOrderDetails object) With the details for the market buy
        # :expRet:           - (Double) The expected return on the trade - The limit sell is placed
        #                      according to this return rate, and the market buy rate
        # :tradeAPI:         - (TradeAPI object) The API to trade with (could be fake API for tests) 
        # 
        #=======================================================================
        super().__init__(market)
        self._marketBuyDetails = marketBuyDetails
        self._expRet = expRet
        self._tradeAPI = tradeAPI
        

    def do(self):
        #=======================================================================
        # Creates 1 market order and appends it to self.orders; 
        # then uses the return values to create a 2nd order and append it as well.
        # 
        # :returns: (Order, Order) A 2-tuple of the orders created on execution
        #=======================================================================

        # Create market buy order
        buyMarket = MarketBuy(self.market,
                              self._marketBuyDetails,
                              self._tradeAPI)
        # Append first order for output
        self.orders.append(buyMarket)

        # Execute order
        didBuyMarket = buyMarket.execTrade()
        # If trade successfull, 
        if didBuyMarket:
            # # log some details,
            # log.info("Trade executed!!\n" +
            #          "Order ID: " + str(buyMarket.orderID) + "\n" +
            #          "Quantity bought: " + str(buyMarket.qty) + "\n" +
            #          "Rate paid: " + str(buyMarket.rate))
            # and execute next one, limit sell

            # Construct limit sell order details
            sellLimitDetailsDict = {"marketName"    : buyMarket.marketName(),
                                    "quantity"      : buyMarket.tradeQty(),
                                    "rate"          : buyMarket.tradeRate() * (1 + self._expRet),
                                    "orderType"     : "LIMIT",
                                    "timeInEffect"  : buyMarket.timeInEffect(),
                                    "conditionType" : buyMarket.conditionType(),
                                    "target"        : 0.}

            # Construct the details object
            sellLimitDetails = BittrexOrderDetails(sellLimitDetailsDict)

            # Construct the limit sell order
            sellLimit = LimitSell(self.market,
                                  sellLimitDetails,
                                  self._tradeAPI)

            # And append
            self.orders.append(sellLimit)
            # Execute second trade
            didLimitSell = sellLimit.execTrade()
            # Check if all good, and log if any problems...
            self.success = True
            if not didLimitSell:
                Error("PumpAndDumpExploitTrade error: Limit sell failed")
                log.critical("Warning: action.PumpAndDumpExploitTrade() Limit Sell failed")
                self.success = False
                return False
        else: 
            Error("PumpAndDumpExploitTrade error: Market buy failed")
            log.critical("Warning: action.PumpAndDumpExploitTrade() Market Buy failed")
            self.success = False

        self.done = True

        return self.orders           
            
    

class MinTradeUp(OrderAction):
    #===========================================================================
    # MinTradeUp requires a total trade amount of 2.2x the minimum trade value defined in the config
    # file.   
    # It places a minimum market trade and a limit sell at 1.2 times the rate.
    #===========================================================================
    def do(self):
        #=======================================================================
        # Creates 1 market order and appends it to self.orders, then uses the return values to
        # create a 2nd order and append it as well. 
        # 
        # :returns: (Order, Order) A 2-tuple of the orders created on execution
        #=======================================================================
        self.done = True
        rate = 1.2*float(self.market.data.summary["Ask"])
        order1 = LimitBuy(self.market, self.market.config["trade_amount"], rate)
        self.orders.append(order1)

        if order1.parseAmount(float(self.market.config["trade_amount"])*2.2):
            if order1.execTrade():
                log.info("Trade details:\n" +
                         "Tentative amount: " +
                         order1.parseAmount(float(self.market.config["trade_amount"])*2.2) + "\n" +
                         "Rate: " + order1.rate + "\n" +
                         "Quantity: " + order1.qty + "\n" +
                         "OrderID: " + order1.orderID + "\n" +
                         "Amount: " + order1.amount)
                order2 = LimitSell(self.market, None, rate, order1.qty)
                self.orders.append(order2)
                if not order2.execTrade():
                    Error("MinTradeUp second buy failed")
                    self.success = False
                    return False
                self.success = True
            else:
                Error("MinTradeUp first buy failed")
                self.success = False
        else:
            self.success = False
            Alert("Trade Up order Too large")
        return self.orders





class SingleOrderAction(OrderAction):
    """
    Stub class no longer needed, but may be useful later
    """
    pass





# class MaxTradeUp(OrderAction):
#     """
#     MaxTradeUp requires a total trade amount of 2.2x the maximum trade value defined in the config
#     file.  It places a maximum market trade and a limit sell at 1.2 times the rate. 
#     """
#     def do(self):
#         """
#         Creates 1 market order and appends it to self.orders, then uses the return values to
#     create a 2nd order and append it as well. 
#
#         :returns: (Order, Order) A 2-tuple of the orders created on execution
#         """
#         rate = 1.2*float(self.market.data.summary["Ask"])
#         order1 = LimitBuy(self.market, self.market.config["max_trade_amount"], rate)
#         self.orders.append(order1)
#         if order1.execTrade():
#             order2 = LimitSell(self.market, order1.qty, rate)
#             self.orders.append(order2)
#             if not order1.execTrade():
#                 Error("MinTradeUp second order failed")
#                 self.done = True
#                 self.success = False
#                 return False
#         else:
#             Error("MinTradeUp first buy failed")
#             self.done = True
#             self.success = False
#             return False
#         return (order1, order2)


class NotifyAction(Action):
    """
    Creates an Info Notification as a response to a strategy
    """
    def __init__(self, message="Default Message", market=None):
        self.market = market
        self.message = message

    def do(self):
        """
        :returns: ( Info(Notification) ) Message to be displayed if strategy executed
        """
        self.done = True
        msg =  Info(self.message, self.market)
        self.complete = True
        return msg


class SendSuccess(NotifyAction):
    """
    Creates an Success Notification as a response to a strategy
    """

    def do(self):
        """
        :returns: ( Success(Notification) ) Message to be displayed if strategy executed
        """
        self.done = True
        msg = Success(self.message, self.market)
        self.complete = True
        self.success = True
        return msg
